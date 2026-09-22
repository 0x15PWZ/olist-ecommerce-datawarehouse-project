"""
============================================================
Gold Layer Business Validation

Table
------------------------------------------------------------
gold.fact_sales

Purpose
------------------------------------------------------------
Validate business rules and chronological relationships
within the Gold Sales Fact.

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


def validate_gold_fact_sales_business():

    print_validation_header(
        "gold.fact_sales - Business Rules"
    )

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            --------------------------------------------------
            -- Rule 1
            -- Order Item ID must be positive
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN order_item_id <= 0
                    THEN 1
                END
            ) AS invalid_order_item_id_count,

            --------------------------------------------------
            -- Rule 2
            -- Price must not be negative
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN price < 0
                    THEN 1
                END
            ) AS invalid_price_count,

            --------------------------------------------------
            -- Rule 3
            -- Freight value must not be negative
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN freight_value < 0
                    THEN 1
                END
            ) AS invalid_freight_value_count,

            --------------------------------------------------
            -- Rule 4
            -- Shipping limit date must exist
            --
            -- Already checked structurally, but retained
            -- here because it is a business requirement.
            --------------------------------------------------

            COUNT(
                CASE
                    WHEN shipping_limit_date IS NULL
                    THEN 1
                END
            ) AS missing_shipping_limit_date_count

        FROM gold.fact_sales

    ),

    ----------------------------------------------------------
    -- Rule 5
    -- Purchase Date <= Shipping Limit Date
    ----------------------------------------------------------

    shipping_date_checks AS (

        SELECT
            COUNT(*) AS invalid_shipping_limit_date_count

        FROM gold.fact_sales f

        JOIN gold.dim_date d
            ON f.purchase_date_key = d.date_key

        WHERE f.shipping_limit_date::date < d.full_date

    ),

    ----------------------------------------------------------
    -- Rule 6
    -- Purchase Date <= Approval Date
    ----------------------------------------------------------

    approval_date_checks AS (

        SELECT
            COUNT(*) AS invalid_approval_date_count

        FROM gold.fact_sales f

        JOIN gold.dim_date purchase_date
            ON f.purchase_date_key = purchase_date.date_key

        JOIN gold.dim_date approval_date
            ON f.approval_date_key = approval_date.date_key

        WHERE f.approval_date_key IS NOT NULL
          AND approval_date.full_date < purchase_date.full_date

    ),

    ----------------------------------------------------------
    -- Rule 7
    -- Purchase Date <= Carrier Date
    ----------------------------------------------------------

    carrier_date_checks AS (

        SELECT
            COUNT(*) AS invalid_carrier_date_count

        FROM gold.fact_sales f

        JOIN gold.dim_date purchase_date
            ON f.purchase_date_key = purchase_date.date_key

        JOIN gold.dim_date carrier_date
            ON f.carrier_date_key = carrier_date.date_key

        WHERE f.carrier_date_key IS NOT NULL
          AND carrier_date.full_date < purchase_date.full_date

    ),

    ----------------------------------------------------------
    -- Rule 8
    -- Purchase Date <= Delivered Date
    ----------------------------------------------------------

    delivered_date_checks AS (

        SELECT
            COUNT(*) AS invalid_delivered_date_count

        FROM gold.fact_sales f

        JOIN gold.dim_date purchase_date
            ON f.purchase_date_key = purchase_date.date_key

        JOIN gold.dim_date delivered_date
            ON f.delivered_date_key = delivered_date.date_key

        WHERE f.delivered_date_key IS NOT NULL
          AND delivered_date.full_date < purchase_date.full_date

    ),

    ----------------------------------------------------------
    -- Rule 9
    -- Purchase Date <= Estimated Delivery Date
    ----------------------------------------------------------

    estimated_delivery_checks AS (

        SELECT
            COUNT(*) AS invalid_estimated_delivery_date_count

        FROM gold.fact_sales f

        JOIN gold.dim_date purchase_date
            ON f.purchase_date_key = purchase_date.date_key

        JOIN gold.dim_date estimated_date
            ON f.estimated_delivery_date_key =
               estimated_date.date_key

        WHERE f.estimated_delivery_date_key IS NOT NULL
          AND estimated_date.full_date < purchase_date.full_date

    ),

    ----------------------------------------------------------
    -- Rule 10
    -- Approval Date <= Carrier Date
    ----------------------------------------------------------

    approval_carrier_checks AS (

        SELECT
            COUNT(*) AS invalid_approval_carrier_date_count

        FROM gold.fact_sales f

        JOIN gold.dim_date approval_date
            ON f.approval_date_key = approval_date.date_key

        JOIN gold.dim_date carrier_date
            ON f.carrier_date_key = carrier_date.date_key

        WHERE f.approval_date_key IS NOT NULL
          AND f.carrier_date_key IS NOT NULL
          AND carrier_date.full_date < approval_date.full_date

    ),

    ----------------------------------------------------------
    -- Rule 11
    -- Carrier Date <= Delivered Date
    ----------------------------------------------------------

    carrier_delivered_checks AS (

        SELECT
            COUNT(*) AS invalid_carrier_delivered_date_count

        FROM gold.fact_sales f

        JOIN gold.dim_date carrier_date
            ON f.carrier_date_key = carrier_date.date_key

        JOIN gold.dim_date delivered_date
            ON f.delivered_date_key = delivered_date.date_key

        WHERE f.carrier_date_key IS NOT NULL
          AND f.delivered_date_key IS NOT NULL
          AND delivered_date.full_date < carrier_date.full_date

    ),

    ----------------------------------------------------------
    -- Rule 13
    -- Create Date <= Update Date
    ----------------------------------------------------------

    system_date_checks AS (

        SELECT
            COUNT(*) AS invalid_system_date_count

        FROM gold.fact_sales

        WHERE update_date < create_date

    )

    SELECT

        v.total_records,

        --------------------------------------------------
        -- Basic Business Rules
        --------------------------------------------------

        v.invalid_order_item_id_count,
        v.invalid_price_count,
        v.invalid_freight_value_count,
        v.missing_shipping_limit_date_count,

        --------------------------------------------------
        -- Order Lifecycle
        --------------------------------------------------

        s.invalid_shipping_limit_date_count,
        a.invalid_approval_date_count,
        c.invalid_carrier_date_count,
        d.invalid_delivered_date_count,
        e.invalid_estimated_delivery_date_count,

        --------------------------------------------------
        -- Lifecycle Relationships
        --------------------------------------------------

        ac.invalid_approval_carrier_date_count,
        cd.invalid_carrier_delivered_date_count,
        --------------------------------------------------
        -- Metadata
        --------------------------------------------------

        sd.invalid_system_date_count,

        --------------------------------------------------
        -- Overall Validation
        --------------------------------------------------

        CASE

            WHEN
            (
                v.invalid_order_item_id_count
              + v.invalid_price_count
              + v.invalid_freight_value_count
              + v.missing_shipping_limit_date_count

              + s.invalid_shipping_limit_date_count
              + a.invalid_approval_date_count
              + c.invalid_carrier_date_count
              + d.invalid_delivered_date_count
              + e.invalid_estimated_delivery_date_count

              + ac.invalid_approval_carrier_date_count
              + cd.invalid_carrier_delivered_date_count

              + sd.invalid_system_date_count

            ) = 0

            THEN 'PASSED'

            ELSE 'FAILED'

        END AS validation_status

    FROM validation_checks v

    CROSS JOIN shipping_date_checks s
    CROSS JOIN approval_date_checks a
    CROSS JOIN carrier_date_checks c
    CROSS JOIN delivered_date_checks d
    CROSS JOIN estimated_delivery_checks e
    CROSS JOIN approval_carrier_checks ac
    CROSS JOIN carrier_delivered_checks cd
    CROSS JOIN system_date_checks sd;
    """

    result = fetch_one(sql)

    (
        total_records,

        invalid_order_item_id,
        invalid_price,
        invalid_freight_value,
        missing_shipping_limit_date,

        invalid_shipping_limit_date,
        invalid_approval_date,
        invalid_carrier_date,
        invalid_delivered_date,
        invalid_estimated_delivery_date,

        invalid_approval_carrier_date,
        invalid_carrier_delivered_date,
        invalid_shipping_carrier_date,

        invalid_system_date,

        validation_status,
    ) = result

    metrics = {

        "Total Records":
            total_records,

        "Invalid order_item_id":
            invalid_order_item_id,

        "Invalid price":
            invalid_price,

        "Invalid freight_value":
            invalid_freight_value,

        "Missing shipping_limit_date":
            missing_shipping_limit_date,

        "Purchase > Shipping Limit":
            invalid_shipping_limit_date,

        "Approval < Purchase":
            invalid_approval_date,

        "Carrier < Purchase":
            invalid_carrier_date,

        "Delivered < Purchase":
            invalid_delivered_date,

        "Estimated Delivery < Purchase":
            invalid_estimated_delivery_date,

        "Carrier < Approval":
            invalid_approval_carrier_date,

        "Delivered < Carrier":
            invalid_carrier_delivered_date,

        "Update < Create":
            invalid_system_date,

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status