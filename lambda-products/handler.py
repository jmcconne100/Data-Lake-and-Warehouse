import boto3
import pandas as pd
from faker import Faker
import random
import os

s3 = boto3.client('s3')
bucket = os.environ.get("BUCKET_NAME", "jon-s3-bucket-for-redshift")
faker = Faker()
random.seed(42)

categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty']
category_lookup = {name: idx+1 for idx, name in enumerate(categories)}

def handler(event, context):
    products = []
    for i in range(1, 1001):
        name = faker.word().capitalize() + " " + faker.word().capitalize()
        category = random.choice(categories)
        price = round(random.uniform(5.0, 2000.0), 2)
        products.append([i, name, category_lookup[category], price])
    df = pd.DataFrame(products, columns=['product_id', 'product_name', 'category_id', 'price'])
    path = '/tmp/products.csv'
    df.to_csv(path, index=False)
    s3.upload_file(path, bucket, 'raw/products/products.csv')
    return {"status": "success", "message": "products.csv uploaded."}
