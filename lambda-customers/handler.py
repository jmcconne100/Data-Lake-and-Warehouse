import boto3
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

faker = Faker()
random.seed(42)
s3 = boto3.client('s3')
bucket = os.environ.get("BUCKET_NAME", "jon-s3-bucket-for-redshift")

segments = ['Consumer', 'Corporate', 'Home Office', 'Small Business']
channels = ['Email', 'Ads', 'Organic', 'Referral', 'Social Media']
countries = ['US', 'UK', 'CA', 'DE', 'IN', 'AU']
regions = {
    'US': ['East', 'West', 'South', 'Midwest'],
    'UK': ['England', 'Scotland', 'Wales', 'NI'],
    'CA': ['Ontario', 'Quebec', 'BC', 'Alberta'],
    'DE': ['Bavaria', 'Berlin', 'Hesse'],
    'IN': ['Maharashtra', 'Delhi', 'Karnataka'],
    'AU': ['NSW', 'VIC', 'QLD']
}

def handler(event, context):
    year = datetime.now().year
    customers = []
    location_lookup = {(c, r): i+1 for i, (c, rlist) in enumerate([(c, r) for c in countries for r in regions[c]]) for r in regions[c]}
    for i in range(1, 100_001):
        name = faker.name()
        email = faker.email()
        signup_date = faker.date_between(start_date=f'{year}-01-01', end_date=f'{year}-12-31')
        last_login = signup_date + timedelta(days=random.randint(1, 365))
        is_active = random.choice([True, False])
        segment_id = segments.index(random.choice(segments)) + 1
        channel_id = channels.index(random.choice(channels)) + 1
        country = random.choice(countries)
        region = random.choice(regions[country])
        location_id = location_lookup[(country, region)]
        customers.append([
            i, name, email, signup_date, last_login, is_active, segment_id, channel_id, location_id
        ])
    df = pd.DataFrame(customers, columns=[
        'customer_id', 'name', 'email', 'signup_date', 'last_login_date',
        'is_active', 'segment_id', 'channel_id', 'location_id'
    ])
    key = f'raw/customers/signup_year={year}/customers_{year}.csv'
    path = '/tmp/customers.csv'
    df.to_csv(path, index=False)
    s3.upload_file(path, bucket, key)
    return {"status": "success", "message": f"{key} uploaded."}
