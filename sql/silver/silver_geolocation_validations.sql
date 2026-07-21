WITH validation_checks AS (
    SELECT
        -- 1. Total Rows Scanned
        COUNT(*) AS total_records,

        -- 2. Mandatory Core Fields
        COUNT(CASE WHEN geolocation_zip_code_prefix IS NULL THEN 1 END) AS null_zip_prefix_count,
        COUNT(CASE WHEN geolocation_lat IS NULL THEN 1 END) AS null_latitude_count,
        COUNT(CASE WHEN geolocation_lng IS NULL THEN 1 END) AS null_longitude_count,

        -- 3. Coordinate Bounds Business Rules
        -- Latitude must strictly fall between -90 and 90 degrees
        COUNT(CASE WHEN geolocation_lat < -90.0 OR geolocation_lat > 90.0 THEN 1 END) AS invalid_latitude_range_count,
        -- Longitude must strictly fall between -180 and 180 degrees
        COUNT(CASE WHEN geolocation_lng < -180.0 OR geolocation_lng > 180.0 THEN 1 END) AS invalid_longitude_range_count,
        -- Check for dead-center default coordinate anomalies (0.0, 0.0 is often an ingestion error)
        COUNT(CASE WHEN geolocation_lat = 0.0 AND geolocation_lng = 0.0 THEN 1 END) AS suspect_zero_island_coordinates_count,

        -- 4. Geographic String Rules
        COUNT(CASE WHEN geolocation_zip_code_prefix <= 0 THEN 1 END) AS negative_or_zero_zip_count,
        COUNT(CASE WHEN geolocation_city IS NULL OR TRIM(geolocation_city) = '' THEN 1 END) AS missing_city_count,
        COUNT(CASE WHEN geolocation_state IS NULL OR LENGTH(TRIM(geolocation_state)) <> 2 THEN 1 END) AS invalid_state_code_count,

        -- 5. System Date Log Rules
        COUNT(CASE WHEN update_date < create_date THEN 1 END) AS system_date_mismatch_count
    FROM silver.geolocation
),
duplicate_checks AS (
    -- 6. Uniqueness Check
    -- In a geolocation master table, a zip code prefix mapping to a specific lat/long coordinate set should be unique.
    SELECT COUNT(*) AS duplicate_coordinate_mappings_count
    FROM
    (
        SELECT
            geolocation_zip_code_prefix,
            geolocation_lat,
            geolocation_lng,
            geolocation_city,
            geolocation_state
        FROM silver.geolocation
        GROUP BY
            geolocation_zip_code_prefix,
            geolocation_lat,
            geolocation_lng,
            geolocation_city,
            geolocation_state
        HAVING COUNT(*) > 1
    ) t;
)
SELECT 
    v.total_records,
    v.null_zip_prefix_count,
    v.negative_or_zero_zip_count,
    v.null_latitude_count,
    v.null_longitude_count,
    v.invalid_latitude_range_count,
    v.invalid_longitude_range_count,
    v.suspect_zero_island_coordinates_count,
    v.missing_city_count,
    v.invalid_state_code_count,
    d.duplicate_coordinate_mappings_count,
    v.system_date_mismatch_count,
    -- Summary Evaluation Status
    CASE 
        WHEN (
            v.null_zip_prefix_count + 
            v.negative_or_zero_zip_count +
            v.null_latitude_count + 
            v.null_longitude_count + 
            v.invalid_latitude_range_count + 
            v.invalid_longitude_range_count + 
            v.missing_city_count + 
            v.invalid_state_code_count + 
            d.duplicate_coordinate_mappings_count + 
            v.system_date_mismatch_count
        ) = 0 THEN 'PASSED'
        ELSE 'FAILED'
    END AS business_rule_status
FROM validation_checks v, duplicate_checks d;