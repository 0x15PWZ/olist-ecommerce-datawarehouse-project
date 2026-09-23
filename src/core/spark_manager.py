"""
============================================================
Core
Spark Manager
------------------------------------------------------------
Purpose
------------------------------------------------------------
Create and manage the SparkSession used by the pipeline.

Responsibilities
------------------------------------------------------------
1. Configure Hadoop for Windows
2. Locate PostgreSQL JDBC Driver
3. Create SparkSession
4. Display Spark information
5. Stop SparkSession
============================================================
"""

import os
from pathlib import Path

from pyspark.sql import SparkSession


class SparkManager:

    def __init__(self, app_name: str = "OlistDataWarehouse"):
        self.app_name = app_name
        self.spark = None

    def create_session(self) -> SparkSession:
        """
        Create and return a configured SparkSession.

        Returns
        -------
        SparkSession
            Configured SparkSession.
        """

        if self.spark is None:

            # ==================================================
            # Configure Hadoop (Windows)
            # ==================================================

            os.environ["HADOOP_HOME"] = r"C:\hadoop"
            os.environ["hadoop.home.dir"] = r"C:\hadoop"

            # ==================================================
            # Locate PostgreSQL JDBC Driver
            # ==================================================

            project_root = Path(__file__).resolve().parents[2]

            postgres_jar = (
                project_root
                / "jars"
                / "postgresql-42.7.3.jar"
            )

            # ==================================================
            # Verify JDBC Driver
            # ==================================================

            if not postgres_jar.exists():
                raise FileNotFoundError(
                    f"PostgreSQL JDBC Driver not found:\n"
                    f"{postgres_jar}"
                )

            # ==================================================
            # Create SparkSession
            # ==================================================

            print("=" * 60)
            print("Spark Session")
            print("=" * 60)
            print(f"Application          : {self.app_name}")
            print(f"PostgreSQL JDBC JAR  : {postgres_jar}")
            print(f"HADOOP_HOME          : {os.environ['HADOOP_HOME']}")
            print("=" * 60)

            self.spark = (
                SparkSession.builder
                .appName(self.app_name)
                .config(
                    "spark.jars",
                    str(postgres_jar)
                )
                .getOrCreate()
            )

            # ==================================================
            # Display Spark Information
            # ==================================================

            print("=" * 60)
            print("Spark Session Created Successfully")
            print("=" * 60)
            print(f"Spark Version : {self.spark.version}")
            print(f"JDBC Driver   : {postgres_jar}")
            print("=" * 60)

        return self.spark

    def stop(self):
        """
        Stop the SparkSession.
        """

        if self.spark is not None:
            self.spark.stop()
            self.spark = None