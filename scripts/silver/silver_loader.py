"""
============================================================
Silver Layer Generic Loader

Purpose
------------------------------------------------------------
Reusable loader for moving data from the Bronze Layer
to the Silver Layer.

ETL Flow
------------------------------------------------------------
1. Read Bronze table
2. Apply business transformation
3. Add ETL metadata
4. Preview transformed data
5. Display schema
6. Count transformed rows
7. Check Silver table
8. Truncate table (if exists)
9. Write to PostgreSQL
10. Validate row count
11. Print execution summary
============================================================
"""

from pyspark.sql.functions import (
    current_timestamp,
    lit
)

from config.config import (
    JDBC_URL,
    DB_USER,
    DB_PASSWORD
)

from scripts.utils.databases import (
    execute_sql,
    fetch_one,
    table_exists
)


def load_bronze_to_silver(
    spark,
    bronze_table: str,
    silver_table: str,
    transform_function,
    source_system: str = "OLIST_CSV",
    file_location: str = ""
):
    """
    Generic Silver Layer Loader.

    Parameters
    ----------
    spark : SparkSession

    bronze_table : str
        Source Bronze table.

    silver_table : str
        Destination Silver table.

    transform_function : function
        Business transformation function.

    source_system : str
        Source system name.

    file_location : str
        Original source file location.
    """

    # ==========================================================
    # Display Job Information
    # ==========================================================

    print("=" * 60)
    print("Silver Layer Loader")
    print("=" * 60)
    print(f"Source Table      : {bronze_table}")
    print(f"Destination Table : {silver_table}")
    print("=" * 60)

    # ==========================================================
    # Read Bronze Table
    # ==========================================================

    print("\nReading Bronze table...")

    bronze_df = (
        spark.read
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", bronze_table)
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .load()
    )

    print("Bronze table loaded successfully.")

    # ==========================================================
    # Apply Business Transformation
    # ==========================================================

    print("\nApplying business transformations...")

    silver_df = transform_function(bronze_df)

    print("Transformation completed.")

    # ==========================================================
    # Add ETL Metadata
    # ==========================================================

    print("\nAdding ETL metadata...")

    silver_df = (
        silver_df
        .withColumn(
            "create_date",
            current_timestamp()
        )
        .withColumn(
            "update_date",
            current_timestamp()
        )
        .withColumn(
            "source_system",
            lit(source_system)
        )
        .withColumn(
            "file_location",
            lit(file_location)
        )
    )

    # ==========================================================
    # Preview Data
    # ==========================================================

    print("\nFirst 5 Records")

    silver_df.show(
        5,
        truncate=False
    )

    # ==========================================================
    # Print Schema
    # ==========================================================

    print("\nSchema")

    silver_df.printSchema()

    # ==========================================================
    # Count Rows
    # ==========================================================

    silver_count = silver_df.count()

    print(f"\nTransformed Rows : {silver_count}")

    # ==========================================================
    # Check Silver Table
    # ==========================================================

    schema_name, table_name = silver_table.split(".")

    if table_exists(schema_name, table_name):

        print("\nSilver table exists.")

        execute_sql(
            f"""
            TRUNCATE TABLE {silver_table};
            """
        )

        print("Table truncated successfully.")

    else:

        print("\nSilver table does not exist.")
        print("Spark will create it automatically.")

    # ==========================================================
    # Write to PostgreSQL
    # ==========================================================

    print("\nWriting data to PostgreSQL...")

    (
        silver_df.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", silver_table)
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )

    print("Write completed successfully.")

    # ==========================================================
    # Validate Row Count
    # ==========================================================

    db_count = fetch_one(
        f"""
        SELECT COUNT(*)
        FROM {silver_table};
        """
    )[0]

    print(f"Database Rows : {db_count}")

    # ==========================================================
    # Row Count Validation
    # ==========================================================

    if silver_count != db_count:

        raise Exception(
            f"""
Row count validation failed.

Silver Rows   : {silver_count}
Database Rows : {db_count}
"""
        )

    # ==========================================================
    # Execution Summary
    # ==========================================================

    print("\n" + "=" * 60)
    print("Silver Load Summary")
    print("=" * 60)
    print(f"Source Table      : {bronze_table}")
    print(f"Destination Table : {silver_table}")
    print(f"Rows Loaded       : {db_count}")
    print(f"Source System     : {source_system}")
    print(f"File Location     : {file_location}")
    print("Status            : SUCCESS")
    print("=" * 60)