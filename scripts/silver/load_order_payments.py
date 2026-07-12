"""
============================================================
Silver Layer

Load Order Payments

Purpose
------------------------------------------------------------
Load Bronze Order Payments into Silver Order Payments.

Process
------------------------------------------------------------
1. Read bronze.order_payments
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.order_payments
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.order_payments import transform_order_payments

def load_order_payment(spark):
    """
    Execute the Silver Orders ETL process.

    Parameters
    ----------
    spark : SparkSession
        Active Spark session.
    """
    # ==========================================================
    # Execute Generic Silver Loader
    # ==========================================================

    load_bronze_to_silver(
        spark=spark,
        bronze_table="bronze.order_payments",
        silver_table="silver.order_payments",
        transform_function=transform_order_payments,
        source_system="OLIST_CSV",
        file_location="data/raw/olist_order_payments_dataset.csv"
    )