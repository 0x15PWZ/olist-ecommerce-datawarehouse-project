
-- Creating fact_sales 
CREATE OR REPLACE VIEW gold.fact_sales AS

SELECT

    oi.order_id,
    oi.order_item_id,

    o.customer_id,
    oi.product_id,
    oi.seller_id,

    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value
        AS total_sales_amount,


    p.total_payment_value,
    p.total_installments,
    p.payment_count,
    p.payment_types,
    r.review_score,

    CURRENT_TIMESTAMP AS create_date

FROM silver.order_items oi

INNER JOIN silver.orders o
    ON oi.order_id = o.order_id

LEFT JOIN gold.order_payments p
    ON oi.order_id = p.order_id

LEFT JOIN silver.order_reviews r
    ON oi.order_id = r.order_id;