
"""
============================================================
Bronze Layer

Load Order Items Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Order items PySpark Schema
from scripts.schemas.order_items_schema import order_items_schema

def load_order_item(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_order_items_dataset.csv",
        table_name="bronze.order_items",
        schema=order_items_schema
    )