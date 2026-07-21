"""
============================================================
Silver Layer Validation

Validate silver.geolocation

Purpose
------------------------------------------------------------
Perform data quality validation for the Silver Geolocation
table and print a validation report.
============================================================
"""

from scripts.utils.databases import fetch_one

from scripts.validations.validation_loader import (
    print_validation_header,
    print_validation_summary
)


def validate_geolocation():
    """
    Validate silver.geolocation.
    """

    sql = """
    WITH validation_checks AS (

        SELECT

            COUNT(*) AS total_records,

            COUNT(
                CASE
                    WHEN geolocation_zip_code_prefix IS NULL
                    THEN 1
                END
            ) AS null_zip_prefix_count,

            COUNT(
                CASE
                    WHEN geolocation_lat IS NULL
                    THEN 1
                END
            ) AS null_latitude_count,

            COUNT(
                CASE
                    WHEN geolocation_lng IS NULL
                    THEN 1
                END
            ) AS null_longitude_count,

            COUNT(
                CASE
                    WHEN geolocation_lat < -90.0
                      OR geolocation_lat > 90.0
                    THEN 1
                END
            ) AS invalid_latitude_range_count,

            COUNT(
                CASE
                    WHEN geolocation_lng < -180.0
                      OR geolocation_lng > 180.0
                    THEN 1
                END
            ) AS invalid_longitude_range_count,

            COUNT(
                CASE
                    WHEN geolocation_lat = 0.0
                     AND geolocation_lng = 0.0
                    THEN 1
                END
            ) AS suspect_zero_island_coordinates_count,

            COUNT(
                CASE
                    WHEN geolocation_zip_code_prefix <= 0
                    THEN 1
                END
            ) AS negative_or_zero_zip_count,

            COUNT(
                CASE
                    WHEN geolocation_city IS NULL
                      OR TRIM(geolocation_city) = ''
                    THEN 1
                END
            ) AS missing_city_count,

            COUNT(
                CASE
                    WHEN geolocation_state IS NULL
                      OR LENGTH(TRIM(geolocation_state)) <> 2
                    THEN 1
                END
            ) AS invalid_state_code_count,

            COUNT(
                CASE
                    WHEN update_date < create_date
                    THEN 1
                END
            ) AS system_date_mismatch_count

        FROM silver.geolocation

    ),

    duplicate_checks AS (

        SELECT

            COUNT(*) AS duplicate_coordinate_mappings_count

        FROM (

            SELECT
                geolocation_zip_code_prefix,
                geolocation_lat,
                geolocation_lng,
                geolocation_city, -- Fixed: Added missing underscore here
                geolocation_state

            FROM silver.geolocation

            WHERE geolocation_zip_code_prefix IS NOT NULL
              AND geolocation_lat IS NOT NULL
              AND geolocation_lng IS NOT NULL
              AND geolocation_city IS NOT NULL
              AND geolocation_state IS NOT NULL


            GROUP BY
                geolocation_zip_code_prefix,
                geolocation_lat,
                geolocation_lng,
                geolocation_city,
                geolocation_state

            HAVING COUNT(*) > 1

        ) t

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

        CASE

            WHEN (

                v.null_zip_prefix_count
                + v.negative_or_zero_zip_count
                + v.null_latitude_count
                + v.null_longitude_count
                + v.invalid_latitude_range_count
                + v.invalid_longitude_range_count
                + v.missing_city_count
                + v.invalid_state_code_count
                + d.duplicate_coordinate_mappings_count
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
        null_zip_prefix,
        negative_or_zero_zip,
        null_latitude,
        null_longitude,
        invalid_latitude_range,
        invalid_longitude_range,
        zero_island_coordinates,
        missing_city,
        invalid_state_code,
        duplicate_coordinate_mappings,
        system_date_mismatch,
        validation_status
    ) = result

    print_validation_header("silver.geolocation")

    metrics = {

        "Total Records": total_records,

        "NULL zip_code_prefix": null_zip_prefix,

        "Zip <= 0": negative_or_zero_zip,

        "NULL latitude": null_latitude,

        "NULL longitude": null_longitude,

        "Invalid latitude range": invalid_latitude_range,

        "Invalid longitude range": invalid_longitude_range,

        "Zero Island coordinates": zero_island_coordinates,

        "Missing city": missing_city,

        "Invalid state code": invalid_state_code,

        "Duplicate coordinate mappings": duplicate_coordinate_mappings,

        "Update < Create": system_date_mismatch

    }

    print_validation_summary(
        metrics,
        validation_status
    )

    return validation_status