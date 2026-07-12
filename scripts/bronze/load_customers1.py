"""
============================================================
Bronze Layer

Load Customers Dataset

ETL Process
------------------------------------------------------------
1. Read CSV using predefined PySpark schema
2. Validate CSV
3. Create Bronze table (first run only)
4. Truncate Bronze table (if already exists)
5. Load data into PostgreSQL
6. Verify row count
============================================================
"""

# Generic Bronze Loader
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Customers PySpark Schema
from scripts.schemas.customers_schema import customers_schema


def load_customer(spark):
    """
    Load the Olist Customers dataset into the Bronze layer.
    """

    load_csv_to_bronze(
        spark=spark,
        csv_file="olist_customers_dataset.csv",
        table_name="bronze.customers",
        schema=customers_schema
    )