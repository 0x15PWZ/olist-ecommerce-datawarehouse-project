"""
============================================================
Gold Layer

Fact Table : Reviews

Source
------------------------------------------------------------
silver.order_reviews
silver.orders

Target
------------------------------------------------------------
gold.fact_reviews

Grain
------------------------------------------------------------
One Row = One Review

Purpose
------------------------------------------------------------
Store customer review transactions using surrogate keys.
============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES,
)

TARGET_TABLE = "gold.fact_reviews"


def load_fact_reviews(spark):

    # ======================================================
    # Step 1 : Read Silver Tables
    # ======================================================

    reviews_df = spark.read.jdbc(
        url=DB_URL,
        table="silver.order_reviews",
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

    dim_review_df = spark.read.jdbc(
        url=DB_URL,
        table="gold.dim_review",
        properties=DB_PROPERTIES
    )

    # ======================================================
    # Step 3 : Create Temp Views
    # ======================================================

    reviews_df.createOrReplaceTempView("reviews")

    orders_df.createOrReplaceTempView("orders")

    dim_customer_df.createOrReplaceTempView("dim_customers")

    dim_review_df.createOrReplaceTempView("dim_review")

    # ======================================================
    # Step 4 : Build Fact Table
    # ======================================================

    fact_reviews = spark.sql("""

    SELECT

        --------------------------------------------------
        -- Degenerate Dimension
        --------------------------------------------------

        r.order_id,

        --------------------------------------------------
        -- Surrogate Keys
        --------------------------------------------------

        dc.customer_key,

        dr.review_key,

        CAST(
            date_format(
                r.review_creation_date,
                'yyyyMMdd'
            ) AS INT
        ) AS review_date_key,

        CAST(
            date_format(
                r.review_answer_timestamp,
                'yyyyMMdd'
            ) AS INT
        ) AS review_answer_date_key,

        --------------------------------------------------
        -- Measures
        --------------------------------------------------

        r.review_score,

        --------------------------------------------------
        -- Metadata
        --------------------------------------------------

        r.create_date,

        r.update_date,

        r.source_system

    FROM reviews r

    INNER JOIN orders o

        ON r.order_id = o.order_id

    INNER JOIN dim_customers dc

        ON o.customer_id = dc.customer_id

    INNER JOIN dim_review dr

        ON r.review_id = dr.review_id

    """)

    # ======================================================
    # Step 5 : Write Gold Table
    # ======================================================

    (
        fact_reviews.write
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
    print(f"Rows  : {fact_reviews.count()}")
    print("=" * 60)