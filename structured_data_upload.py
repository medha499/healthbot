import boto3
import os
import json


## aws s3 sync fhir/ s3://structuredhealthbotdata/structured/ --size-only
 

def parse_fhir_bundle(file_path):
    with open(file_path) as f:
        bundle = json.load(f)

    patient = {}
    conditions = []
    medications = []
    observations = []
    careplans = []

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        r_type = resource.get("resourceType")

        if r_type == "Patient":
            patient = {
                "id": resource.get("id"),
                "gender": resource.get("gender"),
                "birthDate": resource.get("birthDate"),
                "deceasedDateTime": resource.get("deceasedDateTime", None)
            }

        elif r_type == "Condition":
            conditions.append({
                "code": resource.get("code", {}).get("coding", [{}])[0].get("code"),
                "description": resource.get("code", {}).get("coding", [{}])[0].get("display"),
                "onset": resource.get("onsetDateTime"),
                "clinicalStatus": resource.get("clinicalStatus")
            })

        elif r_type == "MedicationRequest":
            medications.append({
                "medication": resource.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("display"),
                "authoredOn": resource.get("authoredOn")
            })

        elif r_type == "Observation":
            observations.append({
                "type": resource.get("code", {}).get("text"),
                "value": resource.get("valueQuantity", {}).get("value"),
                "unit": resource.get("valueQuantity", {}).get("unit"),
                "effectiveDateTime": resource.get("effectiveDateTime")
            })

        elif r_type == "CarePlan":
            careplans.append({
                "description": resource.get("category", [{}])[0].get("coding", [{}])[0].get("display"),
                "status": resource.get("status")
            })

    return {
        "patient": patient,
        "conditions": conditions,
        "medications": medications,
        "observations": observations,
        "careplans": careplans
    }

def upload_structured_json_to_s3(json_data, bucket_name, s3_key):
    s3 = boto3.client("s3")

    extra_args = {
        "ServerSideEncryption": "AES256",
        "Metadata": {
            "project": "healthbot",
            "classification": "structured-ehr",
            "confidential": "yes"
        }
    }

    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=json.dumps(json_data),
        **extra_args
    )

    print(f"✅ Uploaded structured → s3://{bucket_name}/{s3_key}")

def parse_and_upload_folder(local_folder, bucket_name, s3_prefix="structured"):
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            if not file.endswith(".json"):
                continue

            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            structured_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")

            try:
                structured_data = parse_fhir_bundle(local_path)
                upload_structured_json_to_s3(structured_data, bucket_name, structured_key)
            except Exception as e:
                print(f"❌ Failed to process {local_path}: {e}")

if __name__ == "__main__":
    folder_path = "fhir"
    bucket_name = "structuredhealthbotdata"
    parse_and_upload_folder(folder_path, bucket_name)
