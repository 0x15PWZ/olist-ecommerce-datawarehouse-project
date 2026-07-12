"""
============================================================
Bronze Layer Generic Loader

Reusable function for loading CSV files into
PostgreSQL Bronze tables.

ETL Process
------------------------------------------------------------
1. Validate CSV file
2. Read CSV using predefined PySpark schema
3. Preview data
4. Display schema
5. Count CSV rows
6. Check if table exists
7. Truncate table (if exists)
8. Write data to PostgreSQL
9. Validate row count
============================================================
"""

import os

# PostgreSQL JDBC configuration
from config.config import (
    JDBC_URL,
    DB_USER,
    DB_PASSWORD
)

# Database utility functions
from scripts.utils.databases import (
    execute_sql,
    fetch_one,
    table_exists
)


def load_csv_to_bronze(
    spark,
    csv_file: str,
    table_name: str,
    schema
):
    """
    Generic Bronze Layer Loader

    Parameters
    ----------
    spark : SparkSession
        Active Spark Session

    csv_file : str
        CSV filename

    table_name : str
        Destination PostgreSQL table
        Example:
            bronze.customers

    schema : StructType
        PySpark schema for the dataset
    """

    # ==========================================================
    # Display Job Information
    # ==========================================================

    print("=" * 60)
    print("Bronze Layer Loader")
    print("=" * 60)
    print(f"CSV File          : {csv_file}")
    print(f"Destination Table : {table_name}")
    print("=" * 60)

    # ==========================================================
    # Build CSV File Path
    # ==========================================================

    csv_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../data/raw",
            csv_file
        )
    )

    # ==========================================================
    # Validate CSV File
    # ==========================================================

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"CSV file not found:\n{csv_path}"
        )

    print(f"CSV Found : {csv_path}")

    # ==========================================================
    # Read CSV using predefined schema
    # ==========================================================

    print("\nReading CSV...")

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .option("multiLine", True)
        .option("quote", '"')
        .option("escape", '"')
        .option("encoding", "UTF-8")
        .csv(csv_path)
    )

    # ==========================================================
    # Preview Data
    # ==========================================================

    print("\nFirst 5 Records")

    df.show(5, truncate=False)

    print("\nData Schema")

    df.printSchema()

    # ==========================================================
    # Count CSV Rows
    # ==========================================================

    csv_count = df.count()

    print(f"\nCSV Row Count : {csv_count}")

    # ==========================================================
    # Check Table Exists
    # ==========================================================

    schema_name, table = table_name.split(".")

    if table_exists(schema_name, table):

        print(f"\nTable {table_name} exists.")

        print("Truncating table...")

        execute_sql(
            f"""
            TRUNCATE TABLE {table_name};
            """
        )

        print("Table truncated successfully.")

    else:

        print(f"\nTable {table_name} does not exist.")

        print("Spark will create the table automatically.")

    # ==========================================================
    # Write DataFrame into PostgreSQL
    # ==========================================================

    print("\nWriting DataFrame to PostgreSQL...")

    (
        df.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", table_name)
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )

    print("Data loaded successfully.")

    # ==========================================================
    # Validate Row Count
    # ==========================================================

    db_count = fetch_one(
        f"""
        SELECT COUNT(*)
        FROM {table_name};
        """
    )[0]

    print(f"\nDatabase Row Count : {db_count}")

    # ==========================================================
    # Compare Row Counts
    # ==========================================================

    print("\nValidating Row Count...")

    if csv_count == db_count:

        print("=" * 60)
        print("SUCCESS")
        print("=" * 60)
        print(f"CSV Rows      : {csv_count}")
        print(f"Database Rows : {db_count}")
        print("Row count validation passed.")
        print("=" * 60)

    else:

        raise Exception(
            f"""
Row count validation failed.

CSV Rows      : {csv_count}

Database Rows : {db_count}
"""
        )