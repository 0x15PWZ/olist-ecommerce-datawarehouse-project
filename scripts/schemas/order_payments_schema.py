from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DecimalType
)

order_payments_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("payment_sequential", IntegerType(), True),
    StructField("payment_type", StringType(), True),
    StructField("payment_installments", IntegerType(), True),
    StructField("payment_value", DecimalType(10, 2), True)
])