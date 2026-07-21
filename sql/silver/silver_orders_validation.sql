
-- This scription for silver.orders table validation

WITH validation_checks AS (
    SELECT
        -- 1. Total Record Metrics
        COUNT(*) AS total_records,
        COUNT(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 END) AS invalid_order_id_count,

        -- 2. Strict Business Rules: Mandatory Core Fields
        COUNT(CASE WHEN order_purchase_timestamp IS NULL THEN 1 END) AS missing_purchase_timestamp_count,
        COUNT(CASE WHEN customer_id IS NULL OR TRIM(customer_id) = '' THEN 1 END) AS missing_customer_id_count,

        -- 3. Strict Business Rules: Conditional Null/Not Null based on your 8 Statuses
        -- Rule A: APPROVED, INVOICED, PROCESSING, SHIPPED, and DELIVERED must have an approval timestamp
        COUNT(CASE 
            WHEN order_status IN ('APPROVED', 'INVOICED', 'PROCESSING', 'SHIPPED', 'DELIVERED') 
                 AND order_approved_at IS NULL THEN 1 
        END) AS missing_approval_timestamp_count,

        -- Rule B: SHIPPED and DELIVERED must have a carrier pickup timestamp
        COUNT(CASE 
            WHEN order_status IN ('SHIPPED', 'DELIVERED') 
                 AND order_delivered_carrier_date IS NULL THEN 1 
        END) AS missing_carrier_timestamp_count,

        -- Rule C: Only DELIVERED orders must have a final customer delivery timestamp
        COUNT(CASE 
            WHEN order_status = 'DELIVERED' 
                 AND order_delivered_customer_date IS NULL THEN 1 
        END) AS missing_customer_delivery_timestamp_count,

        -- 4. Strict Business Rules: Chronological Logic (When timestamps exist)
        COUNT(CASE WHEN order_purchase_timestamp > order_approved_at THEN 1 END) AS rule_purchase_gt_approval_count,
        COUNT(CASE WHEN order_approved_at > order_delivered_carrier_date THEN 1 END) AS rule_approval_gt_carrier_count,
        COUNT(CASE WHEN order_delivered_carrier_date > order_delivered_customer_date THEN 1 END) AS rule_carrier_gt_delivered_count,

        -- 5. Estimated Delivery Date Rules (Derived from your previous questions)
        COUNT(CASE WHEN order_estimated_delivery_date IS NULL THEN 1 END) AS missing_estimated_date_count,
        COUNT(CASE WHEN order_estimated_delivery_date <= order_purchase_timestamp THEN 1 END) AS estimated_date_before_purchase_count,

        -- 6. System Audit & Ingestion Flags
        COUNT(CASE WHEN is_valid_timestamp = FALSE THEN 1 END) AS invalid_timestamp_flag_count,
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count
    FROM silver.orders
),
duplicate_checks AS (
    SELECT COUNT(*) AS duplicate_order_id_count
    FROM (
        SELECT order_id 
        FROM silver.orders 
        GROUP BY order_id 
        HAVING COUNT(*) > 1
    ) sub
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
    v.rule_purchase_gt_approval_count,
    v.rule_approval_gt_carrier_count,
    v.rule_carrier_gt_delivered_count,
    v.missing_estimated_date_count,
    v.estimated_date_before_purchase_count,
    v.invalid_timestamp_flag_count,
    -- Summary evaluation flag
    CASE 
        WHEN (
            v.invalid_order_id_count + d.duplicate_order_id_count + v.missing_purchase_timestamp_count +
            v.missing_customer_id_count + v.missing_approval_timestamp_count + 
            v.missing_carrier_timestamp_count + v.missing_customer_delivery_timestamp_count + 
            v.rule_purchase_gt_approval_count + v.rule_approval_gt_carrier_count + v.rule_carrier_gt_delivered_count +
            v.missing_estimated_date_count + v.estimated_date_before_purchase_count
        ) = 0 THEN 'PASSED' 
        ELSE 'FAILED' 
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d;

--=====================================================================================================================
-- 1. Invalid Order ID Check
-- Identifies records where the primary key order_id is either missing or empty.
SELECT order_id
FROM silver.orders
WHERE order_id IS NULL OR TRIM(order_id) = '';

-- 2. Duplicate Order ID Check
-- Identifies instances where an order_id is duplicated, violating primary key uniqueness.
SELECT order_id
FROM silver.orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- 3. Missing Purchase Timestamp Check
-- Identifies records where the critical transaction date order_purchase_timestamp is completely missing.
SELECT order_id, order_purchase_timestamp
FROM silver.orders
WHERE order_purchase_timestamp IS NULL;

-- 4. Missing Customer ID Check
-- Identifies records that are missing the associated customer_id (orphan orders).
SELECT order_id, customer_id
FROM silver.orders
WHERE customer_id IS NULL OR TRIM(customer_id) = '';

-- 5. Missing Approval Timestamp (Conditional Check)
-- Identifies orders that are past the 'created' stage but are missing their approval timestamp.
SELECT order_id, order_status, order_approved_at
FROM silver.orders
WHERE order_status IN ('APPROVED', 'INVOICED', 'PROCESSING', 'SHIPPED', 'DELIVERED')
  AND order_approved_at IS NULL;
  
-- 6. Missing Carrier Timestamp (Conditional Check)
-- Identifies dispatched or completed orders that are missing their transit hand-off timestamp.
SELECT order_id, order_status, order_delivered_carrier_date
FROM silver.orders
WHERE order_status IN ('SHIPPED', 'DELIVERED')
  AND order_delivered_carrier_date IS NULL;
  
-- 7. Missing Customer Delivery Timestamp (Conditional Check)
-- Identifies orders marked as fully delivered that lack the final delivery receipt timestamp.
SELECT order_id, order_status, order_delivered_customer_date
FROM silver.orders
WHERE order_status = 'DELIVERED'
  AND order_delivered_customer_date IS NULL;
  
-- 8. Purchase Date After Approval Date Check
--Identifies chronological errors where the purchase timestamp is recorded after the approval timestamp.
SELECT order_id, order_purchase_timestamp, order_approved_at
FROM silver.orders
WHERE order_purchase_timestamp > order_approved_at;

-- 9. Approval Date After Carrier Hand-off Check
--Identifies chronological errors where the transit hand-off occurs before the payment or order approval.
SELECT order_id, order_approved_at, order_delivered_carrier_date
FROM silver.orders
WHERE order_approved_at > order_delivered_carrier_date;

-- 10. Carrier Hand-off After Delivery Check
-- Identifies chronological errors where the customer delivery timestamp precedes the carrier pickup timestamp.
SELECT order_id, order_delivered_carrier_date, order_delivered_customer_date
FROM silver.orders
WHERE order_delivered_carrier_date > order_delivered_customer_date;

-- 11. Missing Estimated Delivery Date Check
-- Identifies records where the business-critical SLA metric order_estimated_delivery_date is empty.
SELECT order_id, order_estimated_delivery_date
FROM silver.orders
WHERE order_estimated_delivery_date IS NULL;

-- 12. Estimated Date Prior to Purchase Check
-- Identifies logical issues where the estimated delivery promise date is set before the actual purchase event.
SELECT order_id, order_purchase_timestamp, order_estimated_delivery_date
FROM silver.orders
WHERE order_estimated_delivery_date <= order_purchase_timestamp;

-- 13. Invalid Ingestion Timestamp Flag Check
-- Identifies records that failed upstream system-level timestamp parsing processes.
SELECT order_id, is_valid_timestamp
FROM silver.orders
WHERE is_valid_timestamp = FALSE;

-- 14. System Audit Date Mismatch Check
-- Identifies illogical system audit metadata where the system update date predates the initial creation date.
SELECT order_id, create_date, update_date
FROM silver.orders
WHERE update_date < create_date;