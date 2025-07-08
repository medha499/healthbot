import boto3
import json
from typing import Dict, Any

def flatten_conditions_with_patient(data: Dict[str, Any]) -> list:
    """
    Extracts conditions and injects patient_id into each record. Converts field names to lowercase.
    """
    conditions = data.get("conditions", [])
    patient_id = data.get("patient", {}).get("id", None)
    
    flattened = []
    for cond in conditions:
        flat = {k.lower(): v for k, v in cond.items()}
        flat["patient_id"] = patient_id
        flattened.append(json.dumps(flat, separators=(",", ":")))
    return flattened

def process_and_store_conditions(bucket: str, source_prefix: str, dest_prefix: str):
    s3 = boto3.client('s3')
    
    response = s3.list_objects_v2(Bucket=bucket, Prefix=source_prefix)
    if 'Contents' not in response:
        print("No files found.")
        return

    for obj in response['Contents']:
        key = obj['Key']
        if not key.endswith('.json'):
            continue

        print(f"Processing: {key}")
        content = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
        lines = content.strip().split("\n")

        all_conditions = []
        for line in lines:
            try:
                data = json.loads(line)
                conditions = flatten_conditions_with_patient(data)
                all_conditions.extend(conditions)
            except Exception as e:
                print(f"Error parsing {key}: {e}")

        # Determine new key
        filename = key.split("/")[-1]
        new_key = f"{dest_prefix}{filename}"

        s3.put_object(
            Bucket=bucket,
            Key=new_key,
            Body="\n".join(all_conditions).encode("utf-8"),
            ContentType='application/json'
        )
        print(f"Uploaded to: {new_key}")

def main():
    BUCKET_NAME = "structuredhealthbotdata"
    SOURCE_PREFIX = "flattened/"
    DEST_PREFIX = "flattened_conditions/"

    process_and_store_conditions(BUCKET_NAME, SOURCE_PREFIX, DEST_PREFIX)

if __name__ == "__main__":
    main()



"""
import boto3
import json

def flatten_conditions(bucket: str, input_prefix: str, output_prefix: str):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket, Prefix=input_prefix)

    for obj in response.get('Contents', []):
        key = obj['Key']
        if not key.endswith('.json'):
            continue

        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        lines = content.strip().split('\n')
        new_lines = []

        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                conditions = data.get("conditions", [])
                for condition in conditions:
                    new_lines.append(json.dumps({k.lower(): v for k, v in condition.items()}))
            except Exception as e:
                print(f"Error parsing line in {key}: {e}")

        new_key = key.replace(input_prefix, output_prefix, 1)
        s3.put_object(
            Bucket=bucket,
            Key=new_key,
            Body='\n'.join(new_lines).encode('utf-8'),
            ContentType='application/json'
        )
        print(f"✓ Flattened and uploaded: {new_key}")

# Example usage:
flatten_conditions(
    bucket="structuredhealthbotdata",
    input_prefix="flattened_lowercase/",
    output_prefix="flattened_flat_conditions/"
)

"""