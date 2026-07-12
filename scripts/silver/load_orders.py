"""
============================================================
Silver Layer

Load Orders

Purpose
------------------------------------------------------------
Load Bronze Orders into Silver Orders.

Process
------------------------------------------------------------
1. Read bronze.orders
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.orders
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.orders import transform_orders

def load_orders(spark):
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
        bronze_table="bronze.orders",
        silver_table="silver.orders",
        transform_function=transform_orders,
        source_system="OLIST_CSV",
        file_location="data/raw/olist_orders_dataset.csv"
    )