"""
============================================================
Silver Layer

Order Payments Transformation

Purpose
------------------------------------------------------------
Transform Bronze Order Payments into
Silver Order Payments.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty business keys
2. Remove duplicate records
3. Trim string columns
4. Convert payment_type to uppercase
5. Limit VARCHAR column lengths
6. Cast payment_installments to Integer
7. Set installments to null when less than 0 or equal to 0
7. Cast payment_value to Decimal(10,2)

============================================================
"""

from pyspark.sql.window import Window

from pyspark.sql.functions import (
    col,
    trim,
    upper,
    row_number,
    substring,
    when
)

from pyspark.sql.types import (
    IntegerType,
    DecimalType
)


def transform_order_payments(df):
    """
    Transform Bronze Order Payments into
    Silver Order Payments.

    Parameters
    ----------
    df : DataFrame
        Bronze order_payments DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver order_payments DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove NULL / Empty Business Keys
    # ==========================================================

    df = df.filter(
        (col("order_id").isNotNull()) &
        (trim(col("order_id")) != "") &
        (col("payment_sequential").isNotNull())
    )

    # ==========================================================
    # Rule 2
    # Remove Duplicate Records
    # Keep Highest Payment Value
    # ==========================================================

    window_spec = (
        Window
        .partitionBy(
            trim(col("order_id")),
            col("payment_sequential")
        )
        .orderBy(
            col("payment_value").desc_nulls_last()
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
            "payment_type",
            trim(col("payment_type"))
        )
    )

    # ==========================================================
    # Rule 4
    # Convert Payment Type to Uppercase
    # ==========================================================

    df = (
        df
        .withColumn(
            "payment_type",
            upper(col("payment_type"))
        )
    )

    # ==========================================================
    # Rule 5
    # Limit VARCHAR Length
    # ==========================================================

    df = (
        df
        .withColumn(
            "order_id",
            substring(col("order_id"), 1, 50)
        )
        .withColumn(
            "payment_type",
            substring(col("payment_type"), 1, 50)
        )
    )

    # ==========================================================
    # Rule 6
    # Cast Installments
    # ==========================================================

    df = (
        df
        .withColumn(
            "payment_installments",
            col("payment_installments").cast(
                IntegerType()
            )
        )
    )
    # ==========================================================
    # Rule 7
    # Installments set to Null when 0 or less than 0
    # ==========================================================

    df = (
        df
        .withColumn(
            "payment_installments",
            when(
                col("payment_installments") <= 0,
                None
            ).otherwise(
                col("payment_installments")
            )
        )
    )

    # ==========================================================
    # Rule 8
    # Cast Payment Value
    # ==========================================================

    df = (
        df
        .withColumn(
            "payment_value",
            col("payment_value").cast(
                DecimalType(10, 2)
            )
        )
    )

    # ==========================================================
    # Return DataFrame
    # ==========================================================

    return df