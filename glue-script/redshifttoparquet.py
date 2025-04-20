import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame

# Parse job args
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

# Init Glue/Spark context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Define input/output paths
raw_path = "s3://jon-s3-bucket-for-redshift/raw/"
processed_path = "s3://jon-s3-bucket-for-redshift/processed/"
dimensions_path = f"{raw_path}dimensions/"

# Read all CSVs recursively (excluding dimensions)
dyf = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [raw_path], "recurse": True},
    format="csv",
    format_options={"withHeader": True}
)

# Convert to DataFrame
df = dyf.toDF()

# Helper: write filtered tables to their folders
def write_filtered_table(df, filter_column, output_folder):
    filtered_df = df.filter(df[filter_column].isNotNull())
    dynamic_frame = DynamicFrame.fromDF(filtered_df, glueContext, "filtered_ctx")
    glueContext.write_dynamic_frame.from_options(
        frame=dynamic_frame,
        connection_type="s3",
        connection_options={"path": f"{processed_path}{output_folder}/"},
        format="parquet"
    )

# Write each star schema component
write_filtered_table(df, "order_id", "orders")
write_filtered_table(df, "customer_id", "customers")
write_filtered_table(df, "product_id", "products")

# Load and write standalone dimension CSVs
dim_tables = ["dim_segments", "dim_channels", "dim_categories", "dim_locations"]
for dim in dim_tables:
    dim_dyf = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={"paths": [f"{dimensions_path}{dim}.csv"]},
        format="csv",
        format_options={"withHeader": True}
    )
    glueContext.write_dynamic_frame.from_options(
        frame=dim_dyf,
        connection_type="s3",
        connection_options={"path": f"{processed_path}{dim}/"},
        format="parquet"
    )

job.commit()
