/*
    This script is for the manipulation of data in PostgreSQL.
*/

-SELECT 
    column_name, 
    data_type,
    character_maximum_length AS max_length
FROM 
    information_schema.columns
WHERE 
    table_schema = 'bronze' -- Replace with schema name if different
    AND table_name = 'order_items';- Check the column data types for specific table
 -- Replace with table name

-- Check the data existence
select * 
from bronze.customers
limit 100;

select * 
from bronze.orders
limit 100;

select * 
from bronze.order_items
limit 100;

select * 
from bronze.order_reviews
limit 100;

select * 
from bronze.order_payments
limit 100;

select * 
from bronze.products
limit 100;

select * 
from bronze.product_category_name_translation
limit 100;

select * 
from bronze.sellers
limit 100;

select * 
from bronze.geolocation
limit 100;

-- 