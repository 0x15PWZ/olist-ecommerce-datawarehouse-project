
"""
============================================================
Bronze Layer

Load Products Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Products PySpark Schema
from scripts.schemas.products_schema import products_schema

def load_product(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_products_dataset.csv",
        table_name="bronze.products",
        schema=products_schema
    )