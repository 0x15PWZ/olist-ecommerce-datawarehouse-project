"""
============================================================
Silver Layer Validation

Validate silver.order_reviews

Purpose
------------------------------------------------------------
Perform data quality validation for the Silver Order Reviews
table and print a validation report.
============================================================
"""

from scripts.utils.databases import fetch_one
from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_order_reviews():
    """
    Validate silver.order_reviews.
    """

    sql = """
    WITH validation_checks AS (
        SELECT
            COUNT(*) AS total_records,

            COUNT(
                CASE
                    WHEN review_id IS NULL
                      OR TRIM(review_id) = ''
                    THEN 1
                END
            ) AS missing_review_id_count,

            COUNT(
                CASE
                    WHEN order_id IS NULL
                      OR TRIM(order_id) = ''
                    THEN 1
                END
            ) AS missing_order_id_count,

            COUNT(
                CASE
                    WHEN review_score IS NULL
                      OR review_score < 1
                      OR review_score > 5
                    THEN 1
                END
            ) AS invalid_review_score_count,

            COUNT(
                CASE
                    WHEN review_comment_title IS NOT NULL
                     AND TRIM(review_comment_title) = ''
                    THEN 1
                END
            ) AS whitespace_only_title_count,

            COUNT(
                CASE
                    WHEN review_comment_message IS NOT NULL
                     AND TRIM(review_comment_message) = ''
                    THEN 1
                END
            ) AS whitespace_only_message_count,

            COUNT(
                CASE
                    WHEN review_creation_date IS NULL
                    THEN 1
                END
            ) AS missing_review_creation_date_count,

            COUNT(
                CASE
                    WHEN review_answer_timestamp IS NOT NULL
                     AND review_creation_date IS NOT NULL
                     AND review_answer_timestamp::date < review_creation_date
                    THEN 1
                END
            ) AS answer_before_creation_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count
        FROM silver.order_reviews
    ),

    duplicate_checks AS (
        SELECT
            COUNT(*) AS duplicate_review_id_count
        FROM (
            SELECT review_id
            FROM silver.order_reviews
            WHERE review_id IS NOT NULL
            GROUP BY review_id
            HAVING COUNT(*) > 1
        ) t
    )

    SELECT
        v.total_records,
        v.missing_review_id_count,
        d.duplicate_review_id_count,
        v.missing_order_id_count,
        v.invalid_review_score_count,
        v.whitespace_only_title_count,
        v.whitespace_only_message_count,
        v.missing_review_creation_date_count,
        v.answer_before_creation_count,
        v.system_date_mismatch_count,
        CASE
            WHEN (
                v.missing_review_id_count
                + d.duplicate_review_id_count
                + v.missing_order_id_count
                + v.invalid_review_score_count
                + v.whitespace_only_title_count
                + v.whitespace_only_message_count
                + v.missing_review_creation_date_count
                + v.answer_before_creation_count
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
        missing_review_id,
        duplicate_review_id,
        missing_order_id,
        invalid_review_score,
        whitespace_title,
        whitespace_message,
        missing_review_creation_date,
        answer_before_creation,
        system_date_mismatch,
        validation_status
    ) = result

    # Critical errors
    critical_errors = (
        missing_review_id +
        missing_order_id +
        duplicate_review_id +
        invalid_review_score +
        missing_review_creation_date +
        answer_before_creation +
        system_date_mismatch 
    )
    
    # Warnings 
    warnings = (
        whitespace_title +
        whitespace_message
    )
    
    # Overall status calculation
    if critical_errors == 0:
        if warnings == 0:
            validation_status = "PASSED"
        else:
            validation_status = "PASSED WITH WARNINGS"
    else:
        validation_status = "FAILED"

    # Print main critical summary
    print_validation_header("silver.order_reviews")

    critical_metrics = {
        "Missing review_id": missing_review_id,
        "Duplicate review_id": duplicate_review_id,
        "Missing order_id": missing_order_id,
        "Invalid review_score": invalid_review_score,
        "Missing review_creation_date": missing_review_creation_date,
        "Answer before review creation": answer_before_creation,
        "Update < Create": system_date_mismatch
    }

    print_validation_summary(
        critical_metrics,
        "PASSED" if critical_errors == 0 else "FAILED"
    )
    
    # Print warning summary
    print("=" * 70)
    print("Source Data Warnings")
    print("=" * 70)

    warning_metrics = {
        "Whitespace review title": whitespace_title,
        "Whitespace review message": whitespace_message,
    }
    
    # Output the warning details dynamically using your helper
    print_validation_summary(
        warning_metrics,
        "PASSED WITH WARNINGS" if warnings > 0 else "NO WARNINGS"
    )

    return validation_status