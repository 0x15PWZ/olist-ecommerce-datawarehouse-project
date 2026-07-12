"""
============================================================
Silver Layer

Orders Transformation

Purpose
------------------------------------------------------------
Transform Bronze orders data into clean and
standardized Silver Customers data.

Business Rules
------------------------------------------------------------
1. Remove NULL or empty order_id
2. Remove duplicate order_id (keep latest purchase timestamp)
3. Trim string columns
4. Convert order_status to uppercase
5. Standardize timestamp columns
6. Validate timestamp sequence
7. Limit varchar lengths

============================================================
"""
from pyspark.sql.window import Window
from pyspark.sql.functions import to_timestamp
from pyspark.sql.functions import when, lit
from pyspark.sql.functions import (
    col,
    trim,
    upper,
    row_number,
    substring
)


def transform_orders(df):

    # 1. Remove NULL or empty order_id
    df = df.filter(
    (col("order_id").isNotNull()) &
    (trim(col("order_id")) != "")
    )

    # 2. Remove duplicate order_id (keep latest purchase timestamp)
    window_spec = Window.partitionBy(
        "order_id"
    ).orderBy(
        col("order_purchase_timestamp").desc_nulls_last()
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

    # 3. Trim string columns
    df = (
    df
    .withColumn("order_id", trim(col("order_id")))
    .withColumn("customer_id", trim(col("customer_id")))
    .withColumn("order_status", trim(col("order_status")))
    )

    # 4. Convert order_status to uppercase

    df = df.withColumn("order_status", upper(col("order_status")))

    # 5. Standardize timestamp columns
    df = (
        df
        .withColumn(
            "order_purchase_timestamp",
            to_timestamp(col("order_purchase_timestamp"))
        )
        .withColumn(
            "order_approved_at",
            to_timestamp(col("order_approved_at"))
        )
        .withColumn(
            "order_delivered_carrier_date",
            to_timestamp(col("order_delivered_carrier_date"))
        )
        .withColumn(
            "order_delivered_customer_date",
            to_timestamp(col("order_delivered_customer_date"))
        )
        .withColumn(
            "order_estimated_delivery_date",
            to_timestamp(col("order_estimated_delivery_date"))
        )
    )

    # 6. Validate timestamp sequence

    df = df.withColumn(
        "is_valid_timestamp",
        when(
            col("order_approved_at").isNull(),
            lit(True)
        ).otherwise(
            col("order_approved_at") >= col("order_purchase_timestamp")
        )
    )

    # 7. Limit varchar lengths
    df = (
        df
        .withColumn(
            "order_id",
            substring(col("order_id"), 1, 50)
        )
        .withColumn(
            "customer_id",
            substring(col("customer_id"), 1, 50)
        )
        .withColumn(
            "order_status",
            substring(col("order_status"), 1, 50)
        )
    ) 

    return df