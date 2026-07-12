/*
============================================================
Silver Layer
============================================================

1. Customers Table Transformation
============================================================
Purpose
------------------------------------------------------------
Transform Bronze Customers data into clean and
standardized Silver Customers data.

Business Rules
------------------------------------------------------------
1. Remove records with NULL customer_id
2. Remove duplicate customer_id
3. Trim leading/trailing whitespace
4. Convert city to uppercase
5. Convert state to uppercase
6. Replace NULL or empty city with 'UNKNOWN'
7. Replace NULL or empty state with 'UNKNOWN'
============================================================
*/

SELECT
    TRIM(customer_id) AS customer_id,
    TRIM(customer_unique_id) AS customer_unique_id,
    customer_zip_code_prefix,
    UPPER(TRIM(customer_city)) AS customer_city,
    UPPER(TRIM(customer_state)) AS customer_state
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY customer_id
        ) AS flag_customer
    FROM bronze.customers
) AS t
WHERE customer_id IS NOT NULL
  AND flag_customer = 1;

/*
============================================================
2. Orders Table Transformation
============================================================
Purpose
------------------------------------------------------------
Transform Bronze Orders data into clean and
standardized Silver Orders data.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty order_id
2. Remove duplicate order_id (keep latest purchase timestamp)
3. Trim string columns
4. Convert order_status to uppercase
5. Standardize timestamp columns
6. Validate timestamp sequence
============================================================
*/
WITH deduplicated_orders AS (
	SELECT
		*,
		-- Order by purchase time descending to pick the latest record
		ROW_NUMBER() OVER (
			PARTITION BY order_id 
			ORDER BY order_purchase_timestamp DESC NULLS LAST
		) AS flag_order
	FROM bronze.orders
	WHERE order_id IS NOT NULL AND TRIM(order_id) != '' 
)
SELECT 
	TRIM(order_id) AS order_id,                        
	TRIM(customer_id) AS customer_id,                  
	UPPER(TRIM(order_status)) AS order_status,          
	order_purchase_timestamp::timestamp AS order_purchase_timestamp,
	order_approved_at::timestamp AS order_approved_at,
	CAST(order_delivered_carrier_date AS timestamp) AS order_delivered_carrier_date,
	CAST(order_delivered_customer_date AS timestamp) AS order_delivered_customer_date,
	CAST(order_estimated_delivery_date AS timestamp) AS order_estimated_delivery_date
FROM deduplicated_orders
WHERE flag_order = 1; 

/*

3 — Order Items Transformation
==============================
Purpose
------------------------------------------------
Transform Bronze Order Items data into clean and
standardized Silver Order Items data.
------------------------------------------------
Business Key: (order_id, order_item_id)
Business Rules
	1. Remove NULL keys
	2. Remove duplicates
	3. Trim IDs
	4. Cast price
	5. Cast freight_value
	6. Cast shipping_limit_date
*/

WITH cleaned_order_items AS (
    SELECT 
        -- Rule 3: Trim IDs
        TRIM(order_id) AS order_id,
		TRIM(product_id) AS product_id,
		TRIM(seller_id) AS seller_id,
        order_item_id,
        price,
        freight_value,
        shipping_limit_date,
        -- Rule 2: Prepare for duplicate removal by ranking rows per business key
        ROW_NUMBER() OVER (
            PARTITION BY TRIM(order_id), order_item_id
            ORDER BY shipping_limit_date DESC -- Keeps the most recent record if duplicates exist
        ) as row_num
    FROM bronze.order_items
    WHERE 
        -- Rule 1: Remove NULL keys
        order_id IS NOT NULL 
        AND order_item_id IS NOT NULL
)
SELECT 
    order_id,
    order_item_id,
	product_id,
	seller_id,
    -- Rule 4 & 5: Cast financial values to NUMERIC for precision
    CAST(price AS NUMERIC(10, 2)) AS price,
    CAST(freight_value AS NUMERIC(10, 2)) AS freight_value,
    -- Rule 6: Cast to TIMESTAMP (or DATE depending on your data string)
    CAST(shipping_limit_date AS TIMESTAMP ) AS shipping_limit_date
FROM cleaned_order_items
WHERE row_num = 1; -- Rule 2: Filters out the duplicates, keeping only the first instance

/*
4 — Order Payments Transformation
==============================
Purpose
------------------------------------------------
Transform Bronze Order Payments data into clean and
standardized Silver Order Payments data.
------------------------------------------------
=========================
Business Key: (order_id, payment_sequential)
Business Rules
	1. Remove NULL keys
	2. Remove duplicates
	3. Uppercase payment_type
	4. Cast payment_installments
	5. Cast payment_value
*/
WITH cleaned_payments AS (
    SELECT 
        TRIM(order_id) AS order_id,
        payment_sequential,
        -- Rule 3: Uppercase payment_type
        UPPER(TRIM(payment_type)) AS payment_type,
        payment_installments,
        payment_value,
        -- Rule 2: Prepare for duplicate removal by ranking rows per business key
        ROW_NUMBER() OVER (
            PARTITION BY TRIM(order_id), payment_sequential 
            ORDER BY payment_value DESC -- Keeps the highest value record if duplicates exist
        ) AS row_num
    FROM bronze.order_payments
    WHERE 
        -- Rule 1: Remove NULL keys
        order_id IS NOT NULL 
        AND payment_sequential IS NOT NULL
)
SELECT 
    order_id,
    payment_sequential,
    payment_type,
    -- Rule 4: Cast installments to an INTEGER
    CAST(payment_installments AS INTEGER) AS payment_installments,
    -- Rule 5: Cast payment value to NUMERIC for financial precision
    CAST(payment_value AS NUMERIC(10, 2)) AS payment_value
FROM cleaned_payments
WHERE row_num = 1; -- Rule 2: Filters out duplicates, keeping only the unique business key

/*

5 — Order Reviews Transformation
==============================
Purpose
------------------------------------------------
Transform Bronze Order Reviews data into clean and
standardized Silver Order Reviews data.
------------------------------------------------
========================
Business Key: review_id
Business Rules
	1. Remove NULL review_id
	2. Remove duplicates
	3. Trim text
	4. Uppercase review title
	5. Cast review_score
	6. Cast timestamps
*/
WITH cleaned_reviews AS (
    SELECT 
        TRIM(review_id) AS review_id,
        TRIM(order_id) AS order_id,
        review_score,
        -- Rule 3 & 4: Trim and Uppercase the review title
        UPPER(TRIM(review_comment_title)) AS review_comment_title,
        -- Rule 3: Trim the comment message
        TRIM(review_comment_message) AS review_comment_message,
        review_creation_date,
        review_answer_timestamp,
        -- Rule 2: Prepare for duplicate removal by ranking rows per review_id
        ROW_NUMBER() OVER (
            PARTITION BY TRIM(review_id) 
            ORDER BY review_answer_timestamp DESC -- Keeps the latest submission if duplicates exist
        ) AS row_num
    FROM bronze.order_reviews
    WHERE 
        -- Rule 1: Remove NULL review_id
        review_id IS NOT NULL
)
SELECT 
    review_id,
    order_id,
    -- Rule 5: Cast review score to a standard SMALLINT or INTEGER
    CAST(review_score AS INTEGER) AS review_score,
    review_comment_title,
    review_comment_message,
    -- Rule 6: Cast date and timestamp fields
    CAST(review_creation_date AS DATE) AS review_creation_date,
    CAST(review_answer_timestamp AS TIMESTAMP) AS review_answer_timestamp
FROM cleaned_reviews
WHERE row_num = 1; -- Rule 2: Filters out duplicates, keeping only the unique business key

/*
6 — Products Transformation
==============================
Purpose
------------------------------------------------
Transform Bronze Products data into clean and
standardized Silver Products data.
------------------------------------------------
==================
Business Key: product_id
Business Rules
	1. Remove NULL product_id
	2. Remove duplicates
	3. Trim category name
	4. Uppercase category name
	5. Cast all numeric columns
*/
WITH cleaned_products AS (
    SELECT 
        TRIM(product_id) AS product_id,
        -- Rule 3 & 4: Trim and Uppercase the category name
        UPPER(TRIM(product_category_name)) AS product_category_name,
        product_name_lenght,
        product_name_description_lenght,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm,
        -- Rule 2: Prepare for duplicate removal by ranking rows per product_id
        ROW_NUMBER() OVER (
            PARTITION BY TRIM(product_id) 
            ORDER BY product_category_name DESC NULLS LAST -- Keeps populated rows over nulls if duplicates exist
        ) AS row_num
    FROM bronze.products
    WHERE 
        -- Rule 1: Remove NULL product_id
        product_id IS NOT NULL
)
SELECT 
    product_id,
    product_category_name,
    -- Rule 5: Cast all numeric counts/lengths to INTEGER
    CAST(product_name_lenght AS INTEGER) AS product_name_length,
    CAST(product_name_description_lenght AS INTEGER) AS product_name_description_length,
    CAST(product_photos_qty AS INTEGER) AS product_photos_qty,
    -- Rule 5: Cast physical dimensions to NUMERIC/DECIMAL for precision
    CAST(product_weight_g AS NUMERIC(10, 2)) AS product_weight_g,
    CAST(product_length_cm AS NUMERIC(10, 2)) AS product_length_cm,
    CAST(product_height_cm AS NUMERIC(10, 2)) AS product_height_cm,
    CAST(product_width_cm AS NUMERIC(10, 2)) AS product_width_cm
FROM cleaned_products
WHERE row_num = 1; -- Rule 2: Filters out duplicates, keeping only the unique product_id

/*
7 — Order Items Transformation
==============================
Purpose
------------------------------------------------
Transform Bronze Sellers data into clean and
standardized Silver Sellers data.
------------------------------------------------
==================
Business Key: seller_id
Business Rules
	1. Remove NULL seller_id
	2. Remove duplicates
	3. Trim
	4. Uppercase city/state
*/

WITH cleaned_sellers AS (
    SELECT 
		-- Trim seller_id
        TRIM(seller_id) AS seller_id,
		seller_zip_code_prefix,
        -- Rule 3 & 4: Trim and Uppercase the city and state
        UPPER(TRIM(seller_city)) AS seller_city,
        UPPER(TRIM(seller_state)) AS seller_state,
        -- Rule 2: Prepare for duplicate removal by ranking rows per seller_id
        ROW_NUMBER() OVER (
            PARTITION BY TRIM(seller_id) 
            ORDER BY seller_state DESC NULLS LAST -- Keeps populated rows over nulls if duplicates exist
        ) AS row_num
    FROM bronze.sellers
    WHERE 
        -- Rule 1: Remove NULL seller_id
        seller_id IS NOT NULL
)
SELECT 
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM cleaned_sellers
WHERE row_num = 1; -- Rule 2: Filters out duplicates, keeping only the unique seller_id

/*
8 — Geolocation Transformation
==============================
Purpose
------------------------------------------------
Transform Bronze Geolocation data into clean and
standardized Silver Geolocation data.
------------------------------------------------
======================
Business Key
There is no single business key.
	Use
	zip
	lat
	lng
	city
	state
for deduplication.
Business Rules
	1. Remove duplicate rows
	2. Trim city/state
	3. Uppercase city/state
	4. Cast latitude/longitude
*/

WITH cleaned_geolocation AS (
    SELECT 
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        -- Rule 2 & 3: Trim and Uppercase the city and state
        UPPER(TRIM(geolocation_city)) AS geolocation_city,
        UPPER(TRIM(geolocation_state)) AS geolocation_state,
        -- Rule 1: Use all five elements to detect and rank exact duplicate rows
        ROW_NUMBER() OVER (
            PARTITION BY 
                geolocation_zip_code_prefix, 
                geolocation_lat, 
                geolocation_lng, 
                UPPER(TRIM(geolocation_city)), 
                UPPER(TRIM(geolocation_state))
            ORDER BY geolocation_zip_code_prefix -- Arbitrary ordering since rows are identical
        ) AS row_num
    FROM bronze.geolocation
)
SELECT 
    geolocation_zip_code_prefix,
    -- Rule 4: Cast latitude and longitude to DOUBLE PRECISION or NUMERIC
    CAST(geolocation_lat AS DOUBLE PRECISION) AS geolocation_lat,
    CAST(geolocation_lng AS DOUBLE PRECISION) AS geolocation_lng,
    geolocation_city,
    geolocation_state
FROM cleaned_geolocation
WHERE row_num = 1; -- Rule 1: Keeps only one unique row, dropping all duplicates

/*
9 — Product Category Name Translation
=====================================
Purpose
------------------------------------------------
Transform Bronze Product Category Name Translation data into clean and
standardized Silver Product Category Name Translation data.
------------------------------------------------
Business Key: product_category_name
Business Rules
	1. Remove NULL category
	2. Remove duplicates
	3. Trim both columns
	4. Uppercase both columns
	5. Limit length	
*/
WITH cleaned_translations AS (
    SELECT 
        -- Rule 3 & 4: Trim and Uppercase the columns
        UPPER(TRIM(product_category_name)) AS product_category_name,
        UPPER(TRIM(product_category_name_english)) AS product_category_name_english,
        -- Rule 2: Prepare for duplicate removal by ranking rows per product_category_name
        ROW_NUMBER() OVER (
            PARTITION BY UPPER(TRIM(product_category_name)) 
            ORDER BY product_category_name_english DESC NULLS LAST -- Keeps populated translations over nulls
        ) AS row_num
    FROM bronze.product_category_name_translation
    WHERE 
        -- Rule 1: Remove NULL category names
        product_category_name IS NOT NULL
)
SELECT 
    -- Rule 5: Limit string length using LEFT()
    LEFT(product_category_name, 50) AS product_category_name,
    LEFT(product_category_name_english, 50) AS product_category_name_english
FROM cleaned_translations
WHERE row_num = 1; -- Rule 2: Filters out duplicates, keeping only the unique category name

 