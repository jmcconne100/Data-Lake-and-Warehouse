
import boto3
import pandas as pd
from faker import Faker
import random
import os

bucket = "jon-s3-bucket-for-redshift"
base_path = "raw/"
faker = Faker()
random.seed(42)
Faker.seed(42)
s3 = boto3.client("s3")

# Dimension values
customer_segments = ['Consumer', 'Corporate', 'Home Office', 'Small Business']
signup_channels = ['Email', 'Ads', 'Organic', 'Referral', 'Social Media']
categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty']
countries = ['US', 'UK', 'CA', 'DE', 'IN', 'AU']
regions = {
    'US': ['East', 'West', 'South', 'Midwest'],
    'UK': ['England', 'Scotland', 'Wales', 'NI'],
    'CA': ['Ontario', 'Quebec', 'BC', 'Alberta'],
    'DE': ['Bavaria', 'Berlin', 'Hesse'],
    'IN': ['Maharashtra', 'Delhi', 'Karnataka'],
    'AU': ['NSW', 'VIC', 'QLD']
}

# Create lookup dictionaries
segment_lookup = {name: idx+1 for idx, name in enumerate(customer_segments)}
channel_lookup = {name: idx+1 for idx, name in enumerate(signup_channels)}
category_lookup = {name: idx+1 for idx, name in enumerate(categories)}

location_lookup = {}
location_records = []
location_id = 1
for country in countries:
    for region in regions[country]:
        location_lookup[(country, region)] = location_id
        location_records.append([location_id, country, region])
        location_id += 1

# Save dimensions
pd.DataFrame([
    {"segment_id": v, "segment": k} for k, v in segment_lookup.items()
]).to_csv("dim_segments.csv", index=False)
pd.DataFrame([
    {"channel_id": v, "channel": k} for k, v in channel_lookup.items()
]).to_csv("dim_channels.csv", index=False)
pd.DataFrame([
    {"category_id": v, "category": k} for k, v in category_lookup.items()
]).to_csv("dim_categories.csv", index=False)
pd.DataFrame(location_records, columns=["location_id", "country", "region"]).to_csv("dim_locations.csv", index=False)

# Upload dimensions
for file in ["dim_segments.csv", "dim_channels.csv", "dim_categories.csv", "dim_locations.csv"]:
    s3.upload_file(file, bucket, f"{base_path}dimensions/{file}")
    os.remove(file)

# Generate products
product_count = 1000
products = []
for i in range(1, product_count + 1):
    name = faker.word().capitalize() + " " + faker.word().capitalize()
    category = random.choice(categories)
    category_id = category_lookup[category]
    price = round(random.uniform(5.0, 2000.0), 2)
    products.append([i, name, category_id, price])

df_products = pd.DataFrame(products, columns=['product_id', 'product_name', 'category_id', 'price'])
df_products.to_csv("products.csv", index=False)
s3.upload_file("products.csv", bucket, f"{base_path}products/products.csv")
os.remove("products.csv")
