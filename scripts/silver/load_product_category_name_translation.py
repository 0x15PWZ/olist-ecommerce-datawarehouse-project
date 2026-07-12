"""
============================================================
Silver Layer

Load Product Category Name Translation

Purpose
------------------------------------------------------------
Load Bronze Product Category Name Translation into Silver Product Category Name Translation.

Process
------------------------------------------------------------
1. Read bronze.product_category_name_translation
2. Apply business transformations
3. Add ETL metadata
4. Write to silver.product_category_name_translation
5. Validate row count

============================================================
"""
from scripts.silver.silver_loader import load_bronze_to_silver
from scripts.transformations.product_category_name_translation import transform_product_category_name_translation

def load_product_category_name_translations(spark):
    """
    Execute the Silver Orders ETL process.

    Parameters
    ----------
    spark : SparkSession
        Active Spark session.
    """
    # ==========================================================
    # Execute Generic Silver Loader
    # ==========================================================

    load_bronze_to_silver(
        spark=spark,
        bronze_table="bronze.product_category_name_translation",
        silver_table="silver.product_category_name_translation",
        transform_function=transform_product_category_name_translation,
        source_system="OLIST_CSV",
        file_location="data/raw/product_category_name_translation_dataset.csv"
    )