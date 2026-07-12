
"""
============================================================
Bronze Layer

Load Sellers Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Sellers PySpark Schema
from scripts.schemas.sellers_schema import sellers_schema
def load_seller(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_sellers_dataset.csv",
        table_name="bronze.sellers",
        schema=sellers_schema
    )