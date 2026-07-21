WITH validation_checks AS (
    SELECT
        -- 1. Total Rows Scanned
        COUNT(*) AS total_records,

        -- 2. Mandatory Core Fields
        COUNT(CASE WHEN seller_id IS NULL OR TRIM(seller_id) = '' THEN 1 END) AS missing_seller_id_count,

        -- 3. Geographic Integrity Rules
        -- Zip code prefixes must be positive integers
        COUNT(CASE WHEN seller_zip_code_prefix IS NULL OR seller_zip_code_prefix <= 0 THEN 1 END) AS invalid_zip_prefix_count,
        -- City names should not be empty or contain only spaces
        COUNT(CASE WHEN seller_city IS NULL OR TRIM(seller_city) = '' THEN 1 END) AS missing_city_count,
        -- State codes should match a standard format length (e.g., exactly 2 characters like SP, RJ, NY)
        COUNT(CASE WHEN seller_state IS NULL OR LENGTH(TRIM(seller_state)) <> 2 THEN 1 END) AS invalid_state_code_count,

        -- 4. Audit & System Date Rules
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count,
        COUNT(CASE WHEN source_system IS NULL OR TRIM(source_system) = '' THEN 1 END) AS missing_source_system_count
    FROM silver.sellers
),
duplicate_checks AS (
    -- 5. Primary Key Uniqueness Check
    SELECT COUNT(*) AS duplicate_seller_id_count
    FROM (
        SELECT seller_id
        FROM silver.sellers
        WHERE seller_id IS NOT NULL
        GROUP BY seller_id
        HAVING COUNT(*) > 1
    ) sub
)
SELECT 
    v.total_records,
    v.missing_seller_id_count,
    d.duplicate_seller_id_count,
    v.invalid_zip_prefix_count,
    v.missing_city_count,
    v.invalid_state_code_count,
    v.system_date_mismatch_count,
    v.missing_source_system_count,
    -- Summary Evaluation Status
    CASE 
        WHEN (
            v.missing_seller_id_count + 
            d.duplicate_seller_id_count + 
            v.invalid_zip_prefix_count + 
            v.missing_city_count + 
            v.invalid_state_code_count + 
            v.system_date_mismatch_count +
            v.missing_source_system_count
        ) = 0 THEN 'PASSED'
        ELSE 'FAILED'
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d;