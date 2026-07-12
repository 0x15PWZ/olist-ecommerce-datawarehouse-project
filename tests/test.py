"""
============================================================
Bronze Layer

Load Customers Dataset

ETL Process

1. Read CSV
2. Validate CSV
3. Truncate Bronze Table
4. Load Data into PostgreSQL
5. Verify row count
============================================================
"""



def load_customer(spark):
    """
    Load Customers CSV into Bronze Layer.
    """

    print("=" * 60)
    print("Loading Customers Dataset...")
    print("=" * 60)

    # ---------------------------------------------------------
    # CSV File Path
    # ---------------------------------------------------------

    csv_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../data/raw/olist_customers_dataset.csv"
        )
    )

    # ---------------------------------------------------------
    # Validate File
    # ---------------------------------------------------------

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"CSV file not found:\n{csv_path}"
        )

    # ---------------------------------------------------------
    # Read CSV
    # ---------------------------------------------------------

    customers_df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(csv_path)
    )

    # ---------------------------------------------------------
    # Preview Data
    # ---------------------------------------------------------

    customers_df.show(5, truncate=False)

    customers_df.printSchema()

    # ---------------------------------------------------------
    # Truncate Bronze Table
    # ---------------------------------------------------------

    execute_sql(
        """
        TRUNCATE TABLE bronze.customers;
        """
    )

    print("bronze.customers truncated successfully.")

    # ---------------------------------------------------------
    # Write DataFrame to PostgreSQL
    # ---------------------------------------------------------
    print("=" * 60)
    print("Loading data into PostgreSQL...")
    print("=" * 60)

    customers_df.write \
        .format("jdbc") \
        .option("url", JDBC_URL) \
        .option("dbtable", "bronze.customers") \
        .option("user", DB_USER) \
        .option("password", DB_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

    print("Customers loaded successfully.")

    # ---------------------------------------------------------
    # Verify row count with PostgreSQL
    # ---------------------------------------------------------

    csv_count = customers_df.count()

    print("=" * 60)
    print(f"CSV Row Count: {csv_count}")
    print("=" * 60)

    db_count = fetch_one(
    """
    SELECT COUNT(*)
    FROM bronze.customers;
    """
    )[0]

    print("=" * 60)
    print(f"Database Row Count: {db_count}")
    print("=" * 60)


    if csv_count == db_count:
        print("=" * 60)
        print("SUCCESS: Data loaded correctly.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("ERROR: Row count mismatch.")
        print("=" * 60)


# =========================================================================
"""
============================================================
Main ETL Pipeline

Execution Order

1. Create Spark Session
2. Run Bronze Layer
3. Stop Spark
============================================================
"""

from scripts.utils.spark_session import create_spark_session
from scripts.bronze.load_customers import load_customer
from scripts.bronze.load_orders import load_order
from scripts.bronze.load_geolocations import load_geolocation
from scripts.bronze.load_order_items import load_order_item
from scripts.bronze.load_order_payments import load_order_payment
from scripts.bronze.load_order_reviews import load_order_review
from scripts.bronze.load_products import load_product
from scripts.bronze.load_sellers import load_seller
from scripts.bronze.load_product_category_name_translations import load_product_category_name_translation

def main():
    """
    Main ETL execution.
    """
    spark = create_spark_session()

    LOADERS = {
        "customers": load_customer,
        "orders": load_order,
        "order_items": load_order_item,
        "order_payments": load_order_payment,
        "order_reviews": load_order_review,       
        "products": load_product,
        "sellers": load_seller,
        "geolocation": load_geolocation,
        "product_category_name_translation": load_product_category_name_translation,
    }

    try:
        while True:
            # User input to load all or specific tables
            try:
                dataset = input(
                    "\nEnter dataset to load (or 'all'): "
                ).strip().lower()

                if dataset == "all":
                    for name, loader in LOADERS.items():
                        print(f"\nLoading {name}...")
                        loader(spark)

                elif dataset in LOADERS:
                    LOADERS[dataset](spark)

                else:
                    raise ValueError(
                        f"Dataset '{dataset}' does not exist."
                    )

            except ValueError as e:
                print(f"\nInput Error: {e}")
                print("\nAvailable datasets:")
                for name in LOADERS:
                    print(f" - {name}")
                print(" - all")

            except Exception as e:
                print(f"\nUnexpected Error during execution: {e}")

            # Ask the user if they want to choose again or exit
            while True:
                choice = input("\nWould you like to choose again? (Yes/No): ").strip().lower()
                if choice in ['yes', 'no']:
                    break
                print("Invalid input. Please enter 'Yes' or 'No'.")

            if choice == 'no':
                print("\nExiting the program...")
                break

    except Exception as e:
        print(f"\nCritical Pipeline Error: {e}")

    finally:
        if 'spark' in locals():
            spark.stop()
            print("\nSpark Session Closed.")

if __name__ == "__main__":
    main()
