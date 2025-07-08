import boto3
import json
from typing import Dict, Any

def flatten_conditions_with_patient(data: Dict[str, Any]) -> list:
    """
    For each condition in the patient file, add the patient_id and flatten.
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

        content = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
        all_conds = []

        for line in content.strip().split("\n"):
            try:
                data = json.loads(line)
                conds = flatten_conditions_with_patient(data)
                all_conds.extend(conds)
            except Exception as e:
                print(f"Error in {key}: {e}")

        new_key = f"{dest_prefix}{key.split('/')[-1]}"
        s3.put_object(
            Bucket=bucket,
            Key=new_key,
            Body="\n".join(all_conds).encode("utf-8"),
            ContentType="application/json"
        )
        print(f"✅ Uploaded conditions to: {new_key}")

# Run the processor
if __name__ == "__main__":
    BUCKET = "structuredhealthbotdata"
    SOURCE = "flattened/"
    DEST = "flattened_conditions/"
    process_and_store_conditions(BUCKET, SOURCE, DEST)
