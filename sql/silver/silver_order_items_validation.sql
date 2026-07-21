WITH validation_checks AS (
    SELECT
        -- 1. Total Rows Scanned
        COUNT(*) AS total_records,

        -- 2. Mandatory Core Fields
        COUNT(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 END) AS missing_order_id_count,
        COUNT(CASE WHEN order_item_id IS NULL THEN 1 END) AS null_order_item_id_count,
        COUNT(CASE WHEN product_id IS NULL OR TRIM(product_id) = '' THEN 1 END) AS missing_product_id_count,
        COUNT(CASE WHEN seller_id IS NULL OR TRIM(seller_id) = '' THEN 1 END) AS missing_seller_id_count,

        -- 3. Value Constraints (Integer Ranges)
        COUNT(CASE WHEN order_item_id <= 0 THEN 1 END) AS invalid_order_item_id_range_count,

        -- 4. Pricing and Financial Bounds
        COUNT(CASE WHEN price IS NULL OR price <= 0 THEN 1 END) AS invalid_price_count,
        COUNT(CASE WHEN freight_value IS NULL OR freight_value < 0 THEN 1 END) AS invalid_freight_count,

        -- 5. Temporal and Shipping Constraints
        COUNT(CASE WHEN shipping_limit_date IS NULL THEN 1 END) AS missing_shipping_limit_count,
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count
    FROM silver.order_items
),
duplicate_checks AS (
    -- 6. Composite Primary Key Uniqueness Check (order_id + order_item_id)
    SELECT COUNT(*) AS duplicate_pk_combination_count
    FROM (
        SELECT order_id, order_item_id
        FROM silver.order_items
        WHERE order_id IS NOT NULL AND order_item_id IS NOT NULL
        GROUP BY order_id, order_item_id
        HAVING COUNT(*) > 1
    ) sub
)
SELECT 
    v.total_records,
    v.missing_order_id_count,
    v.null_order_item_id_count,
    d.duplicate_pk_combination_count,
    v.missing_product_id_count,
    v.missing_seller_id_count,
    v.invalid_order_item_id_range_count,
    v.invalid_price_count,
    v.invalid_freight_count,
    v.missing_shipping_limit_count,
    v.system_date_mismatch_count,
    -- Summary Status Evaluator
    CASE 
        WHEN (
            v.missing_order_id_count + 
            v.null_order_item_id_count + 
            d.duplicate_pk_combination_count + 
            v.missing_product_id_count + 
            v.missing_seller_id_count + 
            v.invalid_order_item_id_range_count + 
            v.invalid_price_count + 
            v.invalid_freight_count + 
            v.missing_shipping_limit_count + 
            v.system_date_mismatch_count
        ) = 0 THEN 'PASSED'
        ELSE 'FAILED'
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d;

--========================================================================================
-- 1. Missing Order ID Check
-- Identifies records that are missing the parent order reference
SELECT order_item_id, order_id
FROM silver.order_items
WHERE order_id IS NULL OR TRIM(order_id) = '';

-- 2. Null Order Item ID Check
-- Identifies records missing the sequence number of the item within the order.
SELECT order_id, order_item_id
FROM silver.order_items
WHERE order_item_id IS NULL;

-- 3. Duplicate Composite Primary Key Check
-- Identifies duplicate records for the same item within a single order, violating the composite primary key constraint (order_id + order_item_id).
SELECT order_id, order_item_id
FROM silver.order_items
WHERE order_id IS NOT NULL AND order_item_id IS NOT NULL
GROUP BY order_id, order_item_id
HAVING COUNT(*) > 1;

-- 4. Missing Product ID Check
-- Identifies order items that do not point to a valid product identifier.
SELECT order_id, order_item_id, product_id
FROM silver.order_items
WHERE product_id IS NULL OR TRIM(product_id) = '';

-- 5. Missing Seller ID Check
-- Identifies order items that do not have an assigned vendor/seller.
SELECT order_id, order_item_id, seller_id
FROM silver.order_items
WHERE seller_id IS NULL OR TRIM(seller_id) = '';

-- 6. Invalid Order Item ID Range Check
-- Identifies records where the item sequence sequence number is zero or negative.

SELECT order_id, order_item_id
FROM silver.order_items
WHERE order_item_id <= 0;

-- 7. Invalid Price Check
-- Identifies records where the item cost is missing, zero, or negative.

SELECT order_id, order_item_id, price
FROM silver.order_items
WHERE price IS NULL OR price <= 0;

-- 8. Invalid Freight Value Check
-- Identifies records where the freight cost is missing or negative (zero freight is allowed for free shipping).

SELECT order_id, order_item_id, freight_value
FROM silver.order_items
WHERE freight_value IS NULL OR freight_value < 0;

-- 9. Missing Shipping Limit Date Check
-- Identifies records missing the seller's shipping deadline timestamp.

SELECT order_id, order_item_id, shipping_limit_date
FROM silver.order_items
WHERE shipping_limit_date IS NULL;

-- 10. System Audit Date Mismatch Check
-- Identifies illogical ingestion tracking metadata where the record update date occurs before its initial creation date.

SELECT order_id, order_item_id, create_date, update_date
FROM silver.order_items
WHERE update_date < create_date;