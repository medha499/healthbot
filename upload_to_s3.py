import boto3
import os


## aws s3 sync fhir/ s3://healthliteracybotdata/healthbot/ --size-only
 

def upload_folder_to_s3(local_folder, bucket_name, s3_prefix="healthbot"):
    s3 = boto3.client("s3")

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)

            # S3 key: preserve folder structure
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")

            extra_args = {
                "ServerSideEncryption": "AES256",
                "Metadata": {
                    "project": "healthbot",
                    "classification": "synthetic-ehr",
                    "confidential": "yes"
                }
            }

            s3.upload_file(local_path, bucket_name, s3_key, ExtraArgs=extra_args)
            print(f"✅ Uploaded: {local_path} → s3://{bucket_name}/{s3_key}")

if __name__ == "__main__":
    folder_path = "fhir"
    bucket = "healthliteracybotdata"
    upload_folder_to_s3(folder_path, bucket)


