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

DB_URL = (
    f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

JDBC_URL = (
    f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

DB_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

