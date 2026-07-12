"""
============================================================
Silver Layer

Load Geolocation

Purpose
------------------------------------------------------------
Load Bronze Geolocation into Silver Geolocation.

Process
------------------------------------------------------------
1. Read bronze.geolocation
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.geolocation
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.geolocation import transform_geolocation

def load_geolocations(spark):
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
        bronze_table="bronze.geolocation",
        silver_table="silver.geolocation",
        transform_function=transform_geolocation,
        source_system="OLIST_CSV",
        file_location="data/raw/olist_geolocation_dataset.csv"
    )