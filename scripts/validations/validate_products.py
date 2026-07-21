"""
============================================================
Silver Layer Validation

Validate silver.products

Purpose
------------------------------------------------------------
Perform data quality validation for the Silver Products
table and print a validation report.
============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_products():
    """
    Validate silver.products.
    """

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            COUNT(
                CASE
                    WHEN product_id IS NULL
                      OR TRIM(product_id) = ''
                    THEN 1
                END
            ) AS missing_product_id_count,

            COUNT(
                CASE
                    WHEN product_category_name IS NOT NULL
                     AND TRIM(product_category_name) = ''
                    THEN 1
                END
            ) AS whitespace_only_category_count,

            COUNT(
                CASE
                    WHEN product_name_length < 0
                    THEN 1
                END
            ) AS negative_name_length_count,

            COUNT(
                CASE
                    WHEN product_description_length < 0
                    THEN 1
                END
            ) AS negative_description_length_count,

            COUNT(
                CASE
                    WHEN product_photos_qty < 0
                    THEN 1
                END
            ) AS negative_photos_qty_count,

            COUNT(
                CASE
                    WHEN product_weight_g IS NOT NULL
                     AND product_weight_g <= 0
                    THEN 1
                END
            ) AS invalid_weight_count,

            COUNT(
                CASE
                    WHEN product_length_cm IS NOT NULL
                     AND product_length_cm <= 0
                    THEN 1
                END
            ) AS invalid_length_count,

            COUNT(
                CASE
                    WHEN product_height_cm IS NOT NULL
                     AND product_height_cm <= 0
                    THEN 1
                END
            ) AS invalid_height_count,

            COUNT(
                CASE
                    WHEN product_width_cm IS NOT NULL
                     AND product_width_cm <= 0
                    THEN 1
                END
            ) AS invalid_width_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM silver.products

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_product_id_count

        FROM (

            SELECT product_id

            FROM silver.products

            WHERE product_id IS NOT NULL

            GROUP BY product_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,
        v.missing_product_id_count,
        d.duplicate_product_id_count,
        v.whitespace_only_category_count,
        v.negative_name_length_count,
        v.negative_description_length_count,
        v.negative_photos_qty_count,
        v.invalid_weight_count,
        v.invalid_length_count,
        v.invalid_height_count,
        v.invalid_width_count,
        v.system_date_mismatch_count,

        CASE

            WHEN (

                v.missing_product_id_count
                + d.duplicate_product_id_count
                + v.whitespace_only_category_count
                + v.negative_name_length_count
                + v.negative_description_length_count
                + v.negative_photos_qty_count
                + v.invalid_weight_count
                + v.invalid_length_count
                + v.invalid_height_count
                + v.invalid_width_count
                + v.system_date_mismatch_count

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
        missing_product_id,
        duplicate_product_id,
        whitespace_category,
        negative_name_length,
        negative_description_length,
        negative_photos_qty,
        invalid_weight,
        invalid_length,
        invalid_height,
        invalid_width,
        system_date_mismatch,
        validation_status
    ) = result

    print_validation_header("silver.products")

    # Critical errors
    critical_errors = (
        missing_product_id +
        duplicate_product_id +
        whitespace_category +
        negative_name_length +
        negative_description_length +
        system_date_mismatch
    )
    # Warnings
    warnings = (
        invalid_weight +
        invalid_height +
        invalid_length +
        invalid_width
    )
    
    # Overall status calculation
    if critical_errors == 0:
        if warnings == 0:
            validation_status = "PASSED"
        else:
            validation_status = "PASSED WITH WARNINGS"
    else:
        validation_status = "FAILED"

    print_validation_header("silver.products")

    critical_metrics = {
        "Missing product_id": missing_product_id,
        "Duplicate product_id": duplicate_product_id,
        "Whitespace category": whitespace_category,
        "Negative product_name_length": negative_name_length,
        "Negative product_description_length": negative_description_length,
        "Negative product_photos_qty": negative_photos_qty,
        "Update < Create": system_date_mismatch

    }

    print_validation_summary(
        critical_metrics,
        "PASSED" if critical_errors == 0 else "FAILED"
    )
    
    # source data warnings
    print("=" * 70)
    print("Source Data Warnings")
    print("=" * 70)

    warning_metrics = {
        "Invalid product weight_g": invalid_weight,
        "Invalid product heignt_cm": invalid_height,
        "Invalid product width_cm": invalid_width,
        "Invalid product length_cm": invalid_length,
    }

    # Warning output
    print_validation_summary(
        warning_metrics,
        "PASSED WITH WARNINGS" if warnings > 0 else "NO WARNINGS"
    )
    return validation_status