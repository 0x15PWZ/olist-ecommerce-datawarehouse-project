WITH validation_checks AS (
    SELECT
        -- 1. Total Rows Scanned
        COUNT(*) AS total_records,

        -- 2. Mandatory Core Fields
        COUNT(CASE WHEN review_id IS NULL OR TRIM(review_id) = '' THEN 1 END) AS missing_review_id_count,
        COUNT(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 END) AS missing_order_id_count,

        -- 3. Review Score Bounds Rule (e.g., standard 1 to 5 star rating system)
        COUNT(CASE WHEN review_score IS NULL OR review_score < 1 OR review_score > 5 THEN 1 END) AS invalid_review_score_count,

        -- 4. Text Content Integrity
        -- Flags records where text fields contain only whitespace characters
        COUNT(CASE WHEN review_comment_title IS NOT NULL AND TRIM(review_comment_title) = '' THEN 1 END) AS whitespace_only_title_count,
        COUNT(CASE WHEN review_comment_message IS NOT NULL AND TRIM(review_comment_message) = '' THEN 1 END) AS whitespace_only_message_count,

        -- 5. Chronological Business Rules
        COUNT(CASE WHEN review_creation_date IS NULL THEN 1 END) AS missing_review_creation_date_count,
        -- The customer service reply (answer) cannot happen before the review is actually created
        COUNT(CASE WHEN review_answer_timestamp::date < review_creation_date THEN 1 END) AS answer_before_creation_count,

        -- 6. System Logging Rules
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count
    FROM silver.order_reviews
),
duplicate_checks AS (
    -- 7. Uniqueness Check
    -- Depending on business rules, a review_id should be unique. 
    SELECT COUNT(*) AS duplicate_review_id_count
    FROM (
        SELECT review_id
        FROM silver.order_reviews
        WHERE review_id IS NOT NULL
        GROUP BY review_id
        HAVING COUNT(*) > 1
    ) sub
)
SELECT 
    v.total_records,
    v.missing_review_id_count,
    d.duplicate_review_id_count,
    v.missing_order_id_count,
    v.invalid_review_score_count,
    v.whitespace_only_title_count,
    v.whitespace_only_message_count,
    v.missing_review_creation_date_count,
    v.answer_before_creation_count,
    v.system_date_mismatch_count,
    -- Summary Evaluation Status (Fails if any data quality metrics are broken)
    CASE 
        WHEN (
            v.missing_review_id_count + 
            d.duplicate_review_id_count + 
            v.missing_order_id_count + 
            v.invalid_review_score_count + 
            v.whitespace_only_title_count + 
            v.whitespace_only_message_count + 
            v.missing_review_creation_date_count + 
            v.answer_before_creation_count + 
            v.system_date_mismatch_count
        ) = 0 THEN 'PASSED'
        ELSE 'FAILED'
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d;