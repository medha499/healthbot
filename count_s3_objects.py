import boto3

def count_s3_objects(bucket, prefix=""):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")

    total_count = 0
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        contents = page.get("Contents", [])
        total_count += len(contents)

    print(f"🔢 Total objects in s3://{bucket}/{prefix}: {total_count}")
    return total_count

# Example usage
count_s3_objects("healthliteracybotdata", "healthbot/")


## CLI COMMAND: aws s3 ls s3://healthliteracybotdata --recursive | wc -l
