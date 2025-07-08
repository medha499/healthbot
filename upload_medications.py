import boto3
import json
from typing import Dict, Any

def flatten_careplans_with_patient(data: Dict[str, Any]) -> list:
    careplans = data.get("careplans", [])
    patient_id = data.get("patient", {}).get("id", None)

    flattened = []
    for plan in careplans:
        flat = {k.lower(): v for k, v in plan.items()}
        flat["patient_id"] = patient_id
        flattened.append(json.dumps(flat, separators=(",", ":")))
    return flattened

def process_and_store_careplans(bucket: str, source_prefix: str, dest_prefix: str):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket, Prefix=source_prefix)
    
    if 'Contents' not in response:
        print("No files found.")
        return

    for obj in response['Contents']:
        key = obj['Key']
        if not key.endswith('.json'):
            continue

        content = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
        all_plans = []

        for line in content.strip().split("\n"):
            try:
                data = json.loads(line)
                plans = flatten_careplans_with_patient(data)
                all_plans.extend(plans)
            except Exception as e:
                print(f"Error in {key}: {e}")

        new_key = f"{dest_prefix}{key.split('/')[-1]}"
        s3.put_object(
            Bucket=bucket,
            Key=new_key,
            Body="\n".join(all_plans).encode("utf-8"),
            ContentType="application/json"
        )
        print(f"✅ Uploaded careplans to: {new_key}")

# Run the processor
if __name__ == "__main__":
    BUCKET = "structuredhealthbotdata"
    SOURCE = "flattened/"
    DEST = "flattened_careplans/"
    process_and_store_careplans(BUCKET, SOURCE, DEST)
