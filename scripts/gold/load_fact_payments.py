"""
============================================================
Gold Layer

Fact Table : Payments

Source
------------------------------------------------------------
silver.order_payments
silver.orders

Target
------------------------------------------------------------
gold.fact_payments

Grain
------------------------------------------------------------
One Row = One Payment Transaction

Purpose
------------------------------------------------------------
Store payment transactions using surrogate keys.
============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES,
)

TARGET_TABLE = "gold.fact_payments"


def load_fact_payments(spark):

    # ======================================================
    # Step 1 : Read Silver Tables
    # ======================================================

    payments_df = spark.read.jdbc(
        url=DB_URL,
        table="silver.order_payments",
        properties=DB_PROPERTIES
    )

    orders_df = spark.read.jdbc(
        url=DB_URL,
        table="silver.orders",
        properties=DB_PROPERTIES
    )

    # ======================================================
    # Step 2 : Read Gold Dimensions
    # ======================================================

    dim_customer_df = spark.read.jdbc(
        url=DB_URL,
        table="gold.dim_customers",
        properties=DB_PROPERTIES
    )

    dim_payment_df = spark.read.jdbc(
        url=DB_URL,
        table="gold.dim_payment",
        properties=DB_PROPERTIES
    )

    # ======================================================
    # Step 3 : Create Temp Views
    # ======================================================

    payments_df.createOrReplaceTempView("payments")

    orders_df.createOrReplaceTempView("orders")

    dim_customer_df.createOrReplaceTempView("dim_customers")

    dim_payment_df.createOrReplaceTempView("dim_payment")

    # ======================================================
    # Step 4 : Build Fact Table
    # ======================================================

    fact_payments = spark.sql("""

    SELECT

        --------------------------------------------------
        -- Degenerate Dimensions
        --------------------------------------------------

        p.order_id,

        p.payment_sequential,

        --------------------------------------------------
        -- Surrogate Keys
        --------------------------------------------------

        dc.customer_key,

        dp.payment_key,

        CAST(
            date_format(
                o.order_purchase_timestamp,
                'yyyyMMdd'
            ) AS INT
        ) AS purchase_date_key,

        --------------------------------------------------
        -- Measures
        --------------------------------------------------

        p.payment_value,

        p.payment_installments,

        --------------------------------------------------
        -- Metadata
        --------------------------------------------------

        p.create_date,

        p.update_date,

        p.source_system

    FROM payments p

    INNER JOIN orders o

        ON p.order_id = o.order_id

    INNER JOIN dim_customers dc

        ON o.customer_id = dc.customer_id

    INNER JOIN dim_payment dp

        ON p.payment_type = dp.payment_type
       AND p.payment_installments = dp.payment_installments

    """)

    # ======================================================
    # Step 5 : Write Gold Table
    # ======================================================

    (
        fact_payments.write
        .mode("overwrite")
        .jdbc(
            url=DB_URL,
            table=TARGET_TABLE,
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 6 : Logging
    # ======================================================

    print("=" * 60)
    print("Gold Fact Loaded")
    print(f"Table : {TARGET_TABLE}")
    print(f"Rows  : {fact_payments.count()}")
    print("=" * 60)