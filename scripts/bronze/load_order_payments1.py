
"""
============================================================
Bronze Layer

Load Order Payments Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Order Payments PySpark Schema

from scripts.schemas.order_payments_schema import order_payments_schema
def load_order_payment(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_order_payments_dataset.csv",
        table_name="bronze.order_payments",
        schema=order_payments_schema
    )