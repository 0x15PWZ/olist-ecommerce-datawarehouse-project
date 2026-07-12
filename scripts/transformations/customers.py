"""
============================================================
Silver Layer

Customers Transformation

Purpose
------------------------------------------------------------
Transform Bronze Customers data into clean and
standardized Silver Customers data.

Business Rules
------------------------------------------------------------
1. Remove records with NULL customer_id
2. Remove duplicate customer_id
3. Trim leading/trailing whitespace
4. Convert city to uppercase
5. Convert state to uppercase
6. Replace NULL or empty city with 'UNKNOWN'
7. Replace NULL or empty state with 'UNKNOWN'
8. Limit customer_id to 50 characters
9. Limit customer_unique_id to 50 characters
10. Limit customer_city to 50 characters
11. Limit customer_state to 2 characters

============================================================
"""

from pyspark.sql.functions import (
    col,
    trim,
    upper,
    when,
    substring
)


def transform_customers(df):
    """
    Transform Bronze Customers DataFrame.

    Parameters
    ----------
    df : DataFrame
        Bronze customers DataFrame.

    Returns
    -------
    DataFrame
        Cleaned Silver customers DataFrame.
    """

    # ==========================================================
    # Rule 1
    # Remove records with NULL customer_id
    # ==========================================================

    df = df.filter(
        col("customer_id").isNotNull()
    )

    # ==========================================================
    # Rule 2
    # Remove duplicate customers
    # Business Key = customer_id
    # ==========================================================

    df = df.dropDuplicates(
        ["customer_id"]
    )

    # ==========================================================
    # Rule 3
    # Remove leading/trailing whitespace
    # ==========================================================

    df = (
        df
        .withColumn(
            "customer_id",
            trim(col("customer_id"))
        )
        .withColumn(
            "customer_unique_id",
            trim(col("customer_unique_id"))
        )
        .withColumn(
            "customer_city",
            trim(col("customer_city"))
        )
        .withColumn(
            "customer_state",
            trim(col("customer_state"))
        )
    )

    # ==========================================================
    # Rule 4
    # Convert city and state to uppercase
    # ==========================================================

    df = (
        df
        .withColumn(
            "customer_city",
            upper(col("customer_city"))
        )
        .withColumn(
            "customer_state",
            upper(col("customer_state"))
        )
    )

    # ==========================================================
    # Rule 5
    # Replace NULL or empty customer_city
    # ==========================================================

    df = (
        df
        .withColumn(
            "customer_city",
            when(
                (col("customer_city").isNull()) |
                (col("customer_city") == ""),
                "UNKNOWN"
            ).otherwise(
                col("customer_city")
            )
        )
    )

    # ==========================================================
    # Rule 6
    # Replace NULL or empty customer_state
    # ==========================================================

    df = (
        df
        .withColumn(
            "customer_state",
            when(
                (col("customer_state").isNull()) |
                (col("customer_state") == ""),
                "UNKNOWN"
            ).otherwise(
                col("customer_state")
            )
        )
    )

    # ==========================================================
    # Rule 7
    # Standardize maximum column lengths
    # ==========================================================

    df = (
        df
        .withColumn(
            "customer_id",
            substring(col("customer_id"), 1, 50)
        )
        .withColumn(
            "customer_unique_id",
            substring(col("customer_unique_id"), 1, 50)
        )
        .withColumn(
            "customer_city",
            substring(col("customer_city"), 1, 50)
        )
        .withColumn(
            "customer_state",
            substring(col("customer_state"), 1, 2)
        )
    )

    # ==========================================================
    # Return transformed DataFrame
    # ==========================================================

    return df