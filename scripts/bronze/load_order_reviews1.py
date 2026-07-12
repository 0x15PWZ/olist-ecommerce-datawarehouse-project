
"""
============================================================
Bronze Layer

Load Order Reviews Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Order Reviews PySpark Schema

from scripts.schemas.order_reviews_schema import order_reviews_schema
def load_order_review(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_order_reviews_dataset.csv",
        table_name="bronze.order_reviews",
        schema=order_reviews_schema
    )