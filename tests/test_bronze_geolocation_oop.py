"""
============================================================
Test
Geolocation Bronze OOP Loader
============================================================
"""

from config.config import (
    JDBC_URL,
    DB_PROPERTIES
)

from src.core.spark_manager import SparkManager
from src.core.database_manager import DatabaseManager
from src.bronze.loaders.geolocation_loader import (
    GeolocationBronzeLoader
)


def main():

    spark_manager = SparkManager(
        app_name="OlistGeolocationBronzeOOP"
    )

    spark = spark_manager.create_session()

    try:

        database_manager = DatabaseManager(
            spark=spark,
            db_url=JDBC_URL,
            db_properties=DB_PROPERTIES
        )

        loader = GeolocationBronzeLoader(
            spark=spark,
            database_manager=database_manager
        )

        loader.load()

    finally:

        spark_manager.stop()


if __name__ == "__main__":
    main()