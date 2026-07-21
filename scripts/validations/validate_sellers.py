"""
============================================================
Silver Layer Validation

Validate silver.sellers

Purpose
------------------------------------------------------------
Perform data quality validation for the Silver Sellers
table and print a validation report.
============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_sellers():
    """
    Validate silver.sellers.
    """

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            COUNT(
                CASE
                    WHEN seller_id IS NULL
                      OR TRIM(seller_id) = ''
                    THEN 1
                END
            ) AS missing_seller_id_count,

            COUNT(
                CASE
                    WHEN seller_zip_code_prefix IS NULL
                      OR seller_zip_code_prefix <= 0
                    THEN 1
                END
            ) AS invalid_zip_prefix_count,

            COUNT(
                CASE
                    WHEN seller_city IS NULL
                      OR TRIM(seller_city) = ''
                    THEN 1
                END
            ) AS missing_city_count,

            COUNT(
                CASE
                    WHEN seller_state IS NULL
                      OR LENGTH(TRIM(seller_state)) <> 2
                    THEN 1
                END
            ) AS invalid_state_code_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count,

            COUNT(
                CASE
                    WHEN source_system IS NULL
                      OR TRIM(source_system) = ''
                    THEN 1
                END
            ) AS missing_source_system_count

        FROM silver.sellers

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_seller_id_count

        FROM (

            SELECT seller_id

            FROM silver.sellers

            WHERE seller_id IS NOT NULL

            GROUP BY seller_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,
        v.missing_seller_id_count,
        d.duplicate_seller_id_count,
        v.invalid_zip_prefix_count,
        v.missing_city_count,
        v.invalid_state_code_count,
        v.system_date_mismatch_count,
        v.missing_source_system_count,

        CASE

            WHEN (

                v.missing_seller_id_count
                + d.duplicate_seller_id_count
                + v.invalid_zip_prefix_count
                + v.missing_city_count
                + v.invalid_state_code_count
                + v.system_date_mismatch_count
                + v.missing_source_system_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS business_rule_status

    FROM validation_checks v

    CROSS JOIN duplicate_checks d;
    """

    result = fetch_one(sql)

    if result is None:
        raise Exception("Validation query returned no result.")

    (
        total_records,
        missing_seller_id,
        duplicate_seller_id,
        invalid_zip_prefix,
        missing_city,
        invalid_state_code,
        system_date_mismatch,
        missing_source_system,
        validation_status
    ) = result

    print_validation_header("silver.sellers")

    metrics = {

        "Total Records": total_records,

        "Missing seller_id": missing_seller_id,

        "Duplicate seller_id": duplicate_seller_id,

        "Invalid zip_code_prefix": invalid_zip_prefix,

        "Missing seller_city": missing_city,

        "Invalid seller_state": invalid_state_code,

        "Update < Create": system_date_mismatch,

        "Missing source_system": missing_source_system

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status