import boto3
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Configuration
bucket = "jon-s3-bucket-for-redshift"
base_filename = "customers"
s3_prefix = "raw/customers/"
years_back = 10
records_per_year = 100_000

# Setup Faker and seed
fake = Faker()
random.seed(42)
Faker.seed(42)

# Lookup values
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

# S3 client
s3 = boto3.client("s3")

# Generate data year by year
this_year = datetime.now().year
for year in range(this_year - years_back + 1, this_year + 1):
    rows = []
    print(f"Generating data for year {year}...")

    for i in range(1, records_per_year + 1):
        name = fake.name()
        email = fake.email()
        signup_date = fake.date_between(start_date=f"{year}-01-01", end_date=f"{year}-12-31")
        last_login = signup_date + timedelta(days=random.randint(1, 365))
        total_orders = random.randint(1, 75)
        total_spent = round(random.uniform(20.0, 10000.0), 2)
        is_active = random.choice([True, False])
        segment = random.choice(customer_segments)
        channel = random.choice(signup_channels)
        country = random.choice(countries)
        region = random.choice(regions[country])

        rows.append([
            i, name, email, signup_date, last_login, total_orders, total_spent,
            is_active, segment, channel, country, region
        ])

    df = pd.DataFrame(rows, columns=[
        "customer_id", "name", "email", "signup_date", "last_login_date",
        "total_orders", "total_spent", "is_active", "customer_segment",
        "signup_channel", "country", "region"
    ])

    filename = f"{base_filename}_{year}.csv"
    s3_folder = f"{s3_prefix}signup_year={year}/"

    df.to_csv(filename, index=False)
    s3.upload_file(filename, bucket, f"{s3_folder}{filename}")
    os.remove(filename)

    print(f"Uploaded {filename} to s3://{bucket}/{s3_folder}{filename}")
