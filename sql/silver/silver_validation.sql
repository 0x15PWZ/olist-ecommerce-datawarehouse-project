/* 
This script for the validation for silver layer tables.

=========================================================
Silver Validation Report
=========================================================

customers
✔ Row Count
✔ Duplicate Check
✔ Null Check
✔ Metadata Check

orders
✔ Row Count
✔ Duplicate Check
✔ Timestamp Check

order_items
✔ Row Count
✔ Duplicate Check

=========================================================
Overall Result

PASS
=========================================================
*/

-- 1. Row Count Validation
SELECT COUNT(*) FROM bronze.customers;
SELECT COUNT(*) FROM silver.customers;

SELECT COUNT(*) FROM bronze.orders;
SELECT COUNT(*) FROM silver.orders;

SELECT COUNT(*) FROM bronze.order_items;
SELECT COUNT(*) FROM silver.order_items;

SELECT COUNT(*) FROM bronze.order_payments;
SELECT COUNT(*) FROM silver.order_payments;

SELECT COUNT(*) FROM bronze.order_reviews;
SELECT COUNT(*) FROM silver.order_reviews;

SELECT COUNT(*) FROM bronze.geolocation;
SELECT COUNT(*) FROM silver.geolocation;

SELECT COUNT(*) FROM bronze.products;
SELECT COUNT(*) FROM silver.products;

SELECT COUNT(*) FROM bronze.sellers;
SELECT COUNT(*) FROM silver.sellers;

SELECT COUNT(*) FROM bronze.product_category_name_translation;
SELECT COUNT(*) FROM silver.product_category_name_translation;


-- 2. Duplicate Business Key Validation

SELECT
    customer_id,
    COUNT(*)
FROM silver.customers
GROUP BY customer_id
HAVING COUNT(*) > 1;

SELECT
    order_id,
    COUNT(*)
FROM silver.orders
GROUP BY order_id
HAVING COUNT(*) > 1;

SELECT
    product_id,
    COUNT(*)
FROM silver.products
GROUP BY product_id
HAVING COUNT(*) > 1;

-- 3. NULL Business Key Validation

SELECT COUNT(*)
FROM silver.customers
WHERE customer_id IS NULL;

SELECT COUNT(*)
FROM silver.orders
WHERE order_id IS NULL;

SELECT COUNT(*)
FROM silver.products
WHERE product_id IS NULL;

-- 4. Empty String Validation

SELECT COUNT(*)
FROM silver.customers
WHERE TRIM(customer_id)='';

SELECT COUNT(*)
FROM silver.orders
WHERE TRIM(order_id)='';

SELECT COUNT(*)
FROM silver.products
WHERE TRIM(product_id)='';

-- 5. Metadata Validation

SELECT
COUNT(*)
FROM silver.customers
WHERE create_date IS NULL;

SELECT
COUNT(*)
FROM silver.customers
WHERE update_date IS NULL;

SELECT
COUNT(*)
FROM silver.customers
WHERE source_system IS NULL;

-- 6. Column Length Validation

SELECT
MAX(LENGTH(customer_city))
FROM silver.customers;

-- 7. Business Rule Validation

SELECT *
FROM silver.customers
WHERE LENGTH(customer_state)<>2;


-- 8. Referential Integrity

SELECT
COUNT(*)
FROM silver.orders o
LEFT JOIN silver.customers c
ON o.customer_id=c.customer_id
WHERE c.customer_id IS NULL;

SELECT COUNT(*)
FROM silver.order_items oi
LEFT JOIN silver.products p
ON oi.product_id=p.product_id
WHERE p.product_id IS NULL;

SELECT COUNT(*)
FROM silver.order_items oi
LEFT JOIN silver.sellers s
ON oi.seller_id=s.seller_id
WHERE s.seller_id IS NULL;

-- 9. Data Type Validation

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='customers';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='orders';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='order_items';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='order_payments';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='order_reviews';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='products';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='sellers';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='geolocation';

SELECT
column_name,
data_type
FROM information_schema.columns
WHERE table_schema='silver'
AND table_name='product_category_name_translation';





