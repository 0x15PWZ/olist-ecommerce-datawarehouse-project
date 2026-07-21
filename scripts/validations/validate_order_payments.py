"""
============================================================
Silver Layer Validation

Validate silver.order_payments

Purpose
------------------------------------------------------------
Perform data quality validation for the Silver Order Payments
table and print a validation report.
============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_order_payments():
    """
    Validate silver.order_payments.
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
                    WHEN payment_sequential IS NULL
                    THEN 1
                END
            ) AS null_payment_sequential_count,

            COUNT(
                CASE
                    WHEN payment_type IS NULL
                      OR TRIM(payment_type) = ''
                    THEN 1
                END
            ) AS missing_payment_type_count,

            COUNT(
                CASE
                    WHEN payment_type = 'NOT_DEFINED'
                    THEN 1
                END
            ) AS undefined_payment_type_count,

            COUNT(
                CASE
                    WHEN payment_type = 'CREDIT_CARD'
                     AND (
                            payment_installments IS NULL
                            OR payment_installments < 1
                         )
                    THEN 1
                END
            ) AS credit_card_invalid_installments_count,

            COUNT(
                CASE
                    WHEN payment_type IN ('BOLETO','DEBIT_CARD')
                     AND payment_installments <> 1
                    THEN 1
                END
            ) AS single_payment_method_multi_installment_count,

            COUNT(
                CASE
                    WHEN payment_installments IS NULL
                      OR payment_installments < 0
                    THEN 1
                END
            ) AS negative_or_null_installments_count,

            COUNT(
                CASE
                    WHEN payment_type IN
                        ('BOLETO','DEBIT_CARD','CREDIT_CARD')
                     AND (
                            payment_value IS NULL
                            OR payment_value <= 0
                         )
                    THEN 1
                END
            ) AS paid_methods_zero_or_negative_value_count,

            COUNT(
                CASE
                    WHEN payment_type = 'VOUCHER'
                     AND (
                            payment_value IS NULL
                            OR payment_value < 0
                         )
                    THEN 1
                END
            ) AS voucher_negative_value_count,

            COUNT(
                CASE
                    WHEN payment_sequential <= 0
                    THEN 1
                END
            ) AS invalid_payment_sequential_range_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM silver.order_payments

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_pk_combination_count

        FROM (

            SELECT
                order_id,
                payment_sequential

            FROM silver.order_payments

            WHERE
                order_id IS NOT NULL
                AND payment_sequential IS NOT NULL

            GROUP BY
                order_id,
                payment_sequential

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,
        v.missing_order_id_count,
        v.null_payment_sequential_count,
        d.duplicate_pk_combination_count,
        v.missing_payment_type_count,
        v.undefined_payment_type_count,
        v.invalid_payment_sequential_range_count,
        v.negative_or_null_installments_count,
        v.credit_card_invalid_installments_count,
        v.single_payment_method_multi_installment_count,
        v.paid_methods_zero_or_negative_value_count,
        v.voucher_negative_value_count,
        v.system_date_mismatch_count,

        CASE

            WHEN (

                v.missing_order_id_count
                + v.null_payment_sequential_count
                + d.duplicate_pk_combination_count
                + v.missing_payment_type_count
                + v.undefined_payment_type_count
                + v.invalid_payment_sequential_range_count
                + v.negative_or_null_installments_count
                + v.credit_card_invalid_installments_count
                + v.single_payment_method_multi_installment_count
                + v.paid_methods_zero_or_negative_value_count
                + v.voucher_negative_value_count
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
        null_payment_sequential,
        duplicate_pk,
        missing_payment_type,
        undefined_payment_type,
        invalid_payment_sequential,
        negative_installments,
        invalid_credit_card_installments,
        invalid_single_payment_installments,
        invalid_paid_payment_value,
        invalid_voucher_value,
        system_date_mismatch,
        validation_status
    ) = result

    # ==========================================================
    # Critical Errors (ETL / Pipeline)
    # ==========================================================
    # Note: undefined_payment_type is removed from here
    critical_errors = (
        missing_order_id +
        null_payment_sequential +
        duplicate_pk +
        missing_payment_type +
        invalid_payment_sequential +
        invalid_paid_payment_value +
        system_date_mismatch +
        negative_installments
    )

    # ==========================================================
    # Source Data Warnings
    # ==========================================================
    # Note: undefined_payment_type is added here
    warnings = (
        undefined_payment_type +
        invalid_credit_card_installments +
        invalid_single_payment_installments +
        invalid_voucher_value
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
    # Printing Results
    # ==========================================================
    print_validation_header("silver.order_payments")

    critical_metrics = {
        "Missing order_id": missing_order_id,
        "NULL payment_sequential": null_payment_sequential,
        "Duplicate PK (order_id + payment_sequential)": duplicate_pk,
        "Missing payment_type": missing_payment_type,
        "Invalid payment_sequential": invalid_payment_sequential,
        "Negative/NULL installments": negative_installments, 
        "Invalid payment_value": invalid_paid_payment_value,
        "Update > Create": system_date_mismatch,      
    }

    print_validation_summary(
        critical_metrics,
        "PASSED" if critical_errors == 0 else "FAILED"
    )

    print("=" * 70)
    print("Source Data Warnings")
    print("=" * 70)

    warning_metrics = {
        "Undefined payment_type": undefined_payment_type,
        "Invalid CREDIT_CARD installments": invalid_credit_card_installments,
        "Negative voucher value": invalid_voucher_value,
        "BOLETO/DEBIT_CARD installments != 1": invalid_single_payment_installments,
    }

    print_validation_summary(
        warning_metrics,
        "WARNING" if warnings > 0 else "NONE"
    )

    print("=" * 70)
    print(f"Overall Validation Status : {validation_status}")
    print("=" * 70)

    return validation_status