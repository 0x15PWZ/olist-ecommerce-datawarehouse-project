"""
============================================================
Gold Layer

Dimension : Reviews

Source
------------------------------------------------------------
silver.order_reviews

Target
------------------------------------------------------------
gold.dim_review

Purpose
------------------------------------------------------------
Create Review Dimension using Surrogate Key.
============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES,
)

from pyspark.sql.window import Window

from pyspark.sql.functions import (
    row_number,
    col,
    when
)

TARGET_TABLE = "gold.dim_review"


def load_dim_review(spark):
    """
    Load Review Dimension into Gold Layer.
    """

    # ======================================================
    # Step 1 : Read Silver Table
    # ======================================================

    review_df = (
        spark.read
        .jdbc(
            url=DB_URL,
            table="silver.order_reviews",
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 2 : Remove Duplicate Reviews
    # ======================================================

    review_df = review_df.dropDuplicates(
        ["review_id"]
    )

    # ======================================================
    # Step 3 : Create Review Sentiment
    # ======================================================

    review_df = review_df.withColumn(
        "review_sentiment",
        when(col("review_score") >= 4, "Positive")
        .when(col("review_score") == 3, "Neutral")
        .otherwise("Negative")
    )

    # ======================================================
    # Step 4 : Generate Surrogate Key
    # ======================================================

    window_spec = Window.orderBy(
        col("review_id")
    )

    dim_review_df = (

        review_df

        .withColumn(

            "review_key",

            row_number().over(window_spec)

        )

        .select(

            "review_key",

            "review_id",

            "review_score",

            "review_sentiment",

            "review_comment_title",

            "review_comment_message",

            "review_creation_date",

            "review_answer_timestamp",

            "create_date",

            "update_date",

            "source_system"

        )

    )

    # ======================================================
    # Step 5 : Write Gold Table
    # ======================================================

    (
        dim_review_df.write
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
    print("Gold Dimension Loaded")
    print(f"Table : {TARGET_TABLE}")
    print(f"Rows  : {dim_review_df.count()}")
    print("=" * 60)