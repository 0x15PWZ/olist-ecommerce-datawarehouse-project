"""
============================================================
Gold Layer Validation

Table
------------------------------------------------------------
gold.dim_sellers

Purpose
------------------------------------------------------------
Validate Gold Seller Dimension business rules.

Grain
------------------------------------------------------------
One row = One seller

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_gold_dim_sellers():

    print_validation_header("gold.dim_sellers")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Surrogate Key
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN seller_key IS NULL
                    THEN 1
                END
            ) AS missing_seller_key_count,

            --------------------------------------------------
            -- Business Key
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN seller_id IS NULL
                      OR TRIM(seller_id) = ''
                    THEN 1
                END
            ) AS missing_seller_id_count,

            --------------------------------------------------
            -- Seller City
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN seller_city IS NULL
                      OR TRIM(seller_city) = ''
                    THEN 1
                END
            ) AS missing_seller_city_count,

            --------------------------------------------------
            -- Seller State
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN seller_state IS NULL
                      OR TRIM(seller_state) = ''
                    THEN 1
                END
            ) AS missing_seller_state_count,

            COUNT(
                CASE
                    WHEN seller_state IS NOT NULL
                     AND LENGTH(TRIM(seller_state)) <> 2
                    THEN 1
                END
            ) AS invalid_seller_state_count,

            --------------------------------------------------
            -- ZIP Code
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN seller_zip_code_prefix IS NULL
                    THEN 1
                END
            ) AS missing_zip_code_count,

            COUNT(
                CASE
                    WHEN seller_zip_code_prefix IS NOT NULL
                     AND seller_zip_code_prefix < 0
                    THEN 1
                END
            ) AS invalid_zip_code_count,

            --------------------------------------------------
            -- Metadata
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM gold.dim_sellers

    ),

    duplicate_seller_key_checks AS (

        SELECT

            COUNT(*) AS duplicate_seller_key_count

        FROM (

            SELECT seller_key

            FROM gold.dim_sellers

            GROUP BY seller_key

            HAVING COUNT(*) > 1

        ) t

    ),

    duplicate_seller_id_checks AS (

        SELECT

            COUNT(*) AS duplicate_seller_id_count

        FROM (

            SELECT seller_id

            FROM gold.dim_sellers

            GROUP BY seller_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,

        --------------------------------------------------
        -- Surrogate Key
        --------------------------------------------------

        v.missing_seller_key_count,
        sk.duplicate_seller_key_count,

        --------------------------------------------------
        -- Business Key
        --------------------------------------------------

        v.missing_seller_id_count,
        si.duplicate_seller_id_count,

        --------------------------------------------------
        -- Seller Attributes
        --------------------------------------------------

        v.missing_seller_city_count,
        v.missing_seller_state_count,
        v.invalid_seller_state_count,

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
                v.missing_seller_key_count
              + sk.duplicate_seller_key_count

              + v.missing_seller_id_count
              + si.duplicate_seller_id_count

              + v.missing_seller_city_count
              + v.missing_seller_state_count
              + v.invalid_seller_state_count

              + v.missing_zip_code_count
              + v.invalid_zip_code_count

              + v.system_date_mismatch_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_seller_key_checks sk

    CROSS JOIN duplicate_seller_id_checks si;
    """

    result = fetch_one(sql)

    (
        total_records,

        missing_seller_key,
        duplicate_seller_key,

        missing_seller_id,
        duplicate_seller_id,

        missing_seller_city,
        missing_seller_state,
        invalid_seller_state,

        missing_zip_code,
        invalid_zip_code,

        system_date_mismatch,

        validation_status,
    ) = result

    metrics = {

        "Total Records": total_records,

        "Missing seller_key": missing_seller_key,
        "Duplicate seller_key": duplicate_seller_key,

        "Missing seller_id": missing_seller_id,
        "Duplicate seller_id": duplicate_seller_id,

        "Missing seller_city": missing_seller_city,
        "Missing seller_state": missing_seller_state,
        "Invalid seller_state": invalid_seller_state,

        "Missing ZIP code": missing_zip_code,
        "Invalid ZIP code": invalid_zip_code,

        "Update < Create": system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status