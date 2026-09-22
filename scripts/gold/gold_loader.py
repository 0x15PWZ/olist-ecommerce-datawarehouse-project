"""
============================================================
Gold Layer Loader
============================================================
"""

from scripts.gold.load_dim_customer import load_dim_customers
from scripts.gold.load_dim_product import load_dim_products
from scripts.gold.load_dim_seller import load_dim_sellers
from scripts.gold.load_dim_payment import load_dim_payment
from scripts.gold.load_dim_review import load_dim_review
from scripts.gold.load_dim_date import load_dim_date

from scripts.gold.load_fact_sales import load_fact_sales
from scripts.gold.load_fact_payments import load_fact_payments
from scripts.gold.load_fact_reviews import load_fact_reviews

from scripts.gold.load_vw_payment_summary import load_vw_payment_summary



def run_gold_layer(spark):
    """
    Execute Gold Layer ETL.
    """

    print("=" * 60)
    print("Starting Gold Layer")
    print("=" * 60)

    # Dimensions
    load_dim_customers(spark)
    load_dim_products(spark)
    load_dim_sellers(spark)
    load_dim_payment(spark)
    load_dim_review(spark)
    load_dim_date(spark)

    # Facts
    load_fact_sales(spark)
    load_fact_payments(spark)
    load_fact_reviews(spark)

    # Views
    load_vw_payment_summary(spark)

    

    print("=" * 60)
    print("Gold Layer Completed")
    print("=" * 60)