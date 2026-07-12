"""
============================================================
Silver Layer

Load Customers

Purpose
------------------------------------------------------------
Load Customers data from the Bronze Layer
into the Silver Layer.

This module only configures the generic
Silver Loader.

Execution Flow
------------------------------------------------------------
1. Read Bronze customers table
2. Apply customer transformation
3. Add ETL metadata
4. Load into Silver customers table
5. Validate row count
============================================================
"""

from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.customers import transform_customers

def load_customer(spark):
    """
    Execute Customers Silver ETL.

    Parameters
    ----------
    spark : SparkSession
        Active Spark Session.
    """
    load_bronze_to_silver(
        spark=spark,

        bronze_table="bronze.customers",

        silver_table="silver.customers",

        transform_function=transform_customers,

        source_system="OLIST_CSV",

        file_location="data/raw/olist_customers_dataset.csv"
    ) 