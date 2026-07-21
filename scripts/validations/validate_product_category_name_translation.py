"""
============================================================
Silver Layer Validation

Validate silver.product_category_name_translation

Purpose
------------------------------------------------------------
Perform data quality validation for the Silver Product
Category Name Translation table and print a validation report.
============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_product_category_name_translation():
    """
    Validate silver.product_category_name_translation.
    """

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            COUNT(
                CASE
                    WHEN product_category_name IS NULL
                      OR TRIM(product_category_name) = ''
                    THEN 1
                END
            ) AS missing_original_name_count,

            COUNT(
                CASE
                    WHEN product_category_name_english IS NULL
                      OR TRIM(product_category_name_english) = ''
                    THEN 1
                END
            ) AS missing_english_translation_count,

            COUNT(
                CASE
                    WHEN LOWER(TRIM(product_category_name))
                       = LOWER(TRIM(product_category_name_english))
                    THEN 1
                END
            ) AS identical_translation_count,

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

        FROM silver.product_category_name_translation

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_original_name_pk_count

        FROM (

            SELECT product_category_name

            FROM silver.product_category_name_translation

            WHERE product_category_name IS NOT NULL

            GROUP BY product_category_name

            HAVING COUNT(*) > 1

        ) t

    ),

    mapping_anomaly_checks AS (

        SELECT

            COUNT(*) AS duplicate_english_mapping_count

        FROM (

            SELECT product_category_name_english

            FROM silver.product_category_name_translation

            WHERE product_category_name_english IS NOT NULL

            GROUP BY product_category_name_english

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,
        v.missing_original_name_count,
        v.missing_english_translation_count,
        d.duplicate_original_name_pk_count,
        m.duplicate_english_mapping_count,
        v.identical_translation_count,
        v.system_date_mismatch_count,
        v.missing_source_system_count,

        CASE

            WHEN (

                v.missing_original_name_count
                + v.missing_english_translation_count
                + d.duplicate_original_name_pk_count
                + m.duplicate_english_mapping_count
                + v.system_date_mismatch_count
                + v.missing_source_system_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS business_rule_status

    FROM validation_checks v

    CROSS JOIN duplicate_checks d

    CROSS JOIN mapping_anomaly_checks m;
    """

    result = fetch_one(sql)

    if result is None:
        raise Exception("Validation query returned no result.")

    (
        total_records,
        missing_original_name,
        missing_english_translation,
        duplicate_original_name,
        duplicate_english_mapping,
        identical_translation,
        system_date_mismatch,
        missing_source_system,
        validation_status
    ) = result

    print_validation_header(
        "silver.product_category_name_translation"
    )

    metrics = {

        "Total Records": total_records,

        "Missing Original Category":
            missing_original_name,

        "Missing English Translation":
            missing_english_translation,

        "Duplicate Original Category":
            duplicate_original_name,

        "Duplicate English Mapping":
            duplicate_english_mapping,

        "Identical Translation":
            identical_translation,

        "Update < Create":
            system_date_mismatch,

        "Missing Source System":
            missing_source_system

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status