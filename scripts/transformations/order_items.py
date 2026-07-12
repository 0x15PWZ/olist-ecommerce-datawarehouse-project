"""
============================================================
Silver Layer

Order Items Transformation

Purpose
------------------------------------------------------------
Transform Bronze Order Items into Silver Order Items.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty business keys
2. Remove duplicate records
3. Trim string columns
4. Limit VARCHAR column lengths
5. Cast financial columns
6. Cast shipping_limit_date to timestamp

============================================================
"""

from pyspark.sql.window import Window

from pyspark.sql.functions import (
    col,
    trim,
    row_number,
    substring,
    to_timestamp
)

from pyspark.sql.types import (
    DecimalType
)


def transform_order_items(df):
    """
    Transform Bronze Order Items into Silver Order Items.

    Parameters
    ----------
    df : DataFrame
        Bronze order_items DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver order_items DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove NULL / Empty Business Keys
    # ==========================================================

    df = df.filter(
        (col("order_id").isNotNull()) &
        (trim(col("order_id")) != "") &
        (col("order_item_id").isNotNull())
    )

    # ==========================================================
    # Rule 2
    # Remove Duplicate Records
    # Keep latest shipping_limit_date
    # ==========================================================

    window_spec = (
        Window
        .partitionBy(
            trim(col("order_id")),
            col("order_item_id")
        )
        .orderBy(
            col("shipping_limit_date").desc_nulls_last()
        )
    )

    df = (
        df
        .withColumn(
            "row_num",
            row_number().over(window_spec)
        )
        .filter(col("row_num") == 1)
        .drop("row_num")
    )

    # ==========================================================
    # Rule 3
    # Trim String Columns
    # ==========================================================

    df = (
        df
        .withColumn(
            "order_id",
            trim(col("order_id"))
        )
        .withColumn(
            "product_id",
            trim(col("product_id"))
        )
        .withColumn(
            "seller_id",
            trim(col("seller_id"))
        )
    )

    # ==========================================================
    # Rule 4
    # Limit VARCHAR Length
    # ==========================================================

    df = (
        df
        .withColumn(
            "order_id",
            substring(col("order_id"), 1, 50)
        )
        .withColumn(
            "product_id",
            substring(col("product_id"), 1, 50)
        )
        .withColumn(
            "seller_id",
            substring(col("seller_id"), 1, 50)
        )
    )

    # ==========================================================
    # Rule 5
    # Cast Financial Columns
    # ==========================================================

    df = (
        df
        .withColumn(
            "price",
            col("price").cast(
                DecimalType(10, 2)
            )
        )
        .withColumn(
            "freight_value",
            col("freight_value").cast(
                DecimalType(10, 2)
            )
        )
    )

    # ==========================================================
    # Rule 6
    # Cast Timestamp
    # ==========================================================

    TIMESTAMP_FORMAT = "yyyy-MM-dd HH:mm:ss"

    df = df.withColumn(
        "shipping_limit_date",
        to_timestamp(
            col("shipping_limit_date"),
            TIMESTAMP_FORMAT
        )
    )

    # ==========================================================
    # Return DataFrame
    # ==========================================================

    return df
