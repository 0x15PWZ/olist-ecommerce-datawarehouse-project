"""
============================================================
Silver Layer

Products Transformation

Purpose
------------------------------------------------------------
Transform Bronze Products into
Silver Products.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty product_id
2. Remove duplicate product_id
3. Trim string columns
4. Convert product_category_name to uppercase
5. Limit VARCHAR column lengths
6. Cast numeric columns
7. Rename misspelled columns

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


def transform_products(df):
    """
    Transform Bronze Products into
    Silver Products.

    Parameters
    ----------
    df : DataFrame
        Bronze products DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver products DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove NULL / Empty Business Key
    # ==========================================================

    df = df.filter(
        (col("product_id").isNotNull()) &
        (trim(col("product_id")) != "")
    )

    # ==========================================================
    # Rule 2
    # Remove Duplicate Products
    # Keep populated category over NULL
    # ==========================================================

    window_spec = (
        Window
        .partitionBy(
            trim(col("product_id"))
        )
        .orderBy(
            col("product_category_name").desc_nulls_last()
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
            "product_id",
            trim(col("product_id"))
        )
        .withColumn(
            "product_category_name",
            trim(col("product_category_name"))
        )
    )

    # ==========================================================
    # Rule 4
    # Convert Category Name to Uppercase
    # ==========================================================

    df = (
        df
        .withColumn(
            "product_category_name",
            upper(col("product_category_name"))
        )
    )

    # ==========================================================
    # Rule 5
    # Limit VARCHAR Length
    # ==========================================================

    df = (
        df
        .withColumn(
            "product_id",
            substring(col("product_id"), 1, 50)
        )
        .withColumn(
            "product_category_name",
            substring(col("product_category_name"), 1, 100)
        )
    )

    # ==========================================================
    # Rule 6
    # Cast Integer Columns
    # ==========================================================

    df = (
        df
        .withColumn(
            "product_name_lenght",
            col("product_name_lenght").cast(
                IntegerType()
            )
        )
        .withColumn(
            "product_description_lenght",
            col("product_description_lenght").cast(
                IntegerType()
            )
        )
        .withColumn(
            "product_photos_qty",
            col("product_photos_qty").cast(
                IntegerType()
            )
        )
    )

    # ==========================================================
    # Rule 7
    # Cast Decimal Columns and set to Null
    # ==========================================================

    df = (
        df
        .withColumn(
            "product_weight_g",
            when(
                col("product_weight_g") <= 0,
                None
            ).otherwise(
                col("product_weight_g")
            )
        )
        .withColumn(
            "product_length_cm",
            when(
                col("product_length_cm") <= 0,
                None
            ).otherwise(
                col("product_length_cm")
            )
        )
        .withColumn(
            "product_height_cm",
            when(
                col("product_height_cm") <= 0,
                None
            ).otherwise(
                col("product_height_cm")
            )
        )
        .withColumn(
            "product_width_cm",
            when(
                col("product_width_cm") <= 0,
                None
            ).otherwise(
                col("product_width_cm")
            )
        )
    )


    # ==========================================================
    # Rule 8
    # Rename Columns
    # ==========================================================

    df = (
        df
        .withColumnRenamed(
            "product_name_lenght",
            "product_name_length"
        )
        .withColumnRenamed(
            "product_description_lenght",
            "product_description_length"
        )
    )

    # ==========================================================
    # Return DataFrame
    # ==========================================================

    return df