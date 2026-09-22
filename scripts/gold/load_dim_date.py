"""
============================================================
Gold Layer

Dimension : Date

Source
------------------------------------------------------------
silver.orders

Target
------------------------------------------------------------
gold.dim_date

Purpose
------------------------------------------------------------
Generate Date Dimension from all order lifecycle dates.

Date Columns
------------------------------------------------------------
1. order_purchase_timestamp
2. order_approved_at
3. order_delivered_carrier_date
4. order_delivered_customer_date
5. order_estimated_delivery_date

============================================================
"""

from config.config import (
    DB_URL,
    DB_PROPERTIES,
)

from pyspark.sql.functions import (
    col,
    year,
    month,
    dayofmonth,
    quarter,
    weekofyear,
    date_format,
    dayofweek,
    when,
    sequence,
    explode,
    to_date,
    lit,
    min,
    max,
    greatest,
    least,
    date_add,
)


TARGET_TABLE = "gold.dim_date"

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def load_dim_date(spark):

    # ======================================================
    # Step 1
    # Read Silver Orders
    # ======================================================

    orders_df = (
        spark.read
        .jdbc(
            url=DB_URL,
            table="silver.orders",
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 2
    # Determine Date Range
    #
    # Use ALL order lifecycle dates.
    # ======================================================

    orders_with_dates = (
        orders_df
        .withColumn(
            "_min_order_date",
            least(
                *[
                    to_date(col(column))
                    for column in DATE_COLUMNS
                ]
            )
        )
        .withColumn(
            "_max_order_date",
            greatest(
                *[
                    to_date(col(column))
                    for column in DATE_COLUMNS
                ]
            )
        )
    )

    # ======================================================
    # Step 3
    # Find Global Minimum Date
    # ======================================================

    min_date = (
        orders_with_dates
        .select(
            min("_min_order_date")
            .alias("min_date")
        )
        .first()["min_date"]
    )

    # ======================================================
    # Step 4
    # Find Global Maximum Date
    # ======================================================

    max_date = (
        orders_with_dates
        .select(
            max("_max_order_date")
            .alias("max_date")
        )
        .first()["max_date"]
    )

    # ======================================================
    # Step 5
    # Validate Date Range
    # ======================================================

    if min_date is None or max_date is None:

        raise ValueError(
            "Unable to determine date range "
            "from silver.orders."
        )

    print("=" * 60)
    print("Date Dimension Range")
    print(f"Minimum Date : {min_date}")
    print(f"Maximum Date : {max_date}")
    print("=" * 60)

    # ======================================================
    # Step 6
    # Generate Every Date
    # ======================================================

    dates_df = (

        spark.range(1)

        .select(
            explode(
                sequence(
                    to_date(lit(str(min_date))),
                    to_date(lit(str(max_date))),
                    lit(1).cast("interval day")
                )
            ).alias("full_date")
        )

    )

    # ======================================================
    # Step 7
    # Build Date Dimension
    # ======================================================

    dim_date_df = (

        dates_df

        # --------------------------------------------------
        # Date Key
        # --------------------------------------------------

        .withColumn(
            "date_key",
            date_format(
                "full_date",
                "yyyyMMdd"
            ).cast("int")
        )

        # --------------------------------------------------
        # Year
        # --------------------------------------------------

        .withColumn(
            "year",
            year("full_date")
        )

        # --------------------------------------------------
        # Quarter
        # --------------------------------------------------

        .withColumn(
            "quarter",
            quarter("full_date")
        )

        # --------------------------------------------------
        # Month
        # --------------------------------------------------

        .withColumn(
            "month",
            month("full_date")
        )

        # --------------------------------------------------
        # Month Name
        # --------------------------------------------------

        .withColumn(
            "month_name",
            date_format(
                "full_date",
                "MMMM"
            )
        )

        # --------------------------------------------------
        # Week of Year
        # --------------------------------------------------

        .withColumn(
            "week_of_year",
            weekofyear("full_date")
        )

        # --------------------------------------------------
        # Day
        # --------------------------------------------------

        .withColumn(
            "day",
            dayofmonth("full_date")
        )

        # --------------------------------------------------
        # Day Name
        # --------------------------------------------------

        .withColumn(
            "day_name",
            date_format(
                "full_date",
                "EEEE"
            )
        )

        # --------------------------------------------------
        # Day of Week
        # --------------------------------------------------

        .withColumn(
            "day_of_week",
            dayofweek("full_date")
        )

        # --------------------------------------------------
        # Weekend Flag
        # --------------------------------------------------

        .withColumn(
            "is_weekend",
            when(
                dayofweek("full_date").isin(1, 7),
                True
            ).otherwise(False)
        )

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        .withColumn(
            "create_date",
            lit(None).cast("timestamp")
        )

        .withColumn(
            "update_date",
            lit(None).cast("timestamp")
        )

        .withColumn(
            "source_system",
            lit("SYSTEM")
        )

    )

    # ======================================================
    # Step 8
    # Select Final Column Order
    # ======================================================

    dim_date_df = dim_date_df.select(
        "date_key",
        "full_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "week_of_year",
        "day",
        "day_name",
        "day_of_week",
        "is_weekend",
        "create_date",
        "update_date",
        "source_system",
    )

    # ======================================================
    # Step 9
    # Write Gold Table
    # ======================================================

    (
        dim_date_df.write
        .mode("overwrite")
        .jdbc(
            url=DB_URL,
            table=TARGET_TABLE,
            properties=DB_PROPERTIES
        )
    )

    # ======================================================
    # Step 10
    # Logging
    # ======================================================

    row_count = dim_date_df.count()

    print("=" * 60)
    print("Gold Dimension Loaded")
    print(f"Table : {TARGET_TABLE}")
    print(f"Rows  : {row_count}")
    print(f"From  : {min_date}")
    print(f"To    : {max_date}")
    print("=" * 60)