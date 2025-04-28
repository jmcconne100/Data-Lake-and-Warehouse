# Lakehouse Project with Redshift Integration (Hybrid Setup)

This project sets up a simplified modern data lakehouse architecture using AWS services, with a hybrid approach:

- **Infrastructure as Code (IaC)** using CloudFormation for Glue, Lambda, Step Functions, and S3  
- **Manual provisioning** of Amazon Redshift (Provisioned Cluster) via the AWS Console for improved control and ease of setup

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

Due to limited CloudFormation support for Redshift features like full database configuration and simplified access controls, we provision the Redshift cluster manually through the AWS Console.

---

### Steps to Create the Redshift Provisioned Cluster

1. **Open the Redshift service in the AWS Console**  
   Navigate to: [https://console.aws.amazon.com/redshift](https://console.aws.amazon.com/redshift)

2. **Click "Create Cluster"**

3. **Choose "Provisioned"**

4. **Cluster Settings**
   - **Cluster Identifier:** `my-redshift-cluster`
   - **Database Name:** `dev`
   - **Master Username:** `redshift_admin`
   - **Master Password:** (choose a secure password and store it safely)

5. **Node Settings**
   - **Node Type:** `dc2.large` (recommended for cost-efficient demo or small workloads)
   - **Number of Nodes:** 1 (single-node cluster)

6. **Network and Security**
   - **Publicly accessible:** Enable this option
   - Ensure your IP address is allowed through security groups (0.0.0.0/0 if testing, or restrict to your IP)
   - Use the default VPC unless you have a custom setup.

7. **IAM and Permissions**
   - Attach an existing IAM Role or create a new one with:
     - `AmazonS3ReadOnlyAccess` (for COPY from S3)
     - (Optional) Glue catalog access permissions if querying external tables
   - The IAM Role must be attached to the Redshift cluster under "Permissions."

8. **Finalize and Create**
   - Review settings
   - Click **Create Cluster**
   - Wait for the cluster status to become **"Available"**

---

### Optional Verification

Once the cluster is available, you can verify it using AWS CLI:

```
aws redshift describe-clusters \
  --cluster-identifier my-redshift-cluster \
  --region us-west-1
```
## Part 3: IAM User Setup for Query Editor v2 Access

To securely access the Redshift cluster without using the root account, an IAM user named `redshift-admin` is created via CloudFormation.

This user allows you to:
- Log into the AWS Management Console
- Access Amazon Redshift via Query Editor v2
- Run SQL queries without managing static database users manually

---

### Required IAM User Setup (redshift-admin)

The `redshift-admin` user should have the following:

- A **Login Profile** (a password) to access the AWS Console
- An attached **IAM Policy** granting Redshift and Query Editor v2 permissions

---

### IAM Policy Example

```
Resources:
  RedshiftAdminUser:
    Type: AWS::IAM::User
    Properties:
      UserName: redshift-admin
      LoginProfile:
        Password: TempStrongP@ssw0rd2025!
        PasswordResetRequired: false
      Policies:
        - PolicyName: RedshiftAdminFullAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - redshift:*
                  - redshift-data:*
                  - secretsmanager:*
                  - sqlworkbench:*
                  - s3:GetObject
                  - s3:ListBucket
                  - iam:GetRole
                  - iam:ListRoles
                Resource: "*"
```
You can set a login profile if needed:

## Part 4: Create Users, Tables and Load Data into Redshift

Run the following commands in the CLI:

# Grant schema usage
```
aws redshift-data execute-statement \
  --cluster-identifier redshift-cluster-1 \
  --database dev \
  --db-user awsuser \
  --sql "GRANT USAGE ON SCHEMA public TO mynewuser;"
```

# Grant select on all current tables
```
aws redshift-data execute-statement \
  --cluster-identifier redshift-cluster-1 \
  --database dev \
  --db-user awsuser \
  --sql "GRANT SELECT ON ALL TABLES IN SCHEMA public TO mynewuser;"
```

# Ensure new tables are accessible automatically
```
aws redshift-data execute-statement \
  --cluster-identifier redshift-cluster-1 \
  --database dev \
  --db-user awsuser \
  --sql "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mynewuser;"
```

After setting up your Redshift cluster and logging in via Query Editor v2, you can create tables and load your processed data stored in S3 into Redshift.

### Establish the Connection

Steps:
- Go to the AWS Console → Amazon Redshift.
- In the left menu, select Query Editor v2.
- Click Connect to database.
- Fill in:
  - Connection method: Amazon Redshift cluster
  - Cluster: redshift-cluster-1
  - Database name: dev
  - Database user: mynewuser
  - Password: SuperSecret123
- (Optional, but recommended) Check Save password if you don’t want to retype it.
- Click Connect.

---

### Data Locations

The processed Parquet data should be located in the following structure:

s3://jon-s3-bucket-for-redshift/processed/orders/ s3://jon-s3-bucket-for-redshift/processed/customers/ s3://jon-s3-bucket-for-redshift/processed/products/ s3://jon-s3-bucket-for-redshift/processed/dim_segments/ s3://jon-s3-bucket-for-redshift/processed/dim_channels/ s3://jon-s3-bucket-for-redshift/processed/dim_locations/ s3://jon-s3-bucket-for-redshift/processed/dim_categories/


---

### Create Tables in Redshift

Example SQL to create the `orders` table:

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
Load Parquet Files into Redshift Using COPY

Use the Redshift COPY command to load Parquet data from S3:

```
COPY orders
FROM 's3://jon-s3-bucket-for-redshift/processed/orders/'
IAM_ROLE 'arn:aws:iam::<your-account-id>:role/<your-redshift-access-role>'
FORMAT AS PARQUET;
```
