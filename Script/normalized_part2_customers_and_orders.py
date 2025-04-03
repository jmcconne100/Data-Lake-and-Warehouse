
import boto3
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

bucket = "jon-s3-bucket-for-redshift"
base_path = "raw/"
faker = Faker()
random.seed(42)
Faker.seed(42)
s3 = boto3.client("s3")

this_year = datetime.now().year
years_back = 10
customer_count_per_year = 100_000
orders_per_year = 300_000
product_count = 1000

# Dimension values
customer_segments = ['Consumer', 'Corporate', 'Home Office', 'Small Business']
signup_channels = ['Email', 'Ads', 'Organic', 'Referral', 'Social Media']
countries = ['US', 'UK', 'CA', 'DE', 'IN', 'AU']
regions = {
    'US': ['East', 'West', 'South', 'Midwest'],
    'UK': ['England', 'Scotland', 'Wales', 'NI'],
    'CA': ['Ontario', 'Quebec', 'BC', 'Alberta'],
    'DE': ['Bavaria', 'Berlin', 'Hesse'],
    'IN': ['Maharashtra', 'Delhi', 'Karnataka'],
    'AU': ['NSW', 'VIC', 'QLD']
}

# Lookup dictionaries
segment_lookup = {name: idx+1 for idx, name in enumerate(customer_segments)}
channel_lookup = {name: idx+1 for idx, name in enumerate(signup_channels)}
location_lookup = {}
location_id = 1
for country in countries:
    for region in regions[country]:
        location_lookup[(country, region)] = location_id
        location_id += 1

# Generate customers and orders
for year in range(this_year - years_back + 1, this_year + 1):
    print(f"Generating data for year {year}")

    # ----- Customers -----
    customers = []
    for i in range(1, customer_count_per_year + 1):
        name = faker.name()
        email = faker.email()
        signup_date = faker.date_between(start_date=f"{year}-01-01", end_date=f"{year}-12-31")
        last_login = signup_date + timedelta(days=random.randint(1, 365))
        is_active = random.choice([True, False])
        segment = random.choice(customer_segments)
        channel = random.choice(signup_channels)
        country = random.choice(countries)
        region = random.choice(regions[country])

        segment_id = segment_lookup[segment]
        channel_id = channel_lookup[channel]
        location_id_fk = location_lookup[(country, region)]

        customers.append([
            i, name, email, signup_date, last_login,
            is_active, segment_id, channel_id, location_id_fk
        ])

    df_customers = pd.DataFrame(customers, columns=[
        "customer_id", "name", "email", "signup_date", "last_login_date",
        "is_active", "segment_id", "channel_id", "location_id"
    ])

    customer_filename = f"customers_{year}.csv"
    customer_path = f"{base_path}customers/signup_year={year}/{customer_filename}"
    df_customers.to_csv(customer_filename, index=False)
    s3.upload_file(customer_filename, bucket, customer_path)
    os.remove(customer_filename)

    # ----- Orders -----
    orders = []
    for i in range(1, orders_per_year + 1):
        customer_id = random.randint(1, customer_count_per_year)
        product_id = random.randint(1, product_count)
        order_date = faker.date_between(start_date=f"{year}-01-01", end_date=f"{year}-12-31")
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(5.0, 1000.0), 2)
        total_price = round(unit_price * quantity, 2)
        status = random.choice(["Shipped", "Returned", "Processing", "Cancelled"])

        orders.append([
            i, customer_id, product_id, order_date, quantity, unit_price, total_price, status
        ])

    df_orders = pd.DataFrame(orders, columns=[
        "order_id", "customer_id", "product_id", "order_date",
        "quantity", "unit_price", "total_price", "status"
    ])

    orders_filename = f"orders_{year}.csv"
    orders_path = f"{base_path}orders/order_year={year}/{orders_filename}"
    df_orders.to_csv(orders_filename, index=False)
    s3.upload_file(orders_filename, bucket, orders_path)
    os.remove(orders_filename)
