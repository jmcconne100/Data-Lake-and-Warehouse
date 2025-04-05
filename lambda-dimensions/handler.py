import boto3
import pandas as pd
import os

s3 = boto3.client('s3')
bucket = os.environ.get("BUCKET_NAME", "jon-s3-bucket-for-redshift")

segments = ['Consumer', 'Corporate', 'Home Office', 'Small Business']
channels = ['Email', 'Ads', 'Organic', 'Referral', 'Social Media']
categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty']
locations = {
    'US': ['East', 'West', 'South', 'Midwest'],
    'UK': ['England', 'Scotland', 'Wales', 'NI'],
    'CA': ['Ontario', 'Quebec', 'BC', 'Alberta'],
    'DE': ['Bavaria', 'Berlin', 'Hesse'],
    'IN': ['Maharashtra', 'Delhi', 'Karnataka'],
    'AU': ['NSW', 'VIC', 'QLD']
}

def upload_csv(df, key):
    filename = f'/tmp/{key.split(\"/\")[-1]}'
    df.to_csv(filename, index=False)
    s3.upload_file(filename, bucket, key)

def handler(event, context):
    upload_csv(pd.DataFrame({'segment_id': range(1, len(segments)+1), 'segment': segments}), 'raw/dimensions/dim_segments.csv')
    upload_csv(pd.DataFrame({'channel_id': range(1, len(channels)+1), 'channel': channels}), 'raw/dimensions/dim_channels.csv')
    upload_csv(pd.DataFrame({'category_id': range(1, len(categories)+1), 'category': categories}), 'raw/dimensions/dim_categories.csv')

    location_rows = []
    location_id = 1
    for country, region_list in locations.items():
        for region in region_list:
            location_rows.append({'location_id': location_id, 'country': country, 'region': region})
            location_id += 1

    upload_csv(pd.DataFrame(location_rows), 'raw/dimensions/dim_locations.csv')

    return {"status": "success", "message": "All dimension files uploaded."}
