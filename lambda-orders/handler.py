import boto3
import pandas as pd
from faker import Faker
import random
from datetime import datetime
import os

faker = Faker()
random.seed(42)
s3 = boto3.client('s3')
bucket = os.environ.get("BUCKET_NAME", "jon-s3-bucket-for-redshift")

def handler(event, context):
    year = datetime.now().year
    orders = []
    for i in range(1, 300_001):
        customer_id = random.randint(1, 100_000)
        product_id = random.randint(1, 1000)
        order_date = faker.date_between(start_date=f'{year}-01-01', end_date=f'{year}-12-31')
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(5.0, 1000.0), 2)
        total_price = round(unit_price * quantity, 2)
        status = random.choice(["Shipped", "Returned", "Processing", "Cancelled"])
        orders.append([
            i, customer_id, product_id, order_date,
            quantity, unit_price, total_price, status
        ])
    df = pd.DataFrame(orders, columns=[
        'order_id', 'customer_id', 'product_id', 'order_date',
        'quantity', 'unit_price', 'total_price', 'status'
    ])
    key = f'raw/orders/order_year={year}/orders_{year}.csv'
    path = '/tmp/orders.csv'
    df.to_csv(path, index=False)
    s3.upload_file(path, bucket, key)
    return {"status": "success", "message": f"{key} uploaded."}
