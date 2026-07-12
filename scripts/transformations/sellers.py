"""
============================================================
Silver Layer

Sellers Transformation

Purpose
------------------------------------------------------------
Transform Bronze Sellers into
Silver Sellers.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty seller_id
2. Remove duplicate seller_id
3. Trim string columns
4. Convert city and state to uppercase
5. Limit VARCHAR column lengths

============================================================
"""

from pyspark.sql.window import Window

from pyspark.sql.functions import (
    col,
    trim,
    upper,
    row_number,
    substring
)


def transform_sellers(df):
    """
    Transform Bronze Sellers into
    Silver Sellers.

    Parameters
    ----------
    df : DataFrame
        Bronze sellers DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver sellers DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove NULL / Empty Business Key
    # ==========================================================

    df = df.filter(
        (col("seller_id").isNotNull()) &
        (trim(col("seller_id")) != "")
    )

    # ==========================================================
    # Rule 2
    # Remove Duplicate Sellers
    # Keep populated state over NULL
    # ==========================================================

    window_spec = (
        Window
        .partitionBy(
            trim(col("seller_id"))
        )
        .orderBy(
            col("seller_state").desc_nulls_last()
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
            "seller_id",
            trim(col("seller_id"))
        )
        .withColumn(
            "seller_city",
            trim(col("seller_city"))
        )
        .withColumn(
            "seller_state",
            trim(col("seller_state"))
        )
    )

    # ==========================================================
    # Rule 4
    # Convert City and State to Uppercase
    # ==========================================================

    df = (
        df
        .withColumn(
            "seller_city",
            upper(col("seller_city"))
        )
        .withColumn(
            "seller_state",
            upper(col("seller_state"))
        )
    )

    # ==========================================================
    # Rule 5
    # Limit VARCHAR Length
    # ==========================================================

    df = (
        df
        .withColumn(
            "seller_id",
            substring(col("seller_id"), 1, 50)
        )
        .withColumn(
            "seller_city",
            substring(col("seller_city"), 1, 100)
        )
        .withColumn(
            "seller_state",
            substring(col("seller_state"), 1, 2)
        )
    )

    # ==========================================================
    # Return Transformed DataFrame
    # ==========================================================

    return df