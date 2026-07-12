/*
  This is creation of nine tables in PostgreSQL.
  Tables:
  	1. customers
	2. geolocation
	3. orders
  	4. order_items
	5. order_payments
	6. order_reviews
	7. products
	8. product_category_name_translation
  	9. sellers 
*/
-- Create customers table
CREATE TABLE IF NOT EXISTS bronze.customers (
    customer_id VARCHAR(50),
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(50),
    customer_state VARCHAR(2)
);

-- Create geolocation table
CREATE TABLE IF NOT EXISTS bronze.geolocation (
	geolocation_zip_code_prefix INT,
	geolocation_lat NUMERIC(10,2),
	geolocation_lng NUMERIC(10,2),
	geolocation_city VARCHAR(50),
	geolocation_state VARCHAR(2)
);


-- Create orders table
CREATE TABLE IF NOT EXISTS bronze.orders (
	order_id VARCHAR(50),
	customer_id VARCHAR(50),
	order_status VARCHAR(50),
	order_purchase_timestamp TIMESTAMP,
	order_approved_at TIMESTAMP,
	order_delivered_carrier_date TIMESTAMP,
	order_delivered_customer_date TIMESTAMP,
	order_estimated_delivery_date TIMESTAMP
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS bronze.order_items (
	order_id VARCHAR(50),
	order_item_id INT,
	product_id VARCHAR(50),
	seller_id VARCHAR(5),
	shipping_limit_date TIMESTAMP,
	price NUMERIC(10,2),
	freight_value NUMERIC(10,2)
);

-- Create order_payments table
CREATE TABLE IF NOT EXISTS bronze.order_payments (
	order_id VARCHAR(50),
	payment_sequential INT,
	payment_type VARCHAR(50),
	payment_installments INT,
	payment_value NUMERIC(10,2)
);

-- Create order_reviews table
CREATE TABLE IF NOT EXISTS bronze.order_reviews (
	review_id VARCHAR(50),
	order_id VARCHAR(50),
	review_score INT,
	review_comment_title VARCHAR(50),
	review_comment_message TEXT,
	review_creation_date TIMESTAMP,
	review_answer_timestamp TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS bronze.products (
	product_id VARCHAR(50),
	product_category_name VARCHAR(50),
	product_name_lenght INT,
	product_description_lenght INT,
	product_photos_qty INT,
	product_weight_g INT,
	product_length_cm INT,
	product_height_cm INT,
	product_width_cm INT
);

-- Create product_category_name_translation table
CREATE TABLE IF NOT EXISTS bronze.product_category_name_translation (
	product_category_name VARCHAR(50),
	product_category_name_english VARCHAR(50)
);

-- Create sellers table
CREATE TABLE IF NOT EXISTS bronze.sellers (
	seller_id VARCHAR(50),
	seller_zip_code_prefix INT,
	seller_city VARCHAR(50),
	seller_state VARCHAR(2)
);


