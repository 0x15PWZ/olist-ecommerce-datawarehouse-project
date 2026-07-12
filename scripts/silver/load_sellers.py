"""
============================================================
Silver Layer

Load Sellers

Purpose
------------------------------------------------------------
Load Bronze Sellers into Silver Sellers.

Process
------------------------------------------------------------
1. Read bronze.sellers
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.sellers
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.sellers import transform_sellers

def load_seller(spark):
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
        bronze_table="bronze.sellers",
        silver_table="silver.sellers",
        transform_function=transform_sellers,
        source_system="OLIST_CSV",
        file_location="data/raw/olist_sellers_dataset.csv"
    )