"""
============================================================
Silver Layer Validation

Validate silver.customers
============================================================
"""

from scripts.utils.databases import fetch_one
from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_customers():

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            COUNT(
                CASE
                    WHEN customer_id IS NULL
                    THEN 1
                END
            ) AS null_customer_id_count,

            COUNT(
                CASE
                    WHEN customer_unique_id IS NULL
                    THEN 1
                END
            ) AS null_customer_unique_id_count,

            COUNT(
                CASE
                    WHEN customer_zip_code_prefix IS NULL
                    THEN 1
                END
            ) AS null_zip_prefix_count,

            COUNT(
                CASE
                    WHEN create_date IS NULL
                    THEN 1
                END
            ) AS null_create_date_count,

            COUNT(
                CASE
                    WHEN TRIM(customer_id) = ''
                    THEN 1
                END
            ) AS empty_customer_id_count,

            COUNT(
                CASE
                    WHEN LENGTH(customer_state) <> 2
                    THEN 1
                END
            ) AS invalid_state_length_count,

            COUNT(
                CASE
                    WHEN customer_zip_code_prefix <= 0
                    THEN 1
                END
            ) AS invalid_zip_range_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS invalid_update_date_count,

            COUNT(
                CASE
                    WHEN create_date > NOW()
                    THEN 1
                END
            ) AS future_create_date_count,

            COUNT(
                CASE
                    WHEN source_system IS NULL
                      OR TRIM(source_system) = ''
                    THEN 1
                END
            ) AS missing_source_system_count,

            COUNT(
                CASE
                    WHEN file_location IS NULL
                      OR TRIM(file_location) = ''
                    THEN 1
                END
            ) AS missing_file_location_count

        FROM silver.customers

    ),

    duplicate_checks AS (

        SELECT
            COUNT(*) AS duplicate_customer_id_count

        FROM
        (
            SELECT customer_id

            FROM silver.customers

            GROUP BY customer_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,
        v.null_customer_id_count,
        v.empty_customer_id_count,
        d.duplicate_customer_id_count,
        v.null_customer_unique_id_count,
        v.null_zip_prefix_count,
        v.invalid_zip_range_count,
        v.invalid_state_length_count,
        v.null_create_date_count,
        v.invalid_update_date_count,
        v.future_create_date_count,
        v.missing_source_system_count,
        v.missing_file_location_count,

        CASE

            WHEN
            (
                v.null_customer_id_count
                + v.empty_customer_id_count
                + d.duplicate_customer_id_count
                + v.invalid_zip_range_count
                + v.invalid_update_date_count
            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_checks d;
    """

    result = fetch_one(sql)

    (
        total_records,
        null_customer_id,
        empty_customer_id,
        duplicate_customer_id,
        null_customer_unique_id,
        null_zip_prefix,
        invalid_zip_range,
        invalid_state_length,
        null_create_date,
        invalid_update_date,
        future_create_date,
        missing_source_system,
        missing_file_location,
        validation_status
    ) = result

    print_validation_header("silver.customers")

    metrics = {

        "Total Records": total_records,
        "NULL customer_id": null_customer_id,
        "Empty customer_id": empty_customer_id,
        "Duplicate customer_id": duplicate_customer_id,
        "NULL customer_unique_id": null_customer_unique_id,
        "NULL zip_code_prefix": null_zip_prefix,
        "Invalid zip_code_prefix": invalid_zip_range,
        "Invalid customer_state length": invalid_state_length,
        "NULL create_date": null_create_date,
        "Update < Create": invalid_update_date,
        "Future create_date": future_create_date,
        "Missing source_system": missing_source_system,
        "Missing file_location": missing_file_location

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status