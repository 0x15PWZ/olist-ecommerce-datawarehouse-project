"""
============================================================
Bronze Layer
Customer Loader
------------------------------------------------------------
Purpose
------------------------------------------------------------
Load the Olist Customers dataset into:

    bronze.customers
============================================================
"""
from src.bronze.base_bronze_loader import BaseBronzeLoader
from scripts.schemas.customers_schema import customers_schema

class CustomerBronzeLoader(BaseBronzeLoader):

    CSV_FILE = "olist_customers_dataset.csv"
    TARGET_TABLE = "bronze.customers"
    SCHEMA = customers_schema