"""
============================================================
Core
Base Loader
------------------------------------------------------------
Purpose
------------------------------------------------------------
Provide common behavior for Bronze, Silver and Gold loaders.
============================================================
"""

from abc import ABC, abstractmethod


class BaseLoader(ABC):

    def __init__(self, spark, database_manager):
        self.spark = spark
        self.db = database_manager

    @abstractmethod
    def load(self):
        """
        Execute the loading process.

        Every concrete loader must implement this method.
        """
        pass

    def log_start(self, layer: str, table_name: str):
        print("=" * 60)
        print(f"{layer} Layer")
        print(f"Loading : {table_name}")
        print("=" * 60)

    def log_complete(self, layer: str, table_name: str, row_count: int):
        print("=" * 60)
        print(f"{layer} Load Complete")
        print(f"Table   : {table_name}")
        print(f"Rows    : {row_count}")
        print("=" * 60)