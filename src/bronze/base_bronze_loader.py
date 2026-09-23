"""
============================================================
Bronze Layer
Base Bronze Loader
------------------------------------------------------------
Purpose
------------------------------------------------------------
Provide reusable CSV-to-PostgreSQL Bronze loading logic.

ETL Process
------------------------------------------------------------
1. Validate CSV file
2. Read CSV using PySpark
3. Preview data
4. Display schema
5. Count CSV rows
6. Check if table exists
7. Truncate table if it exists
8. Write data to PostgreSQL
9. Validate row count
============================================================
"""

import os

from src.core.base_loader import BaseLoader


class BaseBronzeLoader(BaseLoader):
    """
    Generic Bronze Layer Loader.

    Child classes only need to provide:
        - CSV_FILE
        - TARGET_TABLE
        - SCHEMA
    """

    LAYER = "Bronze"

    CSV_FILE = None
    TARGET_TABLE = None
    SCHEMA = None

    def __init__(self, spark, database_manager):
        super().__init__(
            spark=spark,
            database_manager=database_manager
        )

    def load(self):

        self._validate_configuration()

        self.log_start(
            layer=self.LAYER,
            table_name=self.TARGET_TABLE
        )

        print(f"CSV File          : {self.CSV_FILE}")
        print(f"Destination Table : {self.TARGET_TABLE}")
        print("=" * 60)

        # --------------------------------------------------
        # 1. Build CSV path
        # --------------------------------------------------
        csv_path = self._get_csv_path()

        # --------------------------------------------------
        # 2. Validate CSV
        # --------------------------------------------------
        self._validate_csv(csv_path)

        # --------------------------------------------------
        # 3. Read CSV
        # --------------------------------------------------
        df = self._read_csv(csv_path)

        # --------------------------------------------------
        # 4. Preview
        # --------------------------------------------------
        print("\nFirst 5 Records")
        df.show(5, truncate=False)

        print("\nData Schema")
        df.printSchema()

        # --------------------------------------------------
        # 5. Count CSV rows
        # --------------------------------------------------
        csv_count = df.count()

        print(f"\nCSV Row Count : {csv_count}")

        # --------------------------------------------------
        # 6. Prepare target table
        # --------------------------------------------------
        self._prepare_target_table()

        # --------------------------------------------------
        # 7. Write to PostgreSQL
        # --------------------------------------------------
        self._write_to_database(df)

        # --------------------------------------------------
        # 8. Validate row count
        # --------------------------------------------------
        db_count = self._get_database_row_count()

        print(f"\nDatabase Row Count : {db_count}")

        self._validate_row_count(
            csv_count=csv_count,
            db_count=db_count
        )

        self.log_complete(
            layer=self.LAYER,
            table_name=self.TARGET_TABLE,
            row_count=db_count
        )

        return df

    # ======================================================
    # Configuration
    # ======================================================

    def _validate_configuration(self):

        if not self.CSV_FILE:
            raise ValueError(
                "CSV_FILE is not configured."
            )

        if not self.TARGET_TABLE:
            raise ValueError(
                "TARGET_TABLE is not configured."
            )

        if self.SCHEMA is None:
            raise ValueError(
                "SCHEMA is not configured."
            )

    # ======================================================
    # File Handling
    # ======================================================

    def _get_csv_path(self):

        csv_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../data/raw",
                self.CSV_FILE
            )
        )

        return csv_path

    def _validate_csv(self, csv_path):

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"CSV file not found:\n{csv_path}"
            )

        print(f"CSV Found : {csv_path}")

    # ======================================================
    # CSV Reading
    # ======================================================

    def _read_csv(self, csv_path):

        print("\nReading CSV...")

        return (
            self.spark.read
            .option("header", True)
            .option("inferSchema", True)
            .option("multiLine", True)
            .option("quote", '"')
            .option("escape", '"')
            .option("encoding", "UTF-8")
            .schema(self.SCHEMA)
            .csv(csv_path)
        )

    # ======================================================
    # PostgreSQL Preparation
    # ======================================================

    def _prepare_target_table(self):

        schema_name, table_name = (
            self.TARGET_TABLE.split(".", 1)
        )

        if self.db.table_exists(
            f"{schema_name}.{table_name}"
        ):
            print(
                f"\nTable {self.TARGET_TABLE} exists."
            )

            print("Truncating table...")

            self.db.execute_sql(
                f"""
                TRUNCATE TABLE {self.TARGET_TABLE};
                """
            )

            print(
                "Table truncated successfully."
            )

        else:

            print(
                f"\nTable {self.TARGET_TABLE} "
                "does not exist."
            )

            print(
                "Spark will create the table automatically."
            )

    # ======================================================
    # Database Write
    # ======================================================

    def _write_to_database(self, df):

        print(
            "\nWriting DataFrame to PostgreSQL..."
        )

        self.db.write_table(
            dataframe=df,
            table_name=self.TARGET_TABLE,
            mode="append"
        )

        print(
            "Data loaded successfully."
        )

    # ======================================================
    # Validation
    # ======================================================

    def _get_database_row_count(self):

        result = self.db.fetch_one(
            f"""
            SELECT COUNT(*)
            FROM {self.TARGET_TABLE};
            """
        )

        return result[0]

    def _validate_row_count(
        self,
        csv_count,
        db_count
    ):

        print("\nValidating Row Count...")

        if csv_count != db_count:

            raise Exception(
                f"""
Row count validation failed.

CSV Rows      : {csv_count}
Database Rows : {db_count}
"""
            )

        print("=" * 60)
        print("SUCCESS")
        print("=" * 60)
        print(f"CSV Rows      : {csv_count}")
        print(f"Database Rows : {db_count}")
        print("Row count validation passed.")
        print("=" * 60)