"""
============================================================
Gold Layer Validation

Table
------------------------------------------------------------
gold.dim_review

Purpose
------------------------------------------------------------
Validate Gold Review Dimension business rules.

Grain
------------------------------------------------------------
One row = One review dimension record

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_gold_dim_review():

    print_validation_header("gold.dim_review")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Surrogate Key
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN review_key IS NULL
                    THEN 1
                END
            ) AS missing_review_key_count,

            --------------------------------------------------
            -- Review Score
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN review_score IS NULL
                    THEN 1
                END
            ) AS missing_review_score_count,

            COUNT(
                CASE
                    WHEN review_score IS NOT NULL
                     AND review_score NOT BETWEEN 1 AND 5
                    THEN 1
                END
            ) AS invalid_review_score_count,

            --------------------------------------------------
            -- Review Comment Title
            -- Optional attribute
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN review_comment_title IS NOT NULL
                     AND LENGTH(TRIM(review_comment_title)) > 100
                    THEN 1
                END
            ) AS invalid_review_title_length_count,

            --------------------------------------------------
            -- Review Comment Message
            -- Optional attribute
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN review_comment_message IS NOT NULL
                     AND LENGTH(TRIM(review_comment_message)) > 1000
                    THEN 1
                END
            ) AS invalid_review_message_length_count,

            --------------------------------------------------
            -- Review Creation Date
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN review_creation_date IS NULL
                    THEN 1
                END
            ) AS missing_review_creation_date_count,

            --------------------------------------------------
            -- Review Answer Date
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN review_answer_timestamp IS NOT NULL
                     AND review_creation_date IS NOT NULL
                     AND review_answer_timestamp
                         < review_creation_date
                    THEN 1
                END
            ) AS invalid_review_answer_date_count,

            --------------------------------------------------
            -- Metadata
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM gold.dim_review

    ),

    duplicate_review_key_checks AS (

        SELECT

            COUNT(*) AS duplicate_review_key_count

        FROM (

            SELECT review_key

            FROM gold.dim_review

            GROUP BY review_key

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,

        --------------------------------------------------
        -- Surrogate Key
        --------------------------------------------------

        v.missing_review_key_count,
        rk.duplicate_review_key_count,

        --------------------------------------------------
        -- Review Score
        --------------------------------------------------

        v.missing_review_score_count,
        v.invalid_review_score_count,

        --------------------------------------------------
        -- Review Text
        --------------------------------------------------

        v.invalid_review_title_length_count,
        v.invalid_review_message_length_count,

        --------------------------------------------------
        -- Review Dates
        --------------------------------------------------

        v.missing_review_creation_date_count,
        v.invalid_review_answer_date_count,

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
                v.missing_review_key_count
              + rk.duplicate_review_key_count

              + v.missing_review_score_count
              + v.invalid_review_score_count

              + v.invalid_review_title_length_count
              + v.invalid_review_message_length_count

              + v.missing_review_creation_date_count
              + v.invalid_review_answer_date_count

              + v.system_date_mismatch_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_review_key_checks rk;
    """

    result = fetch_one(sql)

    (
        total_records,

        missing_review_key,
        duplicate_review_key,

        missing_review_score,
        invalid_review_score,

        invalid_review_title_length,
        invalid_review_message_length,

        missing_review_creation_date,
        invalid_review_answer_date,

        system_date_mismatch,

        validation_status,
    ) = result

    metrics = {

        "Total Records": total_records,

        "Missing review_key": missing_review_key,
        "Duplicate review_key": duplicate_review_key,

        "Missing review_score": missing_review_score,
        "Invalid review_score": invalid_review_score,

        "Invalid review title length":
            invalid_review_title_length,

        "Invalid review message length":
            invalid_review_message_length,

        "Missing review_creation_date":
            missing_review_creation_date,

        "Invalid review_answer_timestamp":
            invalid_review_answer_date,

        "Update < Create":
            system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status