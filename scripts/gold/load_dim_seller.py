"""
============================================================
Gold Layer

Dimension : Sellers

Source
------------------------------------------------------------
silver.sellers

Target
------------------------------------------------------------
gold.dim_sellers

Purpose
------------------------------------------------------------
Create Seller Dimension using Surrogate Key.
============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES,
)

from pyspark.sql.window import Window

from pyspark.sql.functions import (
    row_number,
    col
)

TARGET_TABLE = "gold.dim_sellers"


def load_dim_sellers(spark):
    """
    Load Seller Dimension into Gold Layer.
    """

    # ======================================================
    # Step 1 : Read Silver Table
    # ======================================================

    sellers_df = (
        spark.read
        .jdbc(
            url=DB_URL,
            table="silver.sellers",
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 2 : Remove Duplicate Sellers
    # ======================================================

    sellers_df = sellers_df.dropDuplicates(
        ["seller_id"]
    )

    # ======================================================
    # Step 3 : Generate Surrogate Key
    # ======================================================

    window_spec = Window.orderBy(
        col("seller_id")
    )

    dim_seller_df = (

        sellers_df

        .withColumn(

            "seller_key",

            row_number().over(window_spec)

        )

        .select(

            "seller_key",

            "seller_id",

            "seller_zip_code_prefix",

            "seller_city",

            "seller_state",

            "create_date",

            "update_date",

            "source_system"

        )

    )

    # ======================================================
    # Step 4 : Write Gold Table
    # ======================================================

    (
        dim_seller_df.write
        .mode("overwrite")
        .jdbc(
            url=DB_URL,
            table=TARGET_TABLE,
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 5 : Logging
    # ======================================================

    print("=" * 60)
    print("Gold Dimension Loaded")
    print(f"Table : {TARGET_TABLE}")
    print(f"Rows  : {dim_seller_df.count()}")
    print("=" * 60)