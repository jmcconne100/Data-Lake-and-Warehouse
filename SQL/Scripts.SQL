CREATE EXTERNAL SCHEMA s3_ext_schema
FROM DATA CATALOG 
DATABASE 'first_redshift_db'  -- You can make up a name here
IAM_ROLE 'arn:aws:iam::286036002000:role/service-role/AmazonRedshift-CommandsAccessRole-20250402T193348'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

CREATE EXTERNAL TABLE s3_ext_schema.customers (
    customer_id INT,
    name VARCHAR,
    signup_date DATE,
    total_orders INT,
    total_spent DECIMAL(10,2)
)
ROW FORMAT DELIMITED 
FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE 
LOCATION 's3://jon-s3-bucket-for-redshift/'
TABLE PROPERTIES ('skip.header.line.count'='1');

SELECT *
FROM s3_ext_schema.customers
LIMIT 10;

CREATE TABLE dw_customers (
    customer_id INT,
    name VARCHAR(100),
    signup_date DATE,
    total_orders INT,
    total_spent DECIMAL(10,2)
);

INSERT INTO dw_customers
SELECT * FROM s3_ext_schema.customers;

SELECT SUM(total_spent) AS total_revenue FROM dw_customers;

SELECT name, total_spent 
FROM dw_customers
ORDER BY total_spent DESC
LIMIT 5;

SELECT * FROM dw_customers
WHERE signup_date BETWEEN '2024-01-01' AND '2024-12-31';