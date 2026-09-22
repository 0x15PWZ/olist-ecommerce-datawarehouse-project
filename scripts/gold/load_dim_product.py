"""
============================================================
Gold Layer

Dimension : Products

Source
------------------------------------------------------------
silver.products

Target
------------------------------------------------------------
gold.dim_products

Purpose
------------------------------------------------------------
Create Product Dimension using Surrogate Key.
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

TARGET_TABLE = "gold.dim_products"


def load_dim_products(spark):
    """
    Load Product Dimension into Gold Layer.
    """

    # ======================================================
    # Step 1 : Read Silver Table
    # ======================================================

    products_df = (
        spark.read
        .jdbc(
            url=DB_URL,
            table="silver.products",
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 2 : Remove Duplicate Products
    # ======================================================

    products_df = products_df.dropDuplicates(
        ["product_id"]
    )

    # ======================================================
    # Step 3 : Generate Surrogate Key
    # ======================================================

    window_spec = Window.orderBy(
        col("product_id")
    )

    dim_product_df = (

        products_df

        .withColumn(

            "product_key",

            row_number().over(window_spec)

        )

        .select(

            "product_key",

            "product_id",

            "product_category_name",

            "product_name_length",

            "product_description_length",

            "product_photos_qty",

            "product_weight_g",

            "product_length_cm",

            "product_height_cm",

            "product_width_cm",

            "create_date",

            "update_date",

            "source_system"

        )

    )

    # ======================================================
    # Step 4 : Write Gold Table
    # ======================================================

    (
        dim_product_df.write
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
    print(f"Rows  : {dim_product_df.count()}")
    print("=" * 60)