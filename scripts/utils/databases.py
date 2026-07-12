"""
============================================================
Database Utility Functions

This module provides reusable helper functions
for interacting with the PostgreSQL database.

Functions
---------
execute_sql()
    Execute SQL statements such as:
    - CREATE TABLE
    - TRUNCATE TABLE
    - DROP TABLE

fetch_one()
    Execute a SELECT query and return one row.

============================================================
"""

import psycopg2

from config.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)


# ==========================================================
# Create PostgreSQL Connection
# ==========================================================

def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ==========================================================
# Execute SQL Statements
# ==========================================================

def execute_sql(sql: str):
    """
    Execute SQL statements that do not return data.

    Examples:
        CREATE TABLE
        TRUNCATE TABLE
        DROP TABLE
        INSERT
        UPDATE
        DELETE
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)

    conn.commit()

    cursor.close()
    conn.close()


# ==========================================================
# Fetch One Record
# ==========================================================

def fetch_one(sql: str):
    """
    Execute a SELECT query and return
    the first record.

    Example:

    SELECT COUNT(*)
    FROM bronze.customers;
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result
# ==========================================================
# Check Whether a Table Exists
# ==========================================================

def table_exists(schema_name: str, table_name: str) -> bool:
    """
    Check whether a PostgreSQL table exists.

    Parameters
    ----------
    schema_name : str
        PostgreSQL schema name.
        Example:
            bronze

    table_name : str
        PostgreSQL table name.
        Example:
            customers

    Returns
    -------
    bool
        True if the table exists.
        False otherwise.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = %s
        );
        """,
        (schema_name, table_name)
    )

    exists = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return exists