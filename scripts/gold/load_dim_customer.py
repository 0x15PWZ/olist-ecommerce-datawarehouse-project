"""
============================================================
Gold Layer

Dimension : Customers

Source
------------------------------------------------------------
silver.customers

Target
------------------------------------------------------------
gold.dim_customers

Purpose
------------------------------------------------------------
Create Customer Dimension using Surrogate Key.
============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES
)

from pyspark.sql.window import Window

from pyspark.sql.functions import (
    row_number,
    col
)

TARGET_TABLE = "gold.dim_customers"


def load_dim_customers(spark):
    """
    Load Customer Dimension into Gold Layer.
    """

    # ======================================================
    # Step 1 : Read Silver Table
    # ======================================================

    customers_df = (
        spark.read
        .jdbc(
            url=DB_URL,
            table="silver.customers",
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 2 : Remove Duplicates
    # ======================================================

    customers_df = customers_df.dropDuplicates(
        ["customer_id"]
    )

    # ======================================================
    # Step 3 : Generate Surrogate Key
    # ======================================================

    window_spec = Window.orderBy(
        col("customer_id")
    )

    dim_customer_df = (

        customers_df

        .withColumn(

            "customer_key",

            row_number().over(window_spec)

        )

        .select(

            "customer_key",

            "customer_id",

            "customer_unique_id",

            "customer_zip_code_prefix",

            "customer_city",

            "customer_state",

            "create_date",

            "update_date",

            "source_system"

        )

    )

    # ======================================================
    # Step 4 : Write Gold Table
    # ======================================================

    (
        dim_customer_df.write
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
    print(f"Rows  : {dim_customer_df.count()}")
    print("=" * 60)