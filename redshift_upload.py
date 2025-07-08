import boto3
import psycopg2

# Replace with your Redshift details
REGION = "us-east-1"  # your region
CLUSTER_ID = "healthbot-data"  # Redshift Serverless workgroup
HOST = "healthbot-data.692859942702.us-east-1.redshift-serverless.amazonaws.com"
PORT = 5439
DB_NAME = "healthbot"  # If "dev" is your default DB
DB_USER = "admin"  # This user must exist on the DB
IAM_ROLE_ARN = "arn:aws:redshift-serverless:us-east-1:692859942702:workgroup/0c29b3e5-d416-49bb-811a-0ce8266b4219"

# Step 1: Generate temporary auth token
session = boto3.Session()
client = session.client("redshift-serverless", region_name=REGION)

token = client.get_cluster_credentials(
    DbUser=DB_USER,
    DbName=DB_NAME,
    ClusterIdentifier=CLUSTER_ID,
    DurationSeconds=900,  # 15 mins
    AutoCreate=False  # Set to True if the user doesn't exist yet
)

# Step 2: Use token to connect to Redshift
conn = psycopg2.connect(
    host=HOST,
    port=PORT,
    database=DB_NAME,
    user=token['DbUser'],
    password=token['DbPassword'],
    sslmode='require'
)

# Test query
cur = conn.cursor()
cur.execute("SHOW DATABASES;")
print("Connected as:", cur.fetchone()[0])
