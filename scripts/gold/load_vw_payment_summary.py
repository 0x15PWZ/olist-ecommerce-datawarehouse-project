"""
============================================================
Gold Layer
View : Payment Summary
------------------------------------------------------------
vw_payment_summary

Purpose
------------------------------------------------------------
Aggregate payment transactions to one row per order.

Source
------------------------------------------------------------
gold.fact_payments

Grain
------------------------------------------------------------
One row = One order

============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES,
)


def load_vw_payment_summary(spark):

    # ======================================================
    # Step 1 : Read Gold Fact Table
    # ======================================================

    fact_payments_df = spark.read.jdbc(
        url=DB_URL,
        table="gold.fact_payments",
        properties=DB_PROPERTIES
    )

    # ======================================================
    # Step 2 : Create Temporary View
    # ======================================================

    fact_payments_df.createOrReplaceTempView(
        "fact_payments"
    )

    # ======================================================
    # Step 3 : Create Payment Summary
    # ======================================================

    payment_summary = spark.sql("""
        SELECT

            --------------------------------------------------
            -- Degenerate Dimension
            --------------------------------------------------

            order_id,

            --------------------------------------------------
            -- Payment Metrics
            --------------------------------------------------

            COUNT(*) AS payment_count,

            SUM(payment_value) AS total_payment,

            --------------------------------------------------
            -- Payment Type
            --------------------------------------------------

            CASE
                WHEN COUNT(DISTINCT payment_key) = 1
                THEN MAX(payment_key)
                ELSE NULL
            END AS payment_key,

            --------------------------------------------------
            -- Installment Information
            --------------------------------------------------

            MAX(payment_installments) AS max_payment_installments,

            --------------------------------------------------
            -- Metadata
            --------------------------------------------------

            MIN(create_date) AS create_date,

            MAX(update_date) AS update_date

        FROM fact_payments

        GROUP BY order_id
    """)

    # ======================================================
    # Step 4 : Register Temporary View
    # ======================================================

    payment_summary.createOrReplaceTempView(
        "vw_payment_summary"
    )

    # ======================================================
    # Step 5 : Logging
    # ======================================================

    print("=" * 60)
    print("Temporary View Created")
    print("View   : vw_payment_summary")
    print(f"Rows   : {payment_summary.count()}")
    print("=" * 60)

    return payment_summary