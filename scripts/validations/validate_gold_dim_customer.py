"""
============================================================
Gold Layer Validation

Table
------------------------------------------------------------
gold.dim_customers

Purpose
------------------------------------------------------------
Validate Gold Customer Dimension business rules.

Grain
------------------------------------------------------------
One row = One customer

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_gold_dim_customers():

    print_validation_header("gold.dim_customers")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Surrogate Key Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN customer_key IS NULL
                    THEN 1
                END
            ) AS missing_customer_key_count,

            --------------------------------------------------
            -- Business Key Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN customer_id IS NULL
                      OR TRIM(customer_id) = ''
                    THEN 1
                END
            ) AS missing_customer_id_count,

            COUNT(
                CASE
                    WHEN customer_unique_id IS NULL
                      OR TRIM(customer_unique_id) = ''
                    THEN 1
                END
            ) AS missing_customer_unique_id_count,

            --------------------------------------------------
            -- Customer Location Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN customer_city IS NULL
                      OR TRIM(customer_city) = ''
                    THEN 1
                END
            ) AS missing_customer_city_count,

            COUNT(
                CASE
                    WHEN customer_state IS NULL
                      OR TRIM(customer_state) = ''
                    THEN 1
                END
            ) AS missing_customer_state_count,

            COUNT(
                CASE
                    WHEN customer_state IS NOT NULL
                     AND LENGTH(TRIM(customer_state)) <> 2
                    THEN 1
                END
            ) AS invalid_customer_state_count,

            --------------------------------------------------
            -- ZIP Code Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN customer_zip_code_prefix IS NULL
                    THEN 1
                END
            ) AS missing_zip_code_count,

            COUNT(
                CASE
                    WHEN customer_zip_code_prefix IS NOT NULL
                     AND customer_zip_code_prefix < 0
                    THEN 1
                END
            ) AS invalid_zip_code_count,

            --------------------------------------------------
            -- Metadata Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM gold.dim_customers

    ),

    duplicate_customer_key_checks AS (

        SELECT

            COUNT(*) AS duplicate_customer_key_count

        FROM (

            SELECT customer_key

            FROM gold.dim_customers

            GROUP BY customer_key

            HAVING COUNT(*) > 1

        ) t

    ),

    duplicate_customer_id_checks AS (

        SELECT

            COUNT(*) AS duplicate_customer_id_count

        FROM (

            SELECT customer_id

            FROM gold.dim_customers

            GROUP BY customer_id

            HAVING COUNT(*) > 1

        ) t

    ),

    duplicate_customer_unique_id_checks AS (

        SELECT

            COUNT(*) AS duplicate_customer_unique_id_count

        FROM (

            SELECT customer_unique_id

            FROM gold.dim_customers

            GROUP BY customer_unique_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,

        --------------------------------------------------
        -- Surrogate Key
        --------------------------------------------------

        v.missing_customer_key_count,
        ck.duplicate_customer_key_count,

        --------------------------------------------------
        -- Business Keys
        --------------------------------------------------

        v.missing_customer_id_count,
        ci.duplicate_customer_id_count,

        v.missing_customer_unique_id_count,

        --------------------------------------------------
        -- Customer Attributes
        --------------------------------------------------

        v.missing_customer_city_count,
        v.missing_customer_state_count,
        v.invalid_customer_state_count,

        --------------------------------------------------
        -- ZIP Code
        --------------------------------------------------

        v.missing_zip_code_count,
        v.invalid_zip_code_count,

        --------------------------------------------------
        -- Metadata
        --------------------------------------------------

        v.system_date_mismatch_count,

        --------------------------------------------------
        -- Overall Validation
        --------------------------------------------------

        CASE

            WHEN
            (
                v.missing_customer_key_count
              + ck.duplicate_customer_key_count

              + v.missing_customer_id_count
              + ci.duplicate_customer_id_count

              + v.missing_customer_unique_id_count

              + v.missing_customer_city_count
              + v.missing_customer_state_count
              + v.invalid_customer_state_count

              + v.missing_zip_code_count
              + v.invalid_zip_code_count

              + v.system_date_mismatch_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_customer_key_checks ck

    CROSS JOIN duplicate_customer_id_checks ci

    CROSS JOIN duplicate_customer_unique_id_checks cu;
    """

    result = fetch_one(sql)

    (
        total_records,

        missing_customer_key,
        duplicate_customer_key,

        missing_customer_id,
        duplicate_customer_id,

        missing_customer_unique_id,

        missing_customer_city,
        missing_customer_state,
        invalid_customer_state,

        missing_zip_code,
        invalid_zip_code,

        system_date_mismatch,

        validation_status,
    ) = result

    metrics = {

        "Total Records": total_records,

        "Missing customer_key": missing_customer_key,
        "Duplicate customer_key": duplicate_customer_key,

        "Missing customer_id": missing_customer_id,
        "Duplicate customer_id": duplicate_customer_id,

        "Missing customer_unique_id": missing_customer_unique_id,

        "Missing customer_city": missing_customer_city,
        "Missing customer_state": missing_customer_state,
        "Invalid customer_state": invalid_customer_state,

        "Missing ZIP code": missing_zip_code,
        "Invalid ZIP code": invalid_zip_code,

        "Update < Create": system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status