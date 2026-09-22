"""
============================================================
Gold Layer

Dimension : Payment

Source
------------------------------------------------------------
silver.order_payments

Target
------------------------------------------------------------
gold.dim_payment

Purpose
------------------------------------------------------------
Create Payment Dimension using Surrogate Key.
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

TARGET_TABLE = "gold.dim_payment"


def load_dim_payment(spark):
    """
    Load Payment Dimension into Gold Layer.
    """

    # ======================================================
    # Step 1 : Read Silver Table
    # ======================================================

    payment_df = (
        spark.read
        .jdbc(
            url=DB_URL,
            table="silver.order_payments",
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 2 : Select Business Attributes
    # ======================================================

    payment_df = (

        payment_df

        .select(

            "payment_type",

            "payment_installments"

        )

        .dropDuplicates()

    )

    # ======================================================
    # Step 3 : Generate Surrogate Key
    # ======================================================

    window_spec = Window.orderBy(

        col("payment_type"),

        col("payment_installments")

    )

    dim_payment_df = (

        payment_df

        .withColumn(

            "payment_key",

            row_number().over(window_spec)

        )

        .select(

            "payment_key",

            "payment_type",

            "payment_installments"

        )

    )

    # ======================================================
    # Step 4 : Write Gold Table
    # ======================================================

    (
        dim_payment_df.write
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
    print(f"Rows  : {dim_payment_df.count()}")
    print("=" * 60)