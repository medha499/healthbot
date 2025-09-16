import boto3
import psycopg2
from psycopg2 import OperationalError

try:
    print("🔐 Requesting temporary credentials...")
    client = boto3.client("redshift-serverless", region_name="us-east-1")
    response = client.get_credentials(workgroupName="healthbot-data", durationSeconds=900)

    db_user = response["dbUser"]
    db_password = response["dbPassword"]
    print(f"🔑 Using credentials for: {db_user}")

    print("🔌 Attempting to connect to Redshift...")
    conn = psycopg2.connect(
        host='',
        port=,
        database='healthbot',
        user=db_user,
        password=db_password,
        sslmode='require',
        connect_timeout=10
    )
    print('Conn', conn)
    print("✅ Connected to Redshift!")

    # Execut
    ###cursor.execute("SELECT * FROM patients LIMIT 10;") 

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients LIMIT 10;")


    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except OperationalError as e:
    print("❌ Connection to Redshift failed.")
    print(e)

except Exception as e:
    print("❌ An unexpected error occurred:")
    print(e)
