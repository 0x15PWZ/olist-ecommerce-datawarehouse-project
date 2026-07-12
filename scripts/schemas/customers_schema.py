# This is DDL script for PySpark 

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType
)

customers_schema = StructType([
    StructField("customer_id", StringType(), True),
    StructField("customer_unique_id", StringType(), True),
    StructField("customer_zip_code_prefix", IntegerType(), True),
    StructField("customer_city", StringType(), True),
    StructField("customer_state", StringType(), True)
])