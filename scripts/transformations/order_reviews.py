"""
============================================================
Silver Layer

Order Reviews Transformation

Purpose
------------------------------------------------------------
Transform Bronze Order Reviews into
Silver Order Reviews.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty review_id
2. Remove duplicate review_id
3. Trim string columns
4. Convert review_comment_title to uppercase
5. Limit VARCHAR column lengths
6. Cast review_score to Integer
7. Cast review_creation_date to Date
8. Cast review_answer_timestamp to Timestamp

============================================================
"""

from pyspark.sql.window import Window

from pyspark.sql.functions import (
    col,
    trim,
    upper,
    row_number,
    substring,
    to_date,
    to_timestamp
)

from pyspark.sql.types import (
    IntegerType
)


def transform_order_reviews(df):
    """
    Transform Bronze Order Reviews into
    Silver Order Reviews.

    Parameters
    ----------
    df : DataFrame
        Bronze order_reviews DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver order_reviews DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove NULL / Empty Business Key
    # ==========================================================

    df = df.filter(
        (col("review_id").isNotNull()) &
        (trim(col("review_id")) != "")
    )

    # ==========================================================
    # Rule 2
    # Remove Duplicate Reviews
    # Keep Latest Review
    # ==========================================================

    window_spec = (
        Window
        .partitionBy(
            trim(col("review_id"))
        )
        .orderBy(
            col("review_answer_timestamp").desc_nulls_last()
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
            "review_id",
            trim(col("review_id"))
        )
        .withColumn(
            "order_id",
            trim(col("order_id"))
        )
        .withColumn(
            "review_comment_title",
            trim(col("review_comment_title"))
        )
        .withColumn(
            "review_comment_message",
            trim(col("review_comment_message"))
        )
    )

    # ==========================================================
    # Rule 4
    # Convert Review Title to Uppercase
    # ==========================================================

    df = (
        df
        .withColumn(
            "review_comment_title",
            upper(col("review_comment_title"))
        )
    )

    # ==========================================================
    # Rule 5
    # Limit VARCHAR Length
    # ==========================================================

    df = (
        df
        .withColumn(
            "review_id",
            substring(col("review_id"), 1, 50)
        )
        .withColumn(
            "order_id",
            substring(col("order_id"), 1, 50)
        )
        .withColumn(
            "review_comment_title",
            substring(col("review_comment_title"), 1, 50)
        )
    )

    # ==========================================================
    # Rule 6
    # Cast Review Score
    # ==========================================================

    df = (
        df
        .withColumn(
            "review_score",
            col("review_score").cast(
                IntegerType()
            )
        )
    )

    # ==========================================================
    # Rule 7
    # Cast Review Creation Date
    # ==========================================================

    DATE_FORMAT = "yyyy-MM-dd HH:mm:ss"

    df = (
        df
        .withColumn(
            "review_creation_date",
            to_date(
                col("review_creation_date"),
                DATE_FORMAT
            )
        )
    )

    # ==========================================================
    # Rule 8
    # Cast Review Answer Timestamp
    # ==========================================================

    TIMESTAMP_FORMAT = "yyyy-MM-dd HH:mm:ss"

    df = (
        df
        .withColumn(
            "review_answer_timestamp",
            to_timestamp(
                col("review_answer_timestamp"),
                TIMESTAMP_FORMAT
            )
        )
    )

    # ==========================================================
    # Return Transformed DataFrame
    # ==========================================================

    return df