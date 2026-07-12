"""
============================================================
Silver Layer

Product Category Name Translation Transformation

Purpose
------------------------------------------------------------
Transform Bronze Product Category Name Translation
into Silver Product Category Name Translation.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty product_category_name
2. Remove duplicate product_category_name
3. Trim string columns
4. Convert to uppercase
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


def transform_product_category_name_translation(df):
    """
    Transform Bronze Product Category Name Translation
    into Silver Product Category Name Translation.

    Parameters
    ----------
    df : DataFrame
        Bronze product category translation DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver product category translation DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove NULL / Empty Business Key
    # ==========================================================

    df = df.filter(
        (col("product_category_name").isNotNull()) &
        (trim(col("product_category_name")) != "")
    )

    # ==========================================================
    # Rule 2
    # Remove Duplicate Categories
    # Keep populated English translation
    # ==========================================================

    window_spec = (
        Window
        .partitionBy(
            upper(trim(col("product_category_name")))
        )
        .orderBy(
            col("product_category_name_english").desc_nulls_last()
        )
    )

    df = (
        df
        .withColumn(
            "row_num",
            row_number().over(window_spec)
        )
        .filter(
            col("row_num") == 1
        )
        .drop("row_num")
    )

    # ==========================================================
    # Rule 3
    # Trim String Columns
    # ==========================================================

    df = (
        df
        .withColumn(
            "product_category_name",
            trim(col("product_category_name"))
        )
        .withColumn(
            "product_category_name_english",
            trim(col("product_category_name_english"))
        )
    )

    # ==========================================================
    # Rule 4
    # Convert to Uppercase
    # ==========================================================

    df = (
        df
        .withColumn(
            "product_category_name",
            upper(col("product_category_name"))
        )
        .withColumn(
            "product_category_name_english",
            upper(col("product_category_name_english"))
        )
    )

    # ==========================================================
    # Rule 5
    # Limit VARCHAR Length
    # ==========================================================

    df = (
        df
        .withColumn(
            "product_category_name",
            substring(
                col("product_category_name"),
                1,
                50
            )
        )
        .withColumn(
            "product_category_name_english",
            substring(
                col("product_category_name_english"),
                1,
                50
            )
        )
    )

    # ==========================================================
    # Return Transformed DataFrame
    # ==========================================================

    return df