WITH validation_checks AS (
    SELECT
        -- 1. Total Rows Scanned
        COUNT(*) AS total_records,

        -- 2. Mandatory Core Fields (Neither side of a translation matrix should be null or blank)
        COUNT(CASE WHEN product_category_name IS NULL OR TRIM(product_category_name) = '' THEN 1 END) AS missing_original_name_count,
        COUNT(CASE WHEN product_category_name_english IS NULL OR TRIM(product_category_name_english) = '' THEN 1 END) AS missing_english_translation_count,

        -- 3. Circular or Redundant Translation Check
        -- Flags cases where the original name is identical to the English name. 
        -- (Note: This is a soft flag; some words are identical across languages, but worth auditing)
        COUNT(CASE WHEN LOWER(TRIM(product_category_name)) = LOWER(TRIM(product_category_name_english)) THEN 1 END) AS identical_translation_count,

        -- 4. System Metadata Audit Log Rules
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count,
        COUNT(CASE WHEN source_system IS NULL OR TRIM(source_system) = '' THEN 1 END) AS missing_source_system_count
    FROM silver.product_category_name_translation
),
duplicate_checks AS (
    -- 5. Primary Key Uniqueness Check (Original Category Name)
    SELECT COUNT(*) AS duplicate_original_name_pk_count
    FROM (
        SELECT product_category_name
        FROM silver.product_category_name_translation
        WHERE product_category_name IS NOT NULL
        GROUP BY product_category_name
        HAVING COUNT(*) > 1
    ) sub
),
mapping_anomaly_checks AS (
    -- 6. Many-to-One / Inverse Uniqueness Check
    -- Ensures that multiple original categories are not mapping to the exact same English category, 
    -- which would cause issues when aggregating data by English names downstream.
    SELECT COUNT(*) AS duplicate_english_mapping_count
    FROM (
        SELECT product_category_name_english
        FROM silver.product_category_name_translation
        WHERE product_category_name_english IS NOT NULL
        GROUP BY product_category_name_english
        HAVING COUNT(*) > 1
    ) sub
)
SELECT 
    v.total_records,
    v.missing_original_name_count,
    v.missing_english_translation_count,
    d.duplicate_original_name_pk_count,
    m.duplicate_english_mapping_count,
    v.identical_translation_count,
    v.system_date_mismatch_count,
    v.missing_source_system_count,
    -- Summary Evaluation Status
    CASE 
        WHEN (
            v.missing_original_name_count + 
            v.missing_english_translation_count + 
            d.duplicate_original_name_pk_count + 
            m.duplicate_english_mapping_count + 
            v.system_date_mismatch_count +
            v.missing_source_system_count
        ) = 0 THEN 'PASSED'
        ELSE 'FAILED'
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d, mapping_anomaly_checks m;