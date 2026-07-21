"""
============================================================
Validation Loader

Purpose
------------------------------------------------------------
Reusable helper functions for Silver Layer validation.

Responsibilities
------------------------------------------------------------
1. Print validation header
2. Print validation summary
3. Return validation status

============================================================
"""


def print_validation_header(table_name: str):
    """
    Print validation header.

    Parameters
    ----------
    table_name : str
        Example:
            silver.customers
            silver.orders
    """

    print("\n" + "=" * 70)
    print("SILVER LAYER VALIDATION")
    print("=" * 70)
    print(f"Table : {table_name}")
    print("=" * 70)


def print_validation_summary(
    metrics: dict,
    validation_status: str
):
    """
    Print validation summary.

    Parameters
    ----------
    metrics : dict
        Dictionary containing validation metrics.

    validation_status : str
        PASSED or FAILED.
    """

    for metric_name, value in metrics.items():

        print(f"{metric_name:<35}: {value}")

    print("-" * 70)
    print(f"{'Validation Status':<35}: {validation_status}")
    print("=" * 70)

    return validation_status