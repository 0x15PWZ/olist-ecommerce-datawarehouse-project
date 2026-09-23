"""
============================================================
Bronze Layer
Geolocation Loader
------------------------------------------------------------
Purpose
------------------------------------------------------------
Load the Olist Geolocation dataset into:

    bronze.geolocations
============================================================
"""

from src.bronze.base_bronze_loader import BaseBronzeLoader

from scripts.schemas.geolocation_schema import geolocation_schema


class GeolocationBronzeLoader(BaseBronzeLoader):

    CSV_FILE = "olist_geolocation_dataset.csv"

    TARGET_TABLE = "bronze.geolocations"

    SCHEMA = geolocation_schema