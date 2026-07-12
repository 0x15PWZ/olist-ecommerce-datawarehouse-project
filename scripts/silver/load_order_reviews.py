"""
============================================================
Silver Layer

Load Order Reviews

Purpose
------------------------------------------------------------
Load Bronze Order Reviews into Silver Order Reviews.

Process
------------------------------------------------------------
1. Read bronze.order_reviews
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.order_reviews
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.order_reviews import transform_order_reviews

def load_order_review(spark):
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
        bronze_table="bronze.order_reviews",
        silver_table="silver.order_reviews",
        transform_function=transform_order_reviews,
        source_system="OLIST_CSV",
        file_location="data/raw/olist_order_reviews_dataset.csv"
    )