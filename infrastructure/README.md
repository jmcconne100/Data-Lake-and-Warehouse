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

### Steps to Create the Redshift Serverless Workgroup and Namespace

1. **Open the Redshift service in the AWS Console**  
   Navigate to: https://console.aws.amazon.com/redshift

2. **Click “Create workgroup”** under **Amazon Redshift Serverless**

3. **Namespace Settings**
   - If prompted, create a new namespace
   - **Namespace name:** `lakehouse-namespace`
   - **Database name:** `dev` (this is automatically set, cannot be changed)
   - Attach an IAM role that includes:
     - `AmazonS3ReadOnlyAccess`
     - (Optional) Glue catalog access if querying external tables
   - Make sure the IAM role is attached to the **namespace** (not just the workgroup)

4. **Workgroup Settings**
   - **Workgroup name:** `lakehouse-workgroup`
   - **Base capacity:** 8 RPU (default is fine for most demos)
   - **Publicly accessible:** (recommended if you want to use Query Editor v2 without complex VPC setup)
   - Configure allowed IPs or rely on default public routing for easy access

5. **Network and Security**
   - Choose the default VPC unless you need a custom one
   - No special subnet configuration needed unless going private

6. **Finalize and Create**
   - Click **Create workgroup**
   - Wait for the status to become **“Available”** for both the **workgroup** and **namespace**

7. **Post-Setup (Required!)**
   - Log out of Root and Log in as redshift-admin
     ```
       aws iam create-login-profile \
       --user-name redshift-admin \
       --password 'TempStrongP@ssw0rd2025!' \
       --no-password-reset-required
     ```
   - Manually create the Redshift DB user to match your IAM login:
     ```
     CREATE USER "IAM:redshift-admin" WITH PASSWORD DISABLE;
     ```
   - Grant permissions to the user on the `public` schema:
     ```
     GRANT USAGE ON SCHEMA public TO "IAM:redshift-admin";
     GRANT CREATE, SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "IAM:redshift-admin";
     ```

---

After this, your Redshift Serverless environment is fully ready for Query Editor v2, COPY commands, and Glue integration.

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