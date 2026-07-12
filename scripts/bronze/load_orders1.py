
"""
============================================================
Bronze Layer

Load Orders Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Orders PySpark Schema
from scripts.schemas.orders_schema import orders_schema

def load_order(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_orders_dataset.csv",
        table_name="bronze.orders",
        schema=orders_schema
    )