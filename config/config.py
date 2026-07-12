"""
============================================================
Project Configuration
Project : Olist E-Commerce Data Warehouse
Author  : Phyoe Wai Zaw
============================================================
"""

# ==========================================================
# PostgreSQL Database Configuration
# ==========================================================

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "olist_dw"
DB_USER = "postgres"
DB_PASSWORD = "tharphyoe"

# ==========================================================
# JDBC Configuration
# ==========================================================

JDBC_URL = (
    f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
)