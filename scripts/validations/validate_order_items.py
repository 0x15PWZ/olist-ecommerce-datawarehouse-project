"""
============================================================
Silver Layer Validation

Validate silver.order_items

Purpose
------------------------------------------------------------
Perform data quality validation for the Silver Order Items
table and print a validation report.
============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_order_items():
    """
    Validate silver.order_items.
    """

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            COUNT(
                CASE
                    WHEN order_id IS NULL
                      OR TRIM(order_id) = ''
                    THEN 1
                END
            ) AS missing_order_id_count,

            COUNT(
                CASE
                    WHEN order_item_id IS NULL
                    THEN 1
                END
            ) AS null_order_item_id_count,

            COUNT(
                CASE
                    WHEN product_id IS NULL
                      OR TRIM(product_id) = ''
                    THEN 1
                END
            ) AS missing_product_id_count,

            COUNT(
                CASE
                    WHEN seller_id IS NULL
                      OR TRIM(seller_id) = ''
                    THEN 1
                END
            ) AS missing_seller_id_count,

            COUNT(
                CASE
                    WHEN order_item_id <= 0
                    THEN 1
                END
            ) AS invalid_order_item_id_range_count,

            COUNT(
                CASE
                    WHEN price IS NULL
                      OR price <= 0
                    THEN 1
                END
            ) AS invalid_price_count,

            COUNT(
                CASE
                    WHEN freight_value IS NULL
                      OR freight_value < 0
                    THEN 1
                END
            ) AS invalid_freight_count,

            COUNT(
                CASE
                    WHEN shipping_limit_date IS NULL
                    THEN 1
                END
            ) AS missing_shipping_limit_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM silver.order_items

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_pk_combination_count

        FROM (

            SELECT
                order_id,
                order_item_id

            FROM silver.order_items

            WHERE
                order_id IS NOT NULL
                AND order_item_id IS NOT NULL

            GROUP BY
                order_id,
                order_item_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,
        v.missing_order_id_count,
        v.null_order_item_id_count,
        d.duplicate_pk_combination_count,
        v.missing_product_id_count,
        v.missing_seller_id_count,
        v.invalid_order_item_id_range_count,
        v.invalid_price_count,
        v.invalid_freight_count,
        v.missing_shipping_limit_count,
        v.system_date_mismatch_count,

        CASE

            WHEN (

                v.missing_order_id_count
                + v.null_order_item_id_count
                + d.duplicate_pk_combination_count
                + v.missing_product_id_count
                + v.missing_seller_id_count
                + v.invalid_order_item_id_range_count
                + v.invalid_price_count
                + v.invalid_freight_count
                + v.missing_shipping_limit_count
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
        missing_order_id,
        null_order_item_id,
        duplicate_pk,
        missing_product_id,
        missing_seller_id,
        invalid_order_item_id,
        invalid_price,
        invalid_freight,
        missing_shipping_limit,
        system_date_mismatch,
        validation_status
    ) = result

    print_validation_header("silver.order_items")

    metrics = {

        "Total Records": total_records,

        "Missing order_id": missing_order_id,

        "NULL order_item_id": null_order_item_id,

        "Duplicate PK (order_id + order_item_id)": duplicate_pk,

        "Missing product_id": missing_product_id,

        "Missing seller_id": missing_seller_id,

        "Invalid order_item_id": invalid_order_item_id,

        "Invalid price": invalid_price,

        "Invalid freight_value": invalid_freight,

        "Missing shipping_limit_date": missing_shipping_limit,

        "Update < Create": system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status