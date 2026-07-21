"""
============================================================
Silver Layer Validation

Table
------------------------------------------------------------
silver.orders

Purpose
------------------------------------------------------------
Validate Silver Orders business rules.

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_orders():

    print_validation_header("silver.orders")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Business Key Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN order_id IS NULL
                      OR TRIM(order_id) = ''
                    THEN 1
                END
            ) AS invalid_order_id_count,

            --------------------------------------------------
            -- Mandatory Fields
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN order_purchase_timestamp IS NULL
                    THEN 1
                END
            ) AS missing_purchase_timestamp_count,

            COUNT(
                CASE
                    WHEN customer_id IS NULL
                      OR TRIM(customer_id) = ''
                    THEN 1
                END
            ) AS missing_customer_id_count,

            --------------------------------------------------
            -- Conditional Business Rules
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN order_status IN
                    (
                        'APPROVED',
                        'INVOICED',
                        'PROCESSING',
                        'SHIPPED',
                        'DELIVERED'
                    )
                    AND order_approved_at IS NULL
                    THEN 1
                END
            ) AS missing_approval_timestamp_count,

            COUNT(
                CASE
                    WHEN order_status IN
                    (
                        'SHIPPED',
                        'DELIVERED'
                    )
                    AND order_delivered_carrier_date IS NULL
                    THEN 1
                END
            ) AS missing_carrier_timestamp_count,

            COUNT(
                CASE
                    WHEN order_status = 'DELIVERED'
                    AND order_delivered_customer_date IS NULL
                    THEN 1
                END
            ) AS missing_customer_delivery_timestamp_count,

            --------------------------------------------------
            -- Timestamp Sequence
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN order_approved_at IS NOT NULL
                    AND order_purchase_timestamp >
                        order_approved_at
                    THEN 1
                END
            ) AS purchase_after_approval_count,

            COUNT(
                CASE
                    WHEN order_approved_at IS NOT NULL
                    AND order_delivered_carrier_date IS NOT NULL
                    AND order_approved_at >
                        order_delivered_carrier_date
                    THEN 1
                END
            ) AS approval_after_carrier_count,

            COUNT(
                CASE
                    WHEN order_delivered_carrier_date IS NOT NULL
                    AND order_delivered_customer_date IS NOT NULL
                    AND order_delivered_carrier_date >
                        order_delivered_customer_date
                    THEN 1
                END
            ) AS carrier_after_customer_count,

            --------------------------------------------------
            -- Estimated Delivery Rules
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN order_estimated_delivery_date IS NULL
                    THEN 1
                END
            ) AS missing_estimated_date_count,

            COUNT(
                CASE
                    WHEN order_estimated_delivery_date IS NOT NULL
                    AND order_estimated_delivery_date
                        <= order_purchase_timestamp
                    THEN 1
                END
            ) AS estimated_before_purchase_count,

            --------------------------------------------------
            -- Metadata
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN is_valid_timestamp = FALSE
                    THEN 1
                END
            ) AS invalid_timestamp_flag_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM silver.orders

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_order_id_count

        FROM (

            SELECT order_id

            FROM silver.orders

            GROUP BY order_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,
        v.invalid_order_id_count,
        d.duplicate_order_id_count,
        v.missing_purchase_timestamp_count,
        v.missing_customer_id_count,
        v.missing_approval_timestamp_count,
        v.missing_carrier_timestamp_count,
        v.missing_customer_delivery_timestamp_count,
        v.purchase_after_approval_count,
        v.approval_after_carrier_count,
        v.carrier_after_customer_count,
        v.missing_estimated_date_count,
        v.estimated_before_purchase_count,
        v.invalid_timestamp_flag_count,
        v.system_date_mismatch_count,

        CASE

            WHEN
            (

                v.invalid_order_id_count
              + d.duplicate_order_id_count
              + v.missing_purchase_timestamp_count
              + v.missing_customer_id_count
              + v.missing_approval_timestamp_count
              + v.missing_carrier_timestamp_count
              + v.missing_customer_delivery_timestamp_count
              + v.purchase_after_approval_count
              + v.approval_after_carrier_count
              + v.carrier_after_customer_count
              + v.missing_estimated_date_count
              + v.estimated_before_purchase_count
              + v.system_date_mismatch_count

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
        invalid_order_id,
        duplicate_order_id,
        missing_purchase_timestamp,
        missing_customer_id,
        missing_approval_timestamp,
        missing_carrier_timestamp,
        missing_customer_delivery_timestamp,
        purchase_after_approval,
        approval_after_carrier,
        carrier_after_customer,
        missing_estimated_date,
        estimated_before_purchase,
        invalid_timestamp_flag,
        system_date_mismatch,
        validation_status,
    ) = result

    # ==========================================================
    # Critical Errors (ETL / Pipeline)
    # ==========================================================

    critical_errors = (
        invalid_order_id +
        duplicate_order_id +
        missing_purchase_timestamp +
        missing_customer_id +
        invalid_timestamp_flag +
        system_date_mismatch
    )

    # ==========================================================
    # Source Data Warnings
    # ==========================================================

    warnings = (
        missing_approval_timestamp +
        missing_carrier_timestamp +
        missing_customer_delivery_timestamp +
        purchase_after_approval +
        approval_after_carrier +
        carrier_after_customer +
        missing_estimated_date +
        estimated_before_purchase
    )

    # ==========================================================
    # Overall Status
    # ==========================================================

    if critical_errors == 0:

        if warnings == 0:
            validation_status = "PASSED"

        else:
            validation_status = "PASSED WITH WARNINGS"

    else:
        validation_status = "FAILED"

    # ==========================================================
    # Print Report
    # ==========================================================

    print("=" * 70)
    print("Critical Errors")
    print("=" * 70)

    critical_metrics = {

        "Invalid order_id": invalid_order_id,
        "Duplicate order_id": duplicate_order_id,
        "Missing purchase timestamp": missing_purchase_timestamp,
        "Missing customer_id": missing_customer_id,
        "Invalid timestamp flag": invalid_timestamp_flag,
        "System date mismatch": system_date_mismatch,

    }

    print_validation_summary(
        critical_metrics,
        "PASSED" if critical_errors == 0 else "FAILED"
    )

    print()

    print("=" * 70)
    print("Source Data Warnings")
    print("=" * 70)

    warning_metrics = {

        "Missing approval timestamp": missing_approval_timestamp,
        "Missing carrier timestamp": missing_carrier_timestamp,
        "Missing customer delivery": missing_customer_delivery_timestamp,
        "Purchase > Approval": purchase_after_approval,
        "Approval > Carrier": approval_after_carrier,
        "Carrier > Delivered": carrier_after_customer,
        "Missing estimated date": missing_estimated_date,
        "Estimated <= Purchase": estimated_before_purchase,

    }

    print_validation_summary(
        warning_metrics,
        "WARNING" if warnings > 0 else "NONE"
    )

    print()
    print("=" * 70)
    print(f"Overall Validation Status : {validation_status}")
    print("=" * 70)

    return validation_status