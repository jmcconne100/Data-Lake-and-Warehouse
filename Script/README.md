# README.md for Normalized Data Generator

This project simulates a realistic, normalized e-commerce dataset and populates an **Amazon S3-based data lake** for downstream analytics using **Amazon Redshift Serverless**.

It uses Python + Faker to generate synthetic data across multiple years and uploads partitioned files in a **normalized (star schema)** format to S3.

---

# Project Structure
```
.
├── normalized_part1_dimensions_and_products.py
├── normalized_part2_customers_and_orders.py
└── S3 Output:
    └── raw/
        ├── dimensions/
        │   ├── dim_segments.csv
        │   ├── dim_channels.csv
        │   ├── dim_categories.csv
        │   └── dim_locations.csv
        ├── products/
        │   └── products.csv
        ├── customers/
        │   ├── signup_year=2015/
        │   │   └── customers_2015.csv
        │   ├── signup_year=2016/
        │   │   └── customers_2016.csv
        │   └── ... (through signup_year=2024)
        └── orders/
            ├── order_year=2015/
            │   └── orders_2015.csv
            ├── order_year=2016/
            │   └── orders_2016.csv
            └── ... (through order_year=2024)
```

# Data Model Overview

This project uses a **star schema** with the following structure:

- `customers` — Fact table with FK references to:
  - `dim_segments`
  - `dim_channels`
  - `dim_locations`

- `orders` — Fact table with FK references to:
  - `products` (which references `dim_categories`)

- `products` — Dimension-like table with FK to `dim_categories`

Each record is:
- **Randomly generated**
- Partitioned by year for customers & orders
- Stored as flat `.csv` files in structured S3 folders

---

# How to Use

1. Set up an **EC2 instance** with `AmazonS3FullAccess` or a scoped bucket policy.
2. Clone this repo or copy these scripts into your instance.
3. Install dependencies:
   ```
   bash
   pip install boto3 pandas faker
   ```