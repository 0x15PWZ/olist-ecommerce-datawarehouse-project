"""
============================================================
Gold Layer Validation

Table
------------------------------------------------------------
gold.dim_date

Purpose
------------------------------------------------------------
Validate Gold Date Dimension business rules.

Grain
------------------------------------------------------------
One row = One calendar date

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_gold_dim_date():

    print_validation_header("gold.dim_date")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Primary Key Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN date_key IS NULL
                    THEN 1
                END
            ) AS missing_date_key_count,

            --------------------------------------------------
            -- Business Date Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN full_date IS NULL
                    THEN 1
                END
            ) AS missing_full_date_count,

            --------------------------------------------------
            -- Calendar Attribute Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN year IS NULL
                      OR year <= 0
                    THEN 1
                END
            ) AS invalid_year_count,

            COUNT(
                CASE
                    WHEN month IS NULL
                      OR month NOT BETWEEN 1 AND 12
                    THEN 1
                END
            ) AS invalid_month_count,

            COUNT(
                CASE
                    WHEN day IS NULL
                      OR day NOT BETWEEN 1 AND 31
                    THEN 1
                END
            ) AS invalid_day_count,

            COUNT(
                CASE
                    WHEN quarter IS NULL
                      OR quarter NOT BETWEEN 1 AND 4
                    THEN 1
                END
            ) AS invalid_quarter_count,

            --------------------------------------------------
            -- Date Consistency
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN full_date IS NOT NULL
                     AND date_key IS NOT NULL
                     AND date_key <>
                         CAST(
                             TO_CHAR(full_date, 'YYYYMMDD')
                             AS INTEGER
                         )
                    THEN 1
                END
            ) AS date_key_mismatch_count,

            --------------------------------------------------
            -- Metadata Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM gold.dim_date

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_date_key_count

        FROM (

            SELECT date_key

            FROM gold.dim_date

            GROUP BY date_key

            HAVING COUNT(*) > 1

        ) t

    ),

    duplicate_date_checks AS (

        SELECT

            COUNT(*) AS duplicate_full_date_count

        FROM (

            SELECT full_date

            FROM gold.dim_date

            GROUP BY full_date

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,

        v.missing_date_key_count,

        d.duplicate_date_key_count,

        v.missing_full_date_count,

        dd.duplicate_full_date_count,

        v.invalid_year_count,

        v.invalid_month_count,

        v.invalid_day_count,

        v.invalid_quarter_count,

        v.date_key_mismatch_count,

        v.system_date_mismatch_count,

        CASE

            WHEN
            (
                v.missing_date_key_count
              + d.duplicate_date_key_count
              + v.missing_full_date_count
              + dd.duplicate_full_date_count
              + v.invalid_year_count
              + v.invalid_month_count
              + v.invalid_day_count
              + v.invalid_quarter_count
              + v.date_key_mismatch_count
              + v.system_date_mismatch_count
            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_checks d

    CROSS JOIN duplicate_date_checks dd;
    """

    result = fetch_one(sql)

    (
        total_records,
        missing_date_key,
        duplicate_date_key,
        missing_full_date,
        duplicate_full_date,
        invalid_year,
        invalid_month,
        invalid_day,
        invalid_quarter,
        date_key_mismatch,
        system_date_mismatch,
        validation_status,
    ) = result

    metrics = {

        "Total Records": total_records,

        "Missing date_key": missing_date_key,
        "Duplicate date_key": duplicate_date_key,

        "Missing full_date": missing_full_date,
        "Duplicate full_date": duplicate_full_date,

        "Invalid year": invalid_year,
        "Invalid month": invalid_month,
        "Invalid day": invalid_day,
        "Invalid quarter": invalid_quarter,
        "Date key mismatch": date_key_mismatch,

        "Update < Create": system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status