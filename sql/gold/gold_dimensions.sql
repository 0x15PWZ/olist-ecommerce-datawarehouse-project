/*
This script is for creation of dimension tables.

*/
-- Create dim_customers
CREATE OR REPLACE VIEW gold.dim_customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    create_date,
    update_date,
    source_system
FROM silver.customers;

-- Create dim_products
CREATE OR REPLACE VIEW gold.dim_products AS

SELECT
    p.product_id,

    p.product_category_name,

    pct.product_category_name_english,

    p.product_name_length,

    p.product_description_length,

    p.product_photos_qty,

    p.product_weight_g,

    p.product_length_cm,

    p.product_height_cm,

    p.product_width_cm,

    p.create_date,

    p.update_date

FROM silver.products p

LEFT JOIN silver.product_category_name_translation pct

ON p.product_category_name =
   pct.product_category_name;

-- Create dim_sellers
CREATE OR REPLACE VIEW gold.dim_sellers AS
(
    seller_id VARCHAR(50) PRIMARY KEY,

    seller_zip_code_prefix INTEGER,

    seller_city VARCHAR(100),

    seller_state VARCHAR(2),

    create_date TIMESTAMP,

    update_date TIMESTAMP,

    source_system VARCHAR(100)
);

-- Create dim payment
CREATE OR REPLACE VIEW gold.order_payments AS

SELECT

    order_id,

    SUM(payment_value) AS total_payment_value,

    SUM(payment_installments) AS total_installments,

    COUNT(*) AS payment_count,

    STRING_AGG(
        DISTINCT payment_type,
        ', '
        ORDER BY payment_type
    ) AS payment_types

FROM silver.order_payments
GROUP BY order_id;

-- Create dim_date
CREATE OR REPLACE VIEW gold.dim_date AS
(
    date_key INTEGER PRIMARY KEY,

    full_date DATE,

    day INTEGER,

    month INTEGER,

    month_name VARCHAR(20),

    quarter INTEGER,

    year INTEGER,

    week INTEGER,

    weekday INTEGER,

    weekday_name VARCHAR(20),

    is_weekend BOOLEAN
);