"""
============================================================
Silver Layer

Load Order Items

Purpose
------------------------------------------------------------
Load Bronze Order Items into Silver Order Items.

Process
------------------------------------------------------------
1. Read bronze.order_items
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.order_items
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.order_items import transform_order_items

def load_order_item(spark):
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
        bronze_table="bronze.order_items",
        silver_table="silver.order_items",
        transform_function=transform_order_items,
        source_system="OLIST_CSV",
        file_location="data/raw/olist_order_items_dataset.csv"
    )