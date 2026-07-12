"""
============================================================
Silver Layer

Geolocation Transformation

Purpose
------------------------------------------------------------
Transform Bronze Geolocation into
Silver Geolocation.

Business Rules
------------------------------------------------------------
1. Remove exact duplicate rows
2. Trim city/state
3. Convert city/state to uppercase
4. Cast latitude and longitude to Double
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

from pyspark.sql.types import (
    DoubleType
)


def transform_geolocation(df):
    """
    Transform Bronze Geolocation into
    Silver Geolocation.

    Parameters
    ----------
    df : DataFrame
        Bronze geolocation DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver geolocation DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove Exact Duplicate Rows
    # ==========================================================

    window_spec = (
        Window
        .partitionBy(
            col("geolocation_zip_code_prefix"),
            col("geolocation_lat"),
            col("geolocation_lng"),
            upper(trim(col("geolocation_city"))),
            upper(trim(col("geolocation_state")))
        )
        .orderBy(
            col("geolocation_zip_code_prefix")
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
    # Rule 2
    # Trim String Columns
    # ==========================================================

    df = (
        df
        .withColumn(
            "geolocation_city",
            trim(col("geolocation_city"))
        )
        .withColumn(
            "geolocation_state",
            trim(col("geolocation_state"))
        )
    )

    # ==========================================================
    # Rule 3
    # Convert City / State to Uppercase
    # ==========================================================

    df = (
        df
        .withColumn(
            "geolocation_city",
            upper(col("geolocation_city"))
        )
        .withColumn(
            "geolocation_state",
            upper(col("geolocation_state"))
        )
    )

    # ==========================================================
    # Rule 4
    # Cast Latitude / Longitude
    # ==========================================================

    df = (
        df
        .withColumn(
            "geolocation_lat",
            col("geolocation_lat").cast(
                DoubleType()
            )
        )
        .withColumn(
            "geolocation_lng",
            col("geolocation_lng").cast(
                DoubleType()
            )
        )
    )

    # ==========================================================
    # Rule 5
    # Limit VARCHAR Length
    # ==========================================================

    df = (
        df
        .withColumn(
            "geolocation_city",
            substring(
                col("geolocation_city"),
                1,
                100
            )
        )
        .withColumn(
            "geolocation_state",
            substring(
                col("geolocation_state"),
                1,
                2
            )
        )
    )

    # ==========================================================
    # Return Transformed DataFrame
    # ==========================================================

    return df