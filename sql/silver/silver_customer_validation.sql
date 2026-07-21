-- This script is for silver.customers table validation

WITH validation_checks AS (
    SELECT
        -- 1. Total Row Count
        COUNT(*) AS total_records,

        -- 2. Null Value Checks (Crucial for IDs and tracking columns)
        COUNT(CASE WHEN customer_id IS NULL THEN 1 END) AS null_customer_id_count,
        COUNT(CASE WHEN customer_unique_id IS NULL THEN 1 END) AS null_customer_unique_id_count,
        COUNT(CASE WHEN customer_zip_code_prefix IS NULL THEN 1 END) AS null_zip_prefix_count,
        COUNT(CASE WHEN create_date IS NULL THEN 1 END) AS null_create_date_count,

        -- 3. String Format & Empty String Checks
        COUNT(CASE WHEN TRIM(customer_id) = '' THEN 1 END) AS empty_customer_id_count,
        COUNT(CASE WHEN LENGTH(customer_state) <> 2 THEN 1 END) AS invalid_state_length_count, -- Assumes 2-letter state codes (e.g., NY, CA)

        -- 4. Numeric Bounds Check (Zip codes shouldn't be negative or zero)
        COUNT(CASE WHEN customer_zip_code_prefix <= 0 THEN 1 END) AS invalid_zip_range_count,

        -- 5. Business Logic / Date Integrity Checks
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS future_update_date_count,
        COUNT(CASE WHEN create_date > NOW() THEN 1 END) AS future_create_date_count,

        -- 6. Metadata Verification
        COUNT(CASE WHEN source_system IS NULL OR TRIM(source_system) = '' THEN 1 END) AS missing_source_system_count
    FROM silver.customers
),
duplicate_checks AS (
    -- 7. Uniqueness Check (Checks if customer_id has duplicates)
    SELECT COUNT(*) AS duplicate_customer_id_count
    FROM (
        SELECT customer_id 
        FROM silver.customers 
        GROUP BY customer_id 
        HAVING COUNT(*) > 1
    ) sub
)
SELECT 
    v.total_records,
    v.null_customer_id_count,
    v.empty_customer_id_count,
    d.duplicate_customer_id_count,
    v.null_customer_unique_id_count,
    v.null_zip_prefix_count,
    v.invalid_zip_range_count,
    v.invalid_state_length_count,
    v.null_create_date_count,
    v.future_update_date_count,
    v.future_create_date_count,
    v.missing_source_system_count,
    -- Simple Status Flag
    CASE 
        WHEN (v.null_customer_id_count + v.empty_customer_id_count + d.duplicate_customer_id_count + v.invalid_zip_range_count + v.future_update_date_count) = 0 
        THEN 'PASSED' 
        ELSE 'FAILED' 
    END AS validation_status
FROM validation_checks v, duplicate_checks d;

-- ================================================================================================================================================================
-- 1. Null Customer ID Check
-- Identifies records missing the primary identifier.
SELECT customer_unique_id, customer_id
FROM silver.customers
WHERE customer_id IS NULL;

-- 2. Empty Customer ID Check
-- Identifies records where the ID is just empty spaces.
SELECT customer_id
FROM silver.customers
WHERE TRIM(customer_id) = '';

-- 3. Duplicate Customer ID Check
-- Identifies IDs that appear more than once in the dataset.
SELECT customer_id, COUNT(*) AS occurrence_count
FROM silver.customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 4. Null Unique Customer ID Check
-- Identifies records missing the secondary unique identifier.
SELECT customer_id, customer_unique_id
FROM silver.customers
WHERE customer_unique_id IS NULL;

-- 5. Null Zip Code Prefix Check
-- Identifies records with missing postal/zip prefix data.
SELECT customer_id, customer_zip_code_prefix
FROM silver.customers
WHERE customer_zip_code_prefix IS NULL;

-- 6. Invalid Zip Code Range Check
-- Identifies zip codes that are zero or negative (invalid bounds).
SELECT customer_id, customer_zip_code_prefix
FROM silver.customers
WHERE customer_zip_code_prefix <= 0;

-- 7. Invalid State Length Check
-- Identifies state codes that do not conform to the standard 2-letter format.
SELECT customer_id, customer_state
FROM silver.customers
WHERE LENGTH(customer_state) <> 2;

-- 8. Null Create Date Check
-- Identifies records missing their creation timestamp.
SELECT customer_id, create_date
FROM silver.customers
WHERE create_date IS NULL;

-- 9. Out-of-Sequence Update Date Check
-- Identifies logical errors where a record claims to have been updated before it was created.
SELECT customer_id, create_date, update_date
FROM silver.customers
WHERE update_date < create_date;

-- 10. Future Create Date Check
-- Identifies records with creation dates set in the future.
SELECT customer_id, create_date
FROM silver.customers
WHERE create_date > NOW();

-- 11. Missing Source System Check
-- Identifies records where the metadata origin is either missing or blank.
SELECT customer_id, source_system
FROM silver.customers
WHERE source_system IS NULL OR TRIM(source_system) = '';
