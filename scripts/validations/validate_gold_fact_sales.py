"""
============================================================
Gold Layer Validation

Table
------------------------------------------------------------
gold.fact_sales

Purpose
------------------------------------------------------------
Validate Gold Sales Fact business rules.

Grain
------------------------------------------------------------
One row = One order item / sales line

============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_gold_fact_sales():

    print_validation_header("gold.fact_sales")

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Business Keys
            --------------------------------------------------

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
            ) AS missing_order_item_id_count,

            --------------------------------------------------
            -- Mandatory Dimension Foreign Keys
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN customer_key IS NULL
                    THEN 1
                END
            ) AS missing_customer_key_count,

            COUNT(
                CASE
                    WHEN product_key IS NULL
                    THEN 1
                END
            ) AS missing_product_key_count,

            COUNT(
                CASE
                    WHEN seller_key IS NULL
                    THEN 1
                END
            ) AS missing_seller_key_count,

            --------------------------------------------------
            -- Purchase Date
            --
            -- Purchase date is mandatory.
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN purchase_date_key IS NULL
                    THEN 1
                END
            ) AS missing_purchase_date_key_count,

            --------------------------------------------------
            -- Optional Order Lifecycle Dates
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN approval_date_key IS NULL
                    THEN 1
                END
            ) AS missing_approval_date_key_count,

            COUNT(
                CASE
                    WHEN carrier_date_key IS NULL
                    THEN 1
                END
            ) AS missing_carrier_date_key_count,

            COUNT(
                CASE
                    WHEN delivered_date_key IS NULL
                    THEN 1
                END
            ) AS missing_delivered_date_key_count,

            --------------------------------------------------
            -- Estimated Delivery Date
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN estimated_delivery_date_key IS NULL
                    THEN 1
                END
            ) AS missing_estimated_delivery_date_key_count,

            --------------------------------------------------
            -- Sales Measures
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN price IS NULL
                    THEN 1
                END
            ) AS missing_price_count,

            COUNT(
                CASE
                    WHEN price IS NOT NULL
                     AND price < 0
                    THEN 1
                END
            ) AS invalid_price_count,

            COUNT(
                CASE
                    WHEN freight_value IS NULL
                    THEN 1
                END
            ) AS missing_freight_value_count,

            COUNT(
                CASE
                    WHEN freight_value IS NOT NULL
                     AND freight_value < 0
                    THEN 1
                END
            ) AS invalid_freight_value_count,

            --------------------------------------------------
            -- Order Status
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN order_status IS NULL
                      OR TRIM(order_status) = ''
                    THEN 1
                END
            ) AS missing_order_status_count,

            --------------------------------------------------
            -- Shipping Limit Date
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN shipping_limit_date IS NULL
                    THEN 1
                END
            ) AS missing_shipping_limit_date_count,

            --------------------------------------------------
            -- Metadata
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM gold.fact_sales

    ),

    ----------------------------------------------------------
    -- Fact Grain Validation
    ----------------------------------------------------------

    duplicate_fact_grain_checks AS (

        SELECT

            COUNT(*) AS duplicate_fact_grain_count

        FROM (

            SELECT
                order_id,
                order_item_id

            FROM gold.fact_sales

            GROUP BY
                order_id,
                order_item_id

            HAVING COUNT(*) > 1

        ) t

    ),

    ----------------------------------------------------------
    -- Customer FK
    ----------------------------------------------------------

    customer_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_customer_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_customers d
            ON f.customer_key = d.customer_key

        WHERE d.customer_key IS NULL

    ),

    ----------------------------------------------------------
    -- Product FK
    ----------------------------------------------------------

    product_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_product_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_products d
            ON f.product_key = d.product_key

        WHERE d.product_key IS NULL

    ),

    ----------------------------------------------------------
    -- Seller FK
    ----------------------------------------------------------

    seller_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_seller_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_sellers d
            ON f.seller_key = d.seller_key

        WHERE d.seller_key IS NULL

    ),

    ----------------------------------------------------------
    -- Purchase Date FK
    ----------------------------------------------------------

    purchase_date_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_purchase_date_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_date d
            ON f.purchase_date_key = d.date_key

        WHERE d.date_key IS NULL

    ),

    ----------------------------------------------------------
    -- Approval Date FK
    ----------------------------------------------------------

    approval_date_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_approval_date_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_date d
            ON f.approval_date_key = d.date_key

        WHERE f.approval_date_key IS NOT NULL
          AND d.date_key IS NULL

    ),

    ----------------------------------------------------------
    -- Carrier Date FK
    ----------------------------------------------------------

    carrier_date_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_carrier_date_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_date d
            ON f.carrier_date_key = d.date_key

        WHERE f.carrier_date_key IS NOT NULL
          AND d.date_key IS NULL

    ),

    ----------------------------------------------------------
    -- Delivered Date FK
    ----------------------------------------------------------

    delivered_date_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_delivered_date_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_date d
            ON f.delivered_date_key = d.date_key

        WHERE f.delivered_date_key IS NOT NULL
          AND d.date_key IS NULL

    ),

    ----------------------------------------------------------
    -- Estimated Delivery Date FK
    ----------------------------------------------------------

    estimated_delivery_date_fk_checks AS (

        SELECT
            COUNT(*) AS invalid_estimated_delivery_date_fk_count

        FROM gold.fact_sales f

        LEFT JOIN gold.dim_date d
            ON f.estimated_delivery_date_key = d.date_key

        WHERE f.estimated_delivery_date_key IS NOT NULL
          AND d.date_key IS NULL

    )

    SELECT

        v.total_records,

        --------------------------------------------------
        -- Fact Grain
        --------------------------------------------------

        v.missing_order_id_count,
        v.missing_order_item_id_count,
        fg.duplicate_fact_grain_count,

        --------------------------------------------------
        -- Customer
        --------------------------------------------------

        v.missing_customer_key_count,
        cf.invalid_customer_fk_count,

        --------------------------------------------------
        -- Product
        --------------------------------------------------

        v.missing_product_key_count,
        pf.invalid_product_fk_count,

        --------------------------------------------------
        -- Seller
        --------------------------------------------------

        v.missing_seller_key_count,
        sf.invalid_seller_fk_count,

        --------------------------------------------------
        -- Purchase Date
        --------------------------------------------------

        v.missing_purchase_date_key_count,
        pdf.invalid_purchase_date_fk_count,

        --------------------------------------------------
        -- Approval Date
        --------------------------------------------------

        v.missing_approval_date_key_count,
        adf.invalid_approval_date_fk_count,

        --------------------------------------------------
        -- Carrier Date
        --------------------------------------------------

        v.missing_carrier_date_key_count,
        cdf.invalid_carrier_date_fk_count,

        --------------------------------------------------
        -- Delivered Date
        --------------------------------------------------

        v.missing_delivered_date_key_count,
        ddf.invalid_delivered_date_fk_count,

        --------------------------------------------------
        -- Estimated Delivery Date
        --------------------------------------------------

        v.missing_estimated_delivery_date_key_count,
        edf.invalid_estimated_delivery_date_fk_count,

        --------------------------------------------------
        -- Measures
        --------------------------------------------------

        v.missing_price_count,
        v.invalid_price_count,

        v.missing_freight_value_count,
        v.invalid_freight_value_count,

        --------------------------------------------------
        -- Attributes
        --------------------------------------------------

        v.missing_order_status_count,
        v.missing_shipping_limit_date_count,

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
                v.missing_order_id_count
              + v.missing_order_item_id_count
              + fg.duplicate_fact_grain_count

              + v.missing_customer_key_count
              + cf.invalid_customer_fk_count

              + v.missing_product_key_count
              + pf.invalid_product_fk_count

              + v.missing_seller_key_count
              + sf.invalid_seller_fk_count

              + v.missing_purchase_date_key_count
              + pdf.invalid_purchase_date_fk_count

              + adf.invalid_approval_date_fk_count

              + cdf.invalid_carrier_date_fk_count

              + ddf.invalid_delivered_date_fk_count

              + edf.invalid_estimated_delivery_date_fk_count

              + v.missing_price_count
              + v.invalid_price_count

              + v.missing_freight_value_count
              + v.invalid_freight_value_count

              + v.missing_order_status_count
              + v.missing_shipping_limit_date_count

              + v.system_date_mismatch_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN duplicate_fact_grain_checks fg

    CROSS JOIN customer_fk_checks cf
    CROSS JOIN product_fk_checks pf
    CROSS JOIN seller_fk_checks sf

    CROSS JOIN purchase_date_fk_checks pdf
    CROSS JOIN approval_date_fk_checks adf
    CROSS JOIN carrier_date_fk_checks cdf
    CROSS JOIN delivered_date_fk_checks ddf
    CROSS JOIN estimated_delivery_date_fk_checks edf;
    """

    result = fetch_one(sql)

    (
        total_records,

        missing_order_id,
        missing_order_item_id,
        duplicate_fact_grain,

        missing_customer_key,
        invalid_customer_fk,

        missing_product_key,
        invalid_product_fk,

        missing_seller_key,
        invalid_seller_fk,

        missing_purchase_date_key,
        invalid_purchase_date_fk,

        missing_approval_date_key,
        invalid_approval_date_fk,

        missing_carrier_date_key,
        invalid_carrier_date_fk,

        missing_delivered_date_key,
        invalid_delivered_date_fk,

        missing_estimated_delivery_date_key,
        invalid_estimated_delivery_date_fk,

        missing_price,
        invalid_price,

        missing_freight_value,
        invalid_freight_value,

        missing_order_status,
        missing_shipping_limit_date,

        system_date_mismatch,

        validation_status,
    ) = result

    metrics = {

        "Total Records":
            total_records,

        "Missing order_id":
            missing_order_id,

        "Missing order_item_id":
            missing_order_item_id,

        "Duplicate order_id + order_item_id":
            duplicate_fact_grain,

        "Missing customer_key":
            missing_customer_key,

        "Invalid customer_key FK":
            invalid_customer_fk,

        "Missing product_key":
            missing_product_key,

        "Invalid product_key FK":
            invalid_product_fk,

        "Missing seller_key":
            missing_seller_key,

        "Invalid seller_key FK":
            invalid_seller_fk,

        "Missing purchase_date_key":
            missing_purchase_date_key,

        "Invalid purchase_date_key FK":
            invalid_purchase_date_fk,

        "Missing approval_date_key (Info)":
            missing_approval_date_key,

        "Invalid approval_date_key FK":
            invalid_approval_date_fk,

        "Missing carrier_date_key (Info)":
            missing_carrier_date_key,

        "Invalid carrier_date_key FK":
            invalid_carrier_date_fk,

        "Missing delivered_date_key (Info)":
            missing_delivered_date_key,

        "Invalid delivered_date_key FK":
            invalid_delivered_date_fk,

        "Missing estimated_delivery_date_key (Info)":
            missing_estimated_delivery_date_key,

        "Invalid estimated_delivery_date_key FK":
            invalid_estimated_delivery_date_fk,

        "Missing price":
            missing_price,

        "Invalid price":
            invalid_price,

        "Missing freight_value":
            missing_freight_value,

        "Invalid freight_value":
            invalid_freight_value,

        "Missing order_status":
            missing_order_status,

        "Missing shipping_limit_date":
            missing_shipping_limit_date,

        "Update < Create":
            system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status