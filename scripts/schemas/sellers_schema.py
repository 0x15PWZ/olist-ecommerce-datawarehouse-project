from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType
)

sellers_schema = StructType([
    StructField("seller_id", StringType(), True),
    StructField("seller_zip_code_prefix", IntegerType(), True),
    StructField("seller_city", StringType(), True),
    StructField("seller_state", StringType(), True)
])