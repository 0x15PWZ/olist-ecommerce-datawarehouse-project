WITH validation_checks AS (
    SELECT
        -- 1. Total Rows Scanned
        COUNT(*) AS total_records,

        -- 2. Mandatory Core Fields
        COUNT(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 END) AS missing_order_id_count,
        COUNT(CASE WHEN payment_sequential IS NULL THEN 1 END) AS null_payment_sequential_count,
        COUNT(CASE WHEN payment_type IS NULL OR TRIM(payment_type) = '' THEN 1 END) AS missing_payment_type_count,

        -- 3. Payment Method Integrity Rules
        COUNT(CASE WHEN payment_type = 'NOT_DEFINED' THEN 1 END) AS undefined_payment_type_count,

        -- 4. Installment Rules by Payment Type
        COUNT(CASE WHEN payment_type = 'CREDIT_CARD' AND (payment_installments IS NULL OR payment_installments < 1) THEN 1 END) AS credit_card_invalid_installments_count,
        COUNT(CASE WHEN payment_type IN ('BOLETO', 'DEBIT_CARD') AND payment_installments <> 1 THEN 1 END) AS single_payment_method_multi_installment_count,
        COUNT(CASE WHEN payment_installments IS NULL OR payment_installments < 0 THEN 1 END) AS negative_or_null_installments_count,

        -- 5. Financial & Value Rules by Payment Type
        COUNT(CASE WHEN payment_type IN ('BOLETO', 'DEBIT_CARD', 'CREDIT_CARD') AND (payment_value IS NULL OR payment_value <= 0) THEN 1 END) AS paid_methods_zero_or_negative_value_count,
        COUNT(CASE WHEN payment_type = 'VOUCHER' AND (payment_value IS NULL OR payment_value < 0) THEN 1 END) AS voucher_negative_value_count,

        -- 6. Structural & Sequence Rules
        COUNT(CASE WHEN payment_sequential <= 0 THEN 1 END) AS invalid_payment_sequential_range_count,
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count
    FROM silver.order_payments
),
duplicate_checks AS (
    -- 7. Composite Primary Key Uniqueness Check (order_id + payment_sequential)
    SELECT COUNT(*) AS duplicate_pk_combination_count
    FROM (
        SELECT order_id, payment_sequential
        FROM silver.order_payments
        WHERE order_id IS NOT NULL AND payment_sequential IS NOT NULL
        GROUP BY order_id, payment_sequential
        HAVING COUNT(*) > 1
    ) sub
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
    -- Summary Evaluation Status (Fails if any rule counter is greater than 0)
    CASE 
        WHEN (
            v.missing_order_id_count + 
            v.null_payment_sequential_count + 
            d.duplicate_pk_combination_count + 
            v.missing_payment_type_count + 
            v.undefined_payment_type_count +
            v.invalid_payment_sequential_range_count + 
            v.negative_or_null_installments_count +
            v.credit_card_invalid_installments_count + 
            v.single_payment_method_multi_installment_count + 
            v.paid_methods_zero_or_negative_value_count + 
            v.voucher_negative_value_count +
            v.system_date_mismatch_count
        ) = 0 THEN 'PASSED'
        ELSE 'FAILED'
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d;

--================================================================================
-- Checks for payments missing the core Order ID
SELECT * FROM silver.order_payments 
WHERE order_id IS NULL OR TRIM(order_id) = '';

-- Checks for payments missing the sequence number (payment_sequential)
SELECT * FROM silver.order_payments 
WHERE payment_sequential IS NULL;

-- Checks for payments missing the payment method/type
SELECT * FROM silver.order_payments 
WHERE payment_type IS NULL OR TRIM(payment_type) = '';

-- Checks if the payment sequence is physically impossible (must be 1 or greater)
SELECT * FROM silver.order_payments 
WHERE payment_sequential <= 0;

-- Checks for invalid installment counts (cannot be negative or missing)
SELECT * FROM silver.order_payments 
WHERE payment_installments IS NULL OR payment_installments < 0;

-- Checks if credit card transactions are marked with 0 installments (credit cards require at least 1 installment)
SELECT * FROM silver.order_payments 
WHERE LOWER(payment_type) = 'credit_card' 
  AND payment_installments < 1;

 -- Checks for illegal negative payment amounts
SELECT * FROM silver.order_payments 
WHERE payment_value IS NULL OR payment_value < 0;

-- Checks for payments of exactly $0 (usually worth inspecting, except for pure voucher transactions)
SELECT * FROM silver.order_payments 
WHERE payment_value = 0;

-- Checks if the system record update date is chronologically before the creation date
SELECT * FROM silver.order_payments 
WHERE update_date < create_date;

-- Checks for duplicates of the composite primary key (order_id + payment_sequential)
-- An order can have multiple payment records, but their sequence numbers must be unique
SELECT order_id, payment_sequential, COUNT(*) 
FROM silver.order_payments 
GROUP BY order_id, payment_sequential 
HAVING COUNT(*) > 1;

-- Checks for invalid "NOT_DEFINED" payment types that slipped through ingestion
SELECT * FROM silver.order_payments 
WHERE payment_type = 'NOT_DEFINED';

-- Checks if Boleto or Card transactions have a $0 value (Boleto/Debit/Credit cannot be free)
SELECT * FROM silver.order_payments 
WHERE payment_type IN ('BOLETO', 'DEBIT_CARD', 'CREDIT_CARD') 
  AND payment_value <= 0;

-- Checks if Vouchers have negative values (Vouchers must be greater than 0, or exactly 0 if fully exhausted)
SELECT * FROM silver.order_payments 
WHERE payment_type = 'VOUCHER' 
  AND payment_value < 0;

-- Checks if BOLETO or DEBIT_CARD transactions have installments (These methods are strictly single-payment, so installments must equal 1)
SELECT * FROM silver.order_payments 
WHERE payment_type IN ('BOLETO', 'DEBIT_CARD') 
  AND payment_installments <> 1;