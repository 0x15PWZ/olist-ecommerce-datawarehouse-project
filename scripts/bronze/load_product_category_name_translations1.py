
"""
============================================================
Bronze Layer

Load Product Category Name Translation Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""
from scripts.bronze.bronze_loader1 import load_csv_to_bronze

# Product Category Name Translation PySpark Schema

from scripts.schemas.category_translation_schema import category_translation_schema
def load_product_category_name_translation(spark):

    load_csv_to_bronze(
        spark=spark,
        csv_file="product_category_name_translation.csv",
        table_name="bronze.product_category_name_translation",
        schema=category_translation_schema
    )