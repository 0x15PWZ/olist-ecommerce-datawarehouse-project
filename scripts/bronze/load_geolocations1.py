
"""
============================================================
Bronze Layer

Load Geolocation Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Geolocation PySpark Schema

from scripts.schemas.geolocation_schema import geolocation_schema
def load_geolocation(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_geolocation_dataset.csv",
        table_name="bronze.geolocation",
        schema=geolocation_schema
    )
