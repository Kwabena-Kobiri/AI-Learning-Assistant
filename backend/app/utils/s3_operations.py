# app/utils/s3_operations.py
import boto3
import os
import logging
from app.config import Config

# Initialize the boto3 client with the credentials
s3_client = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_DEFAULT_REGION,
)


def check_s3_for_pdf(folder_name):
    response = s3_client.list_objects_v2(
        Bucket=Config.S3_BUCKET_NAME, Prefix=folder_name
    )
    if "Contents" in response:
        # print("s3 Data: ", response["Contents"])
        for obj in response["Contents"]:
            if obj["Key"].endswith(".pdf"):
                print(obj["Key"])
                return obj["Key"]
            else:
                print("No documents found in s3...")
    return None


def download_from_s3(s3_path, local_path):
    try:
        s3_client.download_file(Config.S3_BUCKET_NAME, s3_path, local_path)
        logging.info(
            f"Downloaded s3://{Config.S3_BUCKET_NAME}/{s3_path} to {local_path}"
        )
    except Exception as e:
        logging.error(f"Failed to download {s3_path} from S3: {str(e)}")
        raise
