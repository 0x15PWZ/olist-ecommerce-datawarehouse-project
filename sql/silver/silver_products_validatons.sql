WITH validation_checks AS (
    SELECT
        -- 1. Total Rows Scanned
        COUNT(*) AS total_records,

        -- 2. Mandatory Core Fields
        COUNT(CASE WHEN product_id IS NULL OR TRIM(product_id) = '' THEN 1 END) AS missing_product_id_count,

        -- 3. Categorization & Metadata Rules
        COUNT(CASE WHEN product_category_name IS NOT NULL AND TRIM(product_category_name) = '' THEN 1 END) AS whitespace_only_category_count,

        -- 4. Text Length Alignment Rules
        -- Flags cases where the stored length integer doesn't match the actual length of the target data, if available downstream
        COUNT(CASE WHEN product_name_length < 0 THEN 1 END) AS negative_name_length_count,
        COUNT(CASE WHEN product_description_length < 0 THEN 1 END) AS negative_description_length_count,

        -- 5. Media Asset Rules
        COUNT(CASE WHEN product_photos_qty < 0 THEN 1 END) AS negative_photos_qty_count,

        -- 6. Physical Dimensions & Weight Business Rules
        -- Physical items cannot weigh zero or have zero dimensions unless they are purely digital services
        COUNT(CASE WHEN product_weight_g IS NOT NULL AND product_weight_g <= 0 THEN 1 END) AS invalid_weight_count,
        COUNT(CASE WHEN product_length_cm IS NOT NULL AND product_length_cm <= 0 THEN 1 END) AS invalid_length_count,
        COUNT(CASE WHEN product_height_cm IS NOT NULL AND product_height_cm <= 0 THEN 1 END) AS invalid_height_count,
        COUNT(CASE WHEN product_width_cm IS NOT NULL AND product_width_cm <= 0 THEN 1 END) AS invalid_width_count,

        -- 7. System Date Ingestion Check
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count
    FROM silver.products
),
duplicate_checks AS (
    -- 8. Primary Key Uniqueness Check
    SELECT COUNT(*) AS duplicate_product_id_count
    FROM (
        SELECT product_id
        FROM silver.products
        WHERE product_id IS NOT NULL
        GROUP BY product_id
        HAVING COUNT(*) > 1
    ) sub
)
SELECT 
    v.total_records,
    v.missing_product_id_count,
    d.duplicate_product_id_count,
    v.whitespace_only_category_count,
    v.negative_name_length_count,
    v.negative_description_length_count,
    v.negative_photos_qty_count,
    v.invalid_weight_g_count,
    v.invalid_length_cm_count,
    v.invalid_height_cm_count,
    v.invalid_width_cm_count,
    v.system_date_mismatch_count,
    -- Summary Evaluation Status
    CASE 
        WHEN (
            v.missing_product_id_count + 
            d.duplicate_product_id_count + 
            v.whitespace_only_category_count + 
            v.negative_name_length_count + 
            v.negative_description_length_count + 
            v.negative_photos_qty_count + 
            v.invalid_weight_g_count + 
            v.invalid_length_cm_count + 
            v.invalid_height_cm_count + 
            v.invalid_width_cm_count + 
            v.system_date_mismatch_count
        ) = 0 THEN 'PASSED'
        ELSE 'FAILED'
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d; 