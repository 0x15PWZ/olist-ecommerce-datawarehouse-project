"""
============================================================
Gold Layer

Fact Table : Sales

Source
------------------------------------------------------------
silver.orders
silver.order_items

Target
------------------------------------------------------------
gold.fact_sales

Grain
------------------------------------------------------------
One Row = One Order Item

Purpose
------------------------------------------------------------
Sales Fact Table using Surrogate Keys.
============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES,
)

TARGET_TABLE = "gold.fact_sales"


def load_fact_sales(spark):

    # ======================================================
    # Read Silver Tables
    # ======================================================

    orders_df = spark.read.jdbc(
        url=DB_URL,
        table="silver.orders",
        properties=DB_PROPERTIES
    )

    order_items_df = spark.read.jdbc(
        url=DB_URL,
        table="silver.order_items",
        properties=DB_PROPERTIES
    )

    # ======================================================
    # Read Gold Dimensions
    # ======================================================

    dim_customer_df = spark.read.jdbc(
        url=DB_URL,
        table="gold.dim_customers",
        properties=DB_PROPERTIES
    )

    dim_product_df = spark.read.jdbc(
        url=DB_URL,
        table="gold.dim_products",
        properties=DB_PROPERTIES
    )

    dim_seller_df = spark.read.jdbc(
        url=DB_URL,
        table="gold.dim_sellers",
        properties=DB_PROPERTIES
    )

    # ======================================================
    # Create Temp Views
    # ======================================================

    orders_df.createOrReplaceTempView("orders")

    order_items_df.createOrReplaceTempView("order_items")

    dim_customer_df.createOrReplaceTempView("dim_customers")

    dim_product_df.createOrReplaceTempView("dim_products")

    dim_seller_df.createOrReplaceTempView("dim_sellers")

    # ======================================================
    # Build Fact Table
    # ======================================================

    fact_sales = spark.sql("""

    SELECT

        --------------------------------------------------
        -- Degenerate Dimensions
        --------------------------------------------------

        oi.order_id,

        oi.order_item_id,

        o.order_status,

        oi.shipping_limit_date,

        --------------------------------------------------
        -- Surrogate Keys
        --------------------------------------------------

        dc.customer_key,

        dp.product_key,

        ds.seller_key,

        CAST(date_format(
            o.order_purchase_timestamp,
            'yyyyMMdd'
        ) AS INT) AS purchase_date_key,

        CAST(date_format(
            o.order_approved_at,
            'yyyyMMdd'
        ) AS INT) AS approval_date_key,

        CAST(date_format(
            o.order_delivered_carrier_date,
            'yyyyMMdd'
        ) AS INT) AS carrier_date_key,

        CAST(date_format(
            o.order_delivered_customer_date,
            'yyyyMMdd'
        ) AS INT) AS delivered_date_key,

        CAST(date_format(
            o.order_estimated_delivery_date,
            'yyyyMMdd'
        ) AS INT) AS estimated_delivery_date_key,

        --------------------------------------------------
        -- Measures
        --------------------------------------------------

        oi.price,

        oi.freight_value,

        --------------------------------------------------
        -- Metadata
        --------------------------------------------------

        o.create_date,

        o.update_date,

        o.source_system

    FROM order_items oi

    INNER JOIN orders o
        ON oi.order_id = o.order_id

    INNER JOIN dim_customers dc
        ON o.customer_id = dc.customer_id

    INNER JOIN dim_products dp
        ON oi.product_id = dp.product_id

    INNER JOIN dim_sellers ds
        ON oi.seller_id = ds.seller_id

    """)

    # ======================================================
    # Write Fact Table
    # ======================================================

    (
        fact_sales.write
        .mode("overwrite")
        .jdbc(
            url=DB_URL,
            table=TARGET_TABLE,
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Logging
    # ======================================================

    print("=" * 60)
    print("Gold Fact Loaded")
    print(f"Table : {TARGET_TABLE}")
    print(f"Rows  : {fact_sales.count()}")
    print("=" * 60)