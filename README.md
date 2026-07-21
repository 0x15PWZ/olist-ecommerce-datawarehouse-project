# Ecommerence Data Warehouse Project

***Welcome to the Data Warehouse and Analytics Project repository!
This project demonstrates a comprehensive data warehousing and analytics solution, from building a data warehouse to generating actionable insights. Designed as a portfolio project, it highlights industry best practices in data engineering and analytics.***

---

## Tech Stack

| Process | Technology |
|---------|------------|
| ETL| Python |
| Database | PostgreSQL |

---
## Folder Structure

```text
olist-ecommerce-data-warehouse/
│   .gitignore
│   LICENSE
│   main.py
│   README.md
│   requirements.txt
│   
├───config
│   │   config.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           config.cpython-314.pyc
│           __init__.cpython-314.pyc
│           
├───data
│   └───raw
│           olist_customers_dataset.csv
│           olist_geolocation_dataset.csv
│           olist_orders_dataset.csv
│           olist_order_items_dataset.csv
│           olist_order_payments_dataset.csv
│           olist_order_reviews_dataset.csv
│           olist_products_dataset.csv
│           olist_sellers_dataset.csv
│           product_category_name_translation.csv
│           
├───jars
│       postgresql-42.7.3.jar
│       
├───logs
├───notes
│       bronze_note.md
│       
├───scripts
│   │   __init__.py
│   │   
│   ├───bronze
│   │   │   bronze_loader1.py
│   │   │   load_customers1.py
│   │   │   load_geolocations1.py
│   │   │   load_orders1.py
│   │   │   load_order_items1.py
│   │   │   load_order_payments1.py
│   │   │   load_order_reviews1.py
│   │   │   load_products1.py
│   │   │   load_product_category_name_translations1.py
│   │   │   load_sellers1.py
│   │   │   
│   │   └───__pycache__
│   │           bronze_loader.cpython-314.pyc
│   │           bronze_loader1.cpython-314.pyc
│   │           load_customers.cpython-314.pyc
│   │           load_customers1.cpython-314.pyc
│   │           load_geolocations.cpython-314.pyc
│   │           load_geolocations1.cpython-314.pyc
│   │           load_orders.cpython-314.pyc
│   │           load_orders1.cpython-314.pyc
│   │           load_order_items.cpython-314.pyc
│   │           load_order_items1.cpython-314.pyc
│   │           load_order_payments.cpython-314.pyc
│   │           load_order_payments1.cpython-314.pyc
│   │           load_order_reviews.cpython-314.pyc
│   │           load_order_reviews1.cpython-314.pyc
│   │           load_products.cpython-314.pyc
│   │           load_products1.cpython-314.pyc
│   │           load_product_category_name_translations.cpython-314.pyc
│   │           load_product_category_name_translations1.cpython-314.pyc
│   │           load_sellers.cpython-314.pyc
│   │           load_sellers1.cpython-314.pyc
│   │           
│   ├───schemas
│   │   │   category_translation_schema.py
│   │   │   customers_schema.py
│   │   │   geolocation_schema.py
│   │   │   orders_schema.py
│   │   │   order_items_schema.py
│   │   │   order_payments_schema.py
│   │   │   order_reviews_schema.py
│   │   │   products_schema.py
│   │   │   sellers_schema.py
│   │   │   __init__.py
│   │   │   
│   │   └───__pycache__
│   │           category_translation_schema.cpython-314.pyc
│   │           customers_schema.cpython-314.pyc
│   │           geolocation_schema.cpython-314.pyc
│   │           orders_schema.cpython-314.pyc
│   │           order_items_schema.cpython-314.pyc
│   │           order_payments_schema.cpython-314.pyc
│   │           order_reviews_schema.cpython-314.pyc
│   │           products_schema.cpython-314.pyc
│   │           sellers_schema.cpython-314.pyc
│   │           __init__.cpython-314.pyc
│   │           
│   ├───silver
│   │   │   load_customers.py
│   │   │   load_geolocation.py
│   │   │   load_orders.py
│   │   │   load_order_items.py
│   │   │   load_order_payments.py
│   │   │   load_order_reviews.py
│   │   │   load_products.py
│   │   │   load_product_category_name_translation.py
│   │   │   load_sellers.py
│   │   │   silver_loader.py
│   │   │   
│   │   └───__pycache__
│   │           load_customers.cpython-314.pyc
│   │           load_geolocation.cpython-314.pyc
│   │           load_orders.cpython-314.pyc
│   │           load_order_items.cpython-314.pyc
│   │           load_order_payments.cpython-314.pyc
│   │           load_order_reviews.cpython-314.pyc
│   │           load_products.cpython-314.pyc
│   │           load_product_category_name_translation.cpython-314.pyc
│   │           load_sellers.cpython-314.pyc
│   │           silver_loader.cpython-314.pyc
│   │           
│   ├───transformations
│   │   │   customers.py
│   │   │   geolocation.py
│   │   │   orders.py
│   │   │   order_items.py
│   │   │   order_payments.py
│   │   │   order_reviews.py
│   │   │   products.py
│   │   │   product_category_name_translation.py
│   │   │   sellers.py
│   │   │   
│   │   └───__pycache__
│   │           customers.cpython-314.pyc
│   │           geolocation.cpython-314.pyc
│   │           orders.cpython-314.pyc
│   │           order_items.cpython-314.pyc
│   │           order_payments.cpython-314.pyc
│   │           order_reviews.cpython-314.pyc
│   │           products.cpython-314.pyc
│   │           product_category_name_translation.cpython-314.pyc
│   │           sellers.cpython-314.pyc
│   │           
│   ├───utils
│   │   │   databases.py
│   │   │   logger.py
│   │   │   spark_session1.py
│   │   │   __init__.py
│   │   │   
│   │   └───__pycache__
│   │           database.cpython-314.pyc
│   │           databases.cpython-314.pyc
│   │           sparksession.cpython-314.pyc
│   │           spark_session.cpython-314.pyc
│   │           spark_session1.cpython-314.pyc
│   │           __init__.cpython-314.pyc
│   │           
│   ├───validations
│   │   │   validate_customers.py
│   │   │   validate_geolocation.py
│   │   │   validate_orders.py
│   │   │   validate_order_items.py
│   │   │   validate_order_payments.py
│   │   │   validate_order_reviews.py
│   │   │   validate_products.py
│   │   │   validate_product_category_name_translation.py
│   │   │   validate_sellers.py
│   │   │   validation_loader.py
│   │   │   __init.py__
│   │   │   
│   │   └───__pycache__
│   │           validate_customers.cpython-314.pyc
│   │           validate_geolocation.cpython-314.pyc
│   │           validate_orders.cpython-314.pyc
│   │           validate_order_items.cpython-314.pyc
│   │           validate_order_payments.cpython-314.pyc
│   │           validate_order_reviews.cpython-314.pyc
│   │           validate_products.cpython-314.pyc
│   │           validate_product_category_name_translation.cpython-314.pyc
│   │           validate_sellers.cpython-314.pyc
│   │           validation_loader.cpython-314.pyc
│   │           
│   └───__pycache__
│           __init__.cpython-314.pyc
│           
├───sql
│   ├───bronze
│   │       bronze_ddl.sql
│   │       bronze_validation.sql
│   │       
│   ├───ddl
│   │       create_schemas.sql
│   │       
│   ├───gold
│   └───silver
│           silver_customer_validation.sql
│           silver_geolocation_validations.sql
│           silver_orders_validation.sql
│           silver_order_items_validation.sql
│           silver_order_payments_validation.sql
│           silver_order_reviews_validations.sql
│           silver_products_validatons.sql
│           silver_product_category_name_translation.sql
│           silver_sellers_validation.sql
│           silver_transform_tables.sql
│           silver_validation.sql
│           
├───src
│   │   main.py
│   │   
│   ├───bronze
│   ├───config
│   ├───extract
│   ├───gold
│   ├───logging
│   ├───quanlity
│   ├───silver
│   └───utils
└───tests
        test.py

```
---
## Data Architecture
![Data Warehouse Architecture](images/Olist%20Ecommerce%20Data%20Warehouse%20Project%20Architecture%20Design.png)

---
## Project Overview

This project involves:

1. ***Data Architecture***: Designing a Modern Data Warehouse Using Medallion Architecture Bronze, Silver, and Gold layers.
2. ***ETL Pipelines***: Extracting, transforming, and loading data from source systems into the warehouse.
3. ***Data Modeling***: Developing fact and dimension tables optimized for analytical queries.
4. ***Analytics & Reporting***: Creating SQL-based reports and dashboards for actionable insights.

🎯 This repository is an excellent resource for professionals and students looking to showcase expertise in:

- SQL Development
- Data Architect
- Data Engineering
- ETL Pipeline Developer
- Data Modeling
- Data Analytics

---
## Project Requirements

Building the Data Warehouse (Data Engineering)

### Objective
Develop a modern data warehouse using Python and PostgreSQL to consolidate sales data, enabling analytical reporting and informed decision-making.

### Specifications
- ***Data Sources***: Import data source systems provided as CSV files.
- ***Data Quality***: Cleanse and resolve data quality issues prior to analysis.
- ***Integration***: Combine both sources into a single, user-friendly data model designed for analytical queries.
- ***Scope***: Focus on the latest dataset only; historization of data is not required.
- ***Documentation***: Provide clear documentation of the data model to support both business stakeholders and analytics teams.

---

## Lincense

This project is licensed under MIT lincense for more info.
- You are free to use, modify, and share this project with proper attribution.

---

## About Me
Hi there! I'm Phyoe Wai Zaw, also known as Tharphyoe. I’m an enthusiast in Data Engineering and this is the one of my projects.

---

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/phyoe-wai-zaw-418906392) | 
[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/phyoe.wai.zaw.689855)
