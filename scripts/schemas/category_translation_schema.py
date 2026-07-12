from pyspark.sql.types import (
    StructType,
    StructField,
    StringType
)

category_translation_schema = StructType([
    StructField("product_category_name", StringType(), True),
    StructField("product_category_name_english", StringType(), True)
])