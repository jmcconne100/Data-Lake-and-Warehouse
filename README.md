## AWS Lakehouse Data Pipeline with Redshift + Glue + S3

This project implements a cloud-native data lakehouse architecture using Amazon Redshift, Glue, S3, and Lambda. It follows a hybrid approach where most of the infrastructure is provisioned with CloudFormation, and Amazon Redshift is manually configured for better visibility and control. There are additional README's in the respective folders

---

### Architecture Components

- S3 buckets (raw/, processed/)
- Glue Crawler + Glue Job
- Lambda functions for generating synthetic data
- Step Function orchestration
- EventBridge rule to run weekly
- IAM users and roles (redshift-admin)

## Architecture Overview

S3 (raw + processed data) │ ▼ Glue Job (CSV ➝ Parquet) │ ▼ Glue Crawler → Glue Catalog │ ▼ Query + COPY ➝ Amazon Redshift

```
                          ┌────────────────────┐
                          │    EventBridge      │
                          │  (Scheduled Trigger)│
                          └────────┬───────────┘
                                   │
                            (triggers weekly)
                                   ▼
                        ┌──────────────────────┐
                        │      Step Function    │
                        │(orchestrates ETL flow)│
                        └────────┬─────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
        ┌──────────────────┐           ┌────────────────────┐
        │    Lambda:       │           │    Lambda:         │
        │ gen_dimensions.py│           │ gen_fact_data.py   │
        └────────┬─────────┘           └────────┬───────────┘
                 │                              │
                 ▼                              ▼
         ┌──────────────┐              ┌────────────────┐
         │ S3 Bucket:   │              │  S3 Bucket:     │
         │ /raw/        │              │ /raw/           │
         └────┬─────────┘              └──────┬──────────┘
              ▼                                 ▼
         ┌────────────────────────────────────────────┐
         │       Glue Job: CSV ➝ Parquet Conversion    │
         │     (writes to s3://.../processed/)         │
         └──────────────┬──────────────────────────────┘
                        ▼
             ┌─────────────────────┐
             │   Glue Crawler      │
             │ (builds Glue Catalog)│
             └────────────┬────────┘
                          ▼
               ┌──────────────────────┐
               │     Glue Catalog     │
               │(schema definitions)  │
               └────────┬─────────────┘
                        ▼
           ┌────────────────────────────┐
           │    Amazon Redshift         │
           │ (Provisioned Cluster)      │
           └────────┬───────────────────┘
                    ▼
       ┌──────────────────────────────┐
       │ COPY FROM s3://.../processed/│
       │    FORMAT AS PARQUET         │
       └──────────────────────────────┘
```
