"""
============================================================
Spark Session Utility

Purpose:
    Create and return a reusable SparkSession.

Responsibilities
------------------------------------------------------------
1. Configure Hadoop (Windows)
2. Configure PostgreSQL JDBC Driver
3. Create SparkSession
4. Display Spark information

Used by:
    - Bronze Layer
    - Silver Layer
    - Gold Layer
============================================================
"""

import os

from pyspark.sql import SparkSession


def create_spark_session():
    """
    Create and return a configured SparkSession.

    Returns
    -------
    SparkSession
        Spark session configured with the PostgreSQL JDBC driver.
    """

    # ==========================================================
    # Configure Hadoop (Windows Only)
    # ==========================================================

    os.environ["HADOOP_HOME"] = r"C:\hadoop"
    os.environ["hadoop.home.dir"] = r"C:\hadoop"

    # ==========================================================
    # Locate PostgreSQL JDBC Driver
    # ==========================================================

    jar_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../jars/postgresql-42.7.3.jar"
        )
    )

    # Verify the JDBC driver exists
    if not os.path.exists(jar_path):
        raise FileNotFoundError(
            f"PostgreSQL JDBC Driver not found:\n{jar_path}"
        )

    # ==========================================================
    # Create Spark Session
    # ==========================================================

    spark = (
        SparkSession.builder
        .appName("Olist Data Warehouse")
        .config("spark.jars", jar_path)
        .getOrCreate()
    )

    # ==========================================================
    # Display Spark Information
    # ==========================================================

    print("=" * 60)
    print("Spark Session Created Successfully")
    print("=" * 60)
    print(f"Spark Version : {spark.version}")
    print(f"JDBC Driver   : {jar_path}")
    print("=" * 60)

    return spark