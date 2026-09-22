"""
============================================================
Gold Layer Validation

Table
------------------------------------------------------------
gold.dim_products

Purpose
------------------------------------------------------------
Validate Gold Product Dimension business rules.

Grain
------------------------------------------------------------
One row = One product

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_gold_dim_products():

    print_validation_header("gold.dim_products")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Surrogate Key Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_key IS NULL
                    THEN 1
                END
            ) AS missing_product_key_count,

            --------------------------------------------------
            -- Business Key Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_id IS NULL
                      OR TRIM(product_id) = ''
                    THEN 1
                END
            ) AS missing_product_id_count,

            --------------------------------------------------
            -- Product Name Length
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_name_length IS NOT NULL
                     AND product_name_length < 0
                    THEN 1
                END
            ) AS invalid_product_name_length_count,

            --------------------------------------------------
            -- Product Description Length
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_description_length IS NOT NULL
                     AND product_description_length < 0
                    THEN 1
                END
            ) AS invalid_product_description_length_count,

            --------------------------------------------------
            -- Product Photos
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_photos_qty IS NOT NULL
                     AND product_photos_qty < 0
                    THEN 1
                END
            ) AS invalid_product_photos_qty_count,

            --------------------------------------------------
            -- Product Weight
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_weight_g IS NOT NULL
                     AND product_weight_g <= 0
                    THEN 1
                END
            ) AS invalid_product_weight_count,

            --------------------------------------------------
            -- Product Length
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_length_cm IS NOT NULL
                     AND product_length_cm <= 0
                    THEN 1
                END
            ) AS invalid_product_length_count,

            --------------------------------------------------
            -- Product Height
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_height_cm IS NOT NULL
                     AND product_height_cm <= 0
                    THEN 1
                END
            ) AS invalid_product_height_count,

            --------------------------------------------------
            -- Product Width
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN product_width_cm IS NOT NULL
                     AND product_width_cm <= 0
                    THEN 1
                END
            ) AS invalid_product_width_count,

            --------------------------------------------------
            -- Metadata Validation
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM gold.dim_products

    ),

    duplicate_product_key_checks AS (

        SELECT

            COUNT(*) AS duplicate_product_key_count

        FROM (

            SELECT product_key

            FROM gold.dim_products

            GROUP BY product_key

            HAVING COUNT(*) > 1

        ) t

    ),

    duplicate_product_id_checks AS (

        SELECT

            COUNT(*) AS duplicate_product_id_count

        FROM (

            SELECT product_id

            FROM gold.dim_products

            GROUP BY product_id

            HAVING COUNT(*) > 1

        ) t

    )

    SELECT

        v.total_records,

        --------------------------------------------------
        -- Surrogate Key
        --------------------------------------------------

        v.missing_product_key_count,
        pk.duplicate_product_key_count,

        --------------------------------------------------
        -- Business Key
        --------------------------------------------------

        v.missing_product_id_count,
        pi.duplicate_product_id_count,

        --------------------------------------------------
        -- Product Attributes
        --------------------------------------------------

        v.invalid_product_name_length_count,
        v.invalid_product_description_length_count,
        v.invalid_product_photos_qty_count,

        v.invalid_product_weight_count,
        v.invalid_product_length_count,
        v.invalid_product_height_count,
        v.invalid_product_width_count,

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
                v.missing_product_key_count
              + pk.duplicate_product_key_count

              + v.missing_product_id_count
              + pi.duplicate_product_id_count


              + v.invalid_product_name_length_count
              + v.invalid_product_description_length_count
              + v.invalid_product_photos_qty_count

              + v.invalid_product_weight_count
              + v.invalid_product_length_count
              + v.invalid_product_height_count
              + v.invalid_product_width_count

              + v.system_date_mismatch_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_product_key_checks pk

    CROSS JOIN duplicate_product_id_checks pi;
    """

    result = fetch_one(sql)

    (
        total_records,

        missing_product_key,
        duplicate_product_key,

        missing_product_id,
        duplicate_product_id,

        invalid_product_name_length,
        invalid_product_description_length,
        invalid_product_photos_qty,

        invalid_product_weight,
        invalid_product_length,
        invalid_product_height,
        invalid_product_width,

        system_date_mismatch,

        validation_status,
    ) = result

    metrics = {

        "Total Records": total_records,

        "Missing product_key": missing_product_key,
        "Duplicate product_key": duplicate_product_key,

        "Missing product_id": missing_product_id,
        "Duplicate product_id": duplicate_product_id,

        "Invalid product_name_length":
            invalid_product_name_length,

        "Invalid product_description_length":
            invalid_product_description_length,

        "Invalid product_photos_qty":
            invalid_product_photos_qty,

        "Invalid product_weight_g":
            invalid_product_weight,

        "Invalid product_length_cm":
            invalid_product_length,

        "Invalid product_height_cm":
            invalid_product_height,

        "Invalid product_width_cm":
            invalid_product_width,

        "Update < Create": system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status