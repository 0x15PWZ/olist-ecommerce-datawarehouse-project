"""
============================================================
Core
Database Manager
------------------------------------------------------------
Purpose
------------------------------------------------------------
Centralize PostgreSQL database operations.
============================================================
"""

from pyspark.sql import DataFrame

from scripts.utils.databases import (
    execute_sql as legacy_execute_sql,
    fetch_one as legacy_fetch_one,
    table_exists as legacy_table_exists
)


class DatabaseManager:

    def __init__(
        self,
        spark,
        db_url,
        db_properties
    ):

        self.spark = spark
        self.db_url = db_url
        self.db_properties = db_properties

    # ======================================================
    # Spark JDBC
    # ======================================================

    def read_table(
        self,
        table_name: str
    ) -> DataFrame:

        return self.spark.read.jdbc(
            url=self.db_url,
            table=table_name,
            properties=self.db_properties
        )

    def write_table(
        self,
        dataframe: DataFrame,
        table_name: str,
        mode: str = "overwrite"
    ):

        dataframe.write.jdbc(
            url=self.db_url,
            table=table_name,
            mode=mode,
            properties=self.db_properties
        )

    # ======================================================
    # PostgreSQL Utilities
    # ======================================================

    def table_exists(
        self,
        table_name: str
    ) -> bool:

        schema_name, table = table_name.split(".", 1)

        return legacy_table_exists(
            schema_name,
            table
        )

    def execute_sql(
        self,
        sql: str
    ):

        return legacy_execute_sql(sql)

    def fetch_one(
        self,
        sql: str
    ):

        return legacy_fetch_one(sql)