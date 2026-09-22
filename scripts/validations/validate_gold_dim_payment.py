"""
============================================================
Gold Layer Validation

Table
------------------------------------------------------------
gold.dim_payment

Purpose
------------------------------------------------------------
Validate Gold Payment Dimension business rules.

Grain
------------------------------------------------------------
One row = One payment dimension record

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_gold_dim_payment():

    print_validation_header("gold.dim_payment")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Surrogate Key
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN payment_key IS NULL
                    THEN 1
                END
            ) AS missing_payment_key_count,

            --------------------------------------------------
            -- Payment Type
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN payment_type IS NULL
                      OR TRIM(payment_type) = ''
                    THEN 1
                END
            ) AS missing_payment_type_count,

            --------------------------------------------------
            -- Payment Installments
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN payment_installments <= 0
                    THEN 1
                END
            ) AS missing_payment_installments_count,

            COUNT(
                CASE
                    WHEN payment_installments <= 0
                    THEN 1
                END
            ) AS invalid_payment_installments_count
        FROM gold.dim_payment

    ),

    duplicate_payment_key_checks AS (

        SELECT

            COUNT(*) AS duplicate_payment_key_count

        FROM (

            SELECT payment_key

            FROM gold.dim_payment

            GROUP BY payment_key

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,

        --------------------------------------------------
        -- Surrogate Key
        --------------------------------------------------

        v.missing_payment_key_count,
        pk.duplicate_payment_key_count,

        --------------------------------------------------
        -- Payment Attributes
        --------------------------------------------------

        v.missing_payment_type_count,

        v.missing_payment_installments_count,
        v.invalid_payment_installments_count,


        --------------------------------------------------
        -- Overall Validation
        --------------------------------------------------

        CASE

            WHEN
            (
                v.missing_payment_key_count
              + pk.duplicate_payment_key_count

              + v.missing_payment_type_count

              + v.missing_payment_installments_count
              + v.invalid_payment_installments_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_payment_key_checks pk;
    """

    result = fetch_one(sql)

    (
        total_records,

        missing_payment_key,
        duplicate_payment_key,

        missing_payment_type,

        missing_payment_installments,
        invalid_payment_installments,

        validation_status,
    ) = result

    metrics = {

        "Total Records": total_records,

        "Missing payment_key": missing_payment_key,
        "Duplicate payment_key": duplicate_payment_key,

        "Missing payment_type": missing_payment_type,

        "Missing payment_installments":
            missing_payment_installments,

        "Invalid payment_installments":
            invalid_payment_installments,

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status