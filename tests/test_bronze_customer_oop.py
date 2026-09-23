"""
============================================================
Test
Customer Bronze OOP Loader
============================================================
"""

from config.config import (
    JDBC_URL,
    DB_PROPERTIES
)

from src.core.spark_manager import SparkManager
from src.core.database_manager import DatabaseManager

from src.bronze.loaders.customer_loader import (
    CustomerBronzeLoader
)


def main():

    # ========================================================
    # 1. Create Spark Session
    # ========================================================

    spark_manager = SparkManager(
        app_name="OlistCustomerBronzeOOP"
    )

    spark = spark_manager.create_session()

    try:

        # ====================================================
        # 2. Create Database Manager
        # ====================================================

        database_manager = DatabaseManager(
            spark=spark,
            db_url=JDBC_URL,
            db_properties=DB_PROPERTIES
        )

        # ====================================================
        # 3. Create Customer Loader
        # ====================================================

        loader = CustomerBronzeLoader(
            spark=spark,
            database_manager=database_manager
        )

        # ====================================================
        # 4. Execute Bronze Load
        # ====================================================

        loader.load()

    finally:

        # ====================================================
        # 5. Always Stop Spark
        # ====================================================

        spark_manager.stop()


if __name__ == "__main__":
    main()