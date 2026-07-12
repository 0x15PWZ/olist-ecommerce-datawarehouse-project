# Bronze Layer 

*The Bronze Layer* is the raw data ingestion layer of a data warehouse.
Its responsibility is to bring data from the source system into the data warehouse with minimal or no transformation. The goal is to preserve the original data as faithfully as possible.

---

## Project Objective

CSV Files
      │
      ▼
PySpark
      │
      ▼
PostgreSQL (Bronze Schema)

---

## Bronze Layer Characteristics


| *Item* | *Value* | 
| :--------- | :----------: | 
| Definition     |     Raw and unprocessed data from the source     |      
| Source  |  Olist CSV files  |  
| Destination  |  PostgreSQL Bronze schema  |  
| Processing Engine  |  PySpark  |  
| Database  |  Full Load (Truncate & Insert)  |  
| Load Method  |  None (or only schema enforcement)  |  
| Data Model |  None  |  
| Validation  |  Row count comparison  |  


---

## Bronze Layer Objectives

The Bronze Layer should answer these questions:

1. Did we receive the source data?
2. Is every row loaded?
3. Can we reproduce the original source?
4. Can we reload data if necessary?
5. Can we debug ingestion issues?
6. Project Structure

---

### My project is organized as follows:

olist-ecommerce-data-warehouse/
│
├── config/
│   └── config.py
│
├── data/
│   └── raw/
│
├── jars/
│
├── scripts/
│   ├── bronze/
│   │     bronze_loader.py
│   │     load_customers.py
│   │     load_orders.py
│   │     ...
│   │
│   ├── schemas/
│   │     customers_schema.py
│   │     orders_schema.py
│   │     ...
│   │
│   └── utils/
│         spark_session.py
│         database.py
│
└── main.py

---

## Components I Built

### 1. Configuration 

Files: 
    config/config.py

Responsibilities:
    Database host
    Port
    Username
    Password
    JDBC URL

Purpose:
    Avoid hardcoding database information throughout the project.

---

### 2. Spark Session Utility

File: 
    scripts/utils/spark_session.py

Responsibilities:
    Configure Hadoop
    Configure PostgreSQL JDBC
    Create one reusable Spark session
    Return the Spark session

Purpose:
    This ensures Spark is initialized only once.

---

### 3. Database Utility

File:
    scripts/utils/database.py

Functions:
    get_connection() # Creates a PostgreSQL connection.

    execute_sql() # Runs SQL statements such as:
                    . TRUNCATE
                    . CREATE
                    . DROP

    fetch_one() # Retrieves a single result, such as:
                    SELECT COUNT(*)

    table_exists() # Checks if a table exists before truncating it.

---

### 4. PySpark Schemas

Instead of relying on:

    .option("inferSchema", True)

    I  define schemas explicitly using StructType and StructField.

    Benefits:

        . Consistent data types
        . Better performance
        . Avoids schema inference errors
        . Enables Spark to create PostgreSQL tables with the intended types

---

### 5. Generic Bronze Loader

File:
    scripts/bronze/bronze_loader.py

This is the core of the Bronze Layer.

Responsibilities:
    . Validate the CSV file
    . Read the CSV using a predefined schema
    . Preview the data
    . Print the schema
    . Count CSV rows
    . Check if the destination table exists
    . Truncate the table if it exists
    . Write the DataFrame to PostgreSQL via JDBC
    . Validate the row count

Because this logic is centralized, every dataset uses the same loading process.

---
### 6. Dataset-Specific Loaders

Examples:
    load_customers.py
    load_orders.py
    load_products.py

Each loader is intentionally small. It specifies:

    the CSV filename,
    the destination table, and
    the schema.

Example:

load_csv_to_bronze(
    spark=spark,
    csv_file="olist_customers_dataset.csv",
    table_name="bronze.customers",
    schema=customers_schema
)

---
### 7. Main Pipeline

main.py orchestrates the process.

Responsibilities:

    . Create the Spark session
    . Display available datasets
    . Accept user input
    . Run the selected loader(s)
    . Handle errors
    . Stop Spark when finished

Supported commands:

    customers
    orders
    products
    ...
    all
    exit

### Bronze ETL Flow

        Start
        │
        ▼
        Create Spark Session
        │
        ▼
        User selects dataset
        │
        ▼
        Locate CSV
        │
        ▼
        Validate CSV exists
        │
        ▼
        Read CSV using predefined schema
        │
        ▼
        Preview data
        │
        ▼
        Count rows
        │
        ▼
        Check whether the PostgreSQL table exists
        │
        ├── Yes → Truncate table
        │
        └── No → Spark creates the table on write
        │
        ▼
        Write DataFrame to PostgreSQL via JDBC
        │
        ▼
        Count rows in PostgreSQL
        │
        ▼
        Compare CSV and database row counts
        │
        ├── Match → Success
        │
        └── Mismatch → Raise an error
        │
        ▼
        End
        Datasets Loaded

My Bronze layer covers the nine Olist datasets.
Each load performs a simple but effective validation:

    1. Count rows in the CSV.
    2. Count rows in the PostgreSQL table.
    3. Compare the counts.
    4. Report success or raise an error if they differ.

This confirms that all rows were loaded.

---