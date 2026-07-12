"""
============================================================
Silver Layer

Load Products

Purpose
------------------------------------------------------------
Load Bronze Products into Silver Products.

Process
------------------------------------------------------------
1. Read bronze.products
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.products
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.products import transform_products

def load_product(spark):
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
        bronze_table="bronze.products",
        silver_table="silver.products",
        transform_function=transform_products,
        source_system="OLIST_CSV",
        file_location="data/raw/olist_products_dataset.csv"
    )