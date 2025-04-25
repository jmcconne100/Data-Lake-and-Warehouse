# Lakehouse Project with Redshift Integration (Hybrid Setup)

This project sets up a simplified modern data lakehouse architecture using AWS services, with a hybrid approach:

- **Infrastructure as Code (IaC)** using CloudFormation for Glue, Lambda, Step Functions, and S3  
- **Manual provisioning** of Amazon Redshift via the AWS Console for improved control and ease of setup

---

## Part 1: Launch Core Infrastructure (CloudFormation)

Deploy the `Infrastructure.txt` CloudFormation stack, which sets up:

- S3 bucket for raw and processed data  
- Lambda functions for generating dimension and fact data  
- Step Function to orchestrate fact table generation  
- EventBridge rule to schedule weekly jobs  
- Glue Job to convert CSV to Parquet  
- Glue Crawler to catalog processed data  
- IAM users and roles (including `redshift-admin`)

### Deploy the Stack

Using the AWS Console or CLI:

```
aws cloudformation deploy \
  --template-file Infrastructure.txt \
  --stack-name LakehouseInfra \
  --capabilities CAPABILITY_NAMED_IAM
```

## Part 2: Create Redshift Cluster Manually (via AWS Console)

Due to limited CloudFormation support for Redshift features like multi-database setup and IAM identity integration, we provision the Redshift cluster manually in the browser.

### Steps to Create the Redshift Cluster

1. **Open the Redshift service in the AWS Console**  
   Navigate to: https://console.aws.amazon.com/redshift

2. **Click “Create Cluster”**

3. **Choose “Provisioned”** (not Serverless)

4. **Cluster Settings**  
   Fill in the following:
   - **Cluster identifier:** `my-redshift-cluster`
   - **Database name:** `dev` (or `mydatabase`, just be consistent)
   - **Master username:** `redshift_admin`
   - **Master password:** (Choose something secure; save it)

5. **Node settings**
   - **Node type:** `dc2.large` (or `ra3.xlplus` if needed)
   - **Number of nodes:** 1 (single-node for testing)

6. **Network and Security**
   - Leave default VPC and Subnet Group
   - Make sure **public access is enabled** (if you want CLI/BI tool access)
   - Allow access from your IP or use a security group that enables inbound port **5439**

7. **IAM and Permissions**
   - Attach an existing IAM role (or create one) with the following policies:
     - `AmazonS3ReadOnlyAccess` (to allow `COPY` from S3)
     - Any custom policies your Redshift cluster might need

8. **Finalize and Create**
   - Click **Create Cluster**
   - Wait for the status to become **“Available”**

---

### Optional Verification Steps

Once the cluster is available, test the following:

```
aws redshift describe-clusters \
  --cluster-identifier my-redshift-cluster \
  --region us-west-1
```

## Part 3: IAM User for Query Editor v2

To access Redshift securely and avoid using the root user, use the IAM user `redshift-admin` created in your CloudFormation stack.

This IAM user should be granted the following permissions:

### Required IAM Permissions

```
  RedshiftAdminUser:
    Type: AWS::IAM::User
    Properties:
      UserName: redshift-admin
      Policies:
        - PolicyName: QueryEditorV2Support
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - redshift:DescribeClusters
                  - redshift:GetClusterCredentials
                  - redshift:ListSchemas
                  - redshift:ListTables
                  - redshift:TagResource
                  - redshift-data:ExecuteStatement
                  - redshift-data:GetStatementResult
                  - redshift-data:ListDatabases
                  - redshift-data:ListSchemas
                  - redshift-data:ListTables
                  - sqlworkbench:CreateConnection
                  - sqlworkbench:DeleteConnection
                  - sqlworkbench:GetAccountInfo
                  - sqlworkbench:GetUserInfo
                  - sqlworkbench:GetAccountSettings
                  - sqlworkbench:GetUserWorkspaceSettings
                  - sqlworkbench:ListConnections
                  - sqlworkbench:TagResource
                  - sqlworkbench:UntagResource
                  - sqlworkbench:UpdateConnection
                Resource: "*"
```

## Part 4: Create Tables & Load Data into Redshift

After setting up your Redshift cluster and logging in via Query Editor v2, you can begin creating tables and loading Parquet data from S3 (processed by your Glue jobs).

---

### Data Locations

Your Parquet data should be located in a structure like:


---

### Create Tables (Example)

```
CREATE TABLE orders (
  order_id INT,
  customer_id INT,
  product_id INT,
  order_date DATE,
  quantity INT,
  unit_price FLOAT8,
  total_price FLOAT8,
  status VARCHAR(50)
);
```

### Load Parquet with COPY

Use the Redshift COPY command to load Parquet data from S3:

```
FROM 's3://jon-s3-bucket-for-redshift/processed/orders/'
IAM_ROLE 'arn:aws:iam::<your-account-id>:role/<your-redshift-access-role>'
FORMAT AS PARQUET;
```

Repeat this for each table (e.g., customers, products, dim_segments, etc.).