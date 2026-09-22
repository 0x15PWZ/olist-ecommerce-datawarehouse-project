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

--================================================================================

-- 1. Missing Review ID Check
-- Identifies records where the primary review_id is either missing or empty.
SELECT order_id, review_id
FROM silver.order_reviews
WHERE review_id IS NULL OR TRIM(review_id) = '';

-- 2. Duplicate Review ID Check
-- Identifies instances where a review_id is duplicated, indicating potential data replication issues.
SELECT review_id
FROM silver.order_reviews
WHERE review_id IS NOT NULL
GROUP BY review_id
HAVING COUNT(*) > 1;

-- 3. Missing Order ID Check
-- Identifies orphan reviews that do not link back to an existing order.
SELECT review_id, order_id
FROM silver.order_reviews
WHERE order_id IS NULL OR TRIM(order_id) = '';

-- 4. Invalid Review Score Check
-- Identifies score violations outside the standard 1 to 5 star rating boundary.
SELECT review_id, review_score
FROM silver.order_reviews
WHERE review_score IS NULL OR review_score < 1 OR review_score > 5;

-- 5. Whitespace-Only Title Check
-- Flags records where the comment title property exists but contains only blank spaces.

SELECT review_id, review_comment_title
FROM silver.order_reviews
WHERE review_comment_title IS NOT NULL AND TRIM(review_comment_title) = '';

-- 6. Whitespace-Only Message Check
--Flags records where the comment message property exists but contains only blank spaces.

SELECT review_id, review_comment_message
FROM silver.order_reviews
WHERE review_comment_message IS NOT NULL AND TRIM(review_comment_message) = '';

-- 7. Missing Review Creation Date Check
--Identifies records missing the mandatory date tracking when the review was written.
SELECT review_id, review_creation_date
FROM silver.order_reviews
WHERE review_creation_date IS NULL;
-- 8. Out-of-Sequence Answer Timestamp Check
-- Identifies timeline errors where a customer service agent replied before the review was officially created.

SELECT review_id, review_creation_date, review_answer_timestamp
FROM silver.order_reviews
WHERE review_answer_timestamp::date < review_creation_date;

-- 9. System Audit Date Mismatch Check
-- Identifies data integration issues where a record updates before its primary creation timestamp.
SELECT review_id, create_date, update_date
FROM silver.order_reviews
WHERE update_date < create_date;