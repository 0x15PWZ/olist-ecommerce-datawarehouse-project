"""
============================================================
Main ETL Pipeline

Purpose
------------------------------------------------------------
Central controller for all ETL layers.

Execution Flow
------------------------------------------------------------
1. Create Spark Session
2. Select ETL Layer
3. Select Dataset
4. Execute Loader
5. Stop Spark Session
============================================================
"""

from datetime import datetime  # Tracking execution times
from scripts.utils.spark_session1 import create_spark_session

# Bronze loaders (Aliased to avoid collision)
from scripts.bronze.load_customers1 import load_customer as load_customer_bronze
from scripts.bronze.load_orders1 import load_order as load_order_bronze
from scripts.bronze.load_geolocations1 import load_geolocation as load_geolocation_bronze
from scripts.bronze.load_order_items1 import load_order_item as load_order_item_bronze
from scripts.bronze.load_order_payments1 import load_order_payment as load_order_payment_bronze
from scripts.bronze.load_order_reviews1 import load_order_review as load_order_review_bronze
from scripts.bronze.load_products1 import load_product as load_product_bronze
from scripts.bronze.load_sellers1 import load_seller as load_seller_bronze
from scripts.bronze.load_product_category_name_translations1 import (
    load_product_category_name_translation as load_product_category_name_translation_bronze
)

# Silver loaders (Aliased to avoid collision)
from scripts.silver.load_customers import load_customer as load_customer_silver
from scripts.silver.load_orders import load_orders as load_orders_silver
from scripts.silver.load_order_items import load_order_item as load_order_item_silver
from scripts.silver.load_order_payments import load_order_payment as load_order_payment_silver
from scripts.silver.load_order_reviews import load_order_review as load_order_review_silver
from scripts.silver.load_products import load_product as load_product_silver
from scripts.silver.load_sellers import load_seller as load_seller_silver
from scripts.silver.load_geolocation import load_geolocations as load_geolocation_silver
from scripts.silver.load_product_category_name_translation import load_product_category_name_translations as load_product_category_name_translation_silver

# ==========================================================
# Validation Modules
# ==========================================================
from scripts.validations.validate_customers import validate_customers
from scripts.validations.validate_orders import validate_orders
from scripts.validations.validate_order_items import validate_order_items
from scripts.validations.validate_order_payments import validate_order_payments
from scripts.validations.validate_order_reviews import validate_order_reviews
from scripts.validations.validate_products import validate_products
from scripts.validations.validate_sellers import validate_sellers
from scripts.validations.validate_geolocation import validate_geolocation
from scripts.validations.validate_product_category_name_translation import validate_product_category_name_translation

BRONZE_select_loaders = {
    "customers": load_customer_bronze,
    "orders": load_order_bronze,
    "order_items": load_order_item_bronze,
    "order_payments": load_order_payment_bronze,
    "order_reviews": load_order_review_bronze,
    "products": load_product_bronze,
    "sellers": load_seller_bronze,
    "geolocation": load_geolocation_bronze,
    "product_category_name_translation": load_product_category_name_translation_bronze,
}

SILVER_select_loaders = {
    "customers": load_customer_silver,
    "orders": load_orders_silver,
    "order_items": load_order_item_silver,
    "order_payments": load_order_payment_silver,
    "order_reviews": load_order_review_silver,
    "products": load_product_silver,
    "sellers": load_seller_silver,
    "geolocation": load_geolocation_silver,
    "product_category_name_translation": load_product_category_name_translation_silver,
}

VALIDATION_loaders = {
    "customers": validate_customers,
    "orders": validate_orders,
    "order_items": validate_order_items,
    "order_payments": validate_order_payments,
    "order_reviews": validate_order_reviews,
    "products": validate_products,
    "sellers": validate_sellers,
    "geolocation": validate_geolocation,
    "product_category_name_translation": validate_product_category_name_translation,
}

LAYER_REGISTRY = {
    "bronze": BRONZE_select_loaders,
    "silver": SILVER_select_loaders,
    "validate": VALIDATION_loaders,
}

def run_loader(spark, dataset, select_loaders, layer):
    """
    Execute a single dataset loader safely with performance tracking.
    Conditionally omits Spark for validation tasks.
    """
    if dataset not in select_loaders:
        raise ValueError(f"Dataset '{dataset}' not found.")

    # Capture start time
    start_time = datetime.now()

    print("\n" + "=" * 60)
    print(f"Starting execution: {layer.upper()} - {dataset}")
    print(f"Start Time:    {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Execute the loader function (Skip passing Spark if it's the validation layer)
    if layer == "validate":
        select_loaders[dataset]()
    else:
        select_loaders[dataset](spark)

    # Capture end time and calculate duration
    end_time = datetime.now()
    duration = end_time - start_time
    duration_in_seconds = int(duration.total_seconds())

    print("\n" + "=" * 60)
    print(f"Completed execution: {layer.upper()} - {dataset}")
    print(f"Start Time :     {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time   :     {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration   :     {duration_in_seconds} seconds")
    print("=" * 60)


def main():
    """
    Main entry point for the ETL pipeline.
    """
    spark = None

    try:
        # ======================================================
        # Step 1: Create Spark Session
        # ======================================================
        spark = create_spark_session()

        while True:
            print("\nAvailable Layers:")
            for layer in LAYER_REGISTRY:
                print(f"  - {layer}")
            print("  - exit")

            layer = input("\nEnter ETL layer: ").strip().lower()

            if layer == "exit":
                break

            if layer not in LAYER_REGISTRY:
                print("Invalid layer.")
                continue

            select_loaders = LAYER_REGISTRY[layer]

            # ==================================================
            # Step 2: Show menu
            # ==================================================
            print("\nAvailable datasets:")
            for name in select_loaders:
                print(f"  - {name}")
            print("  - all")
            print("  - exit")

            # ==================================================
            # Step 3: User input
            # ==================================================
            dataset = input("\nEnter dataset to process: ").strip().lower()

            # ==================================================
            # Step 4: Exit option
            # ==================================================
            if dataset == "exit":
                print("\nExiting pipeline...")
                break

            # ==================================================
            # Step 5: Load/Validate ALL datasets
            # ==================================================
            elif dataset == "all":
                print(f"\nStarting full {layer.title()} layer execution...\n")
                for name in select_loaders:
                    try:
                        run_loader(spark, name, select_loaders, layer)
                    except Exception as e:
                        print(f"\nERROR processing {name} in {layer}: {e}")

            # ==================================================
            # Step 6: Load/Validate SINGLE dataset
            # ==================================================
            elif dataset in select_loaders:
                try:
                    run_loader(spark, dataset, select_loaders, layer)
                except Exception as e:
                    print("\n" + "=" * 60)
                    print("PROCESS FAILED")
                    print("=" * 60)
                    print(f"Layer   : {layer}")
                    print(f"Dataset : {dataset}")
                    print(f"Reason  : {e}")
                    print("=" * 60)

            # ==================================================
            # Step 7: Invalid input handling
            # ==================================================
            else:
                print("\nInvalid dataset name.")
                print("Please choose from the available list.")

            # ==================================================
            # Step 8: Ask user to continue
            # ==================================================
            while True:
                choice = input("\nDo you want to continue? (yes/no): ").strip().lower()
                if choice in ["yes", "no"]:
                    break
                print("Invalid input. Please type 'yes' or 'no'.")

            if choice == "no":
                print("\nStopping pipeline...")
                break

    except Exception as e:
        print("\nCRITICAL PIPELINE ERROR")
        print("=" * 40)
        print(e)

    finally:
        if spark:
            spark.stop()
            print("\nSpark session stopped successfully.")


# ==========================================================
# Entry Point
# ==========================================================
if __name__ == "__main__":
    main()

    