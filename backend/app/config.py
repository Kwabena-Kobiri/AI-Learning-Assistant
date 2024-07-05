# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    

# class Config:
#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#     S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
#     S3_FOLDER_NAME = os.getenv("S3_FOLDER_NAME")
#     OPENSEARCH_URL = os.getenv("OPENSEARCH_URL")
#     REDIS_URL = os.getenv("REDIS_URL")
#     AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
#     AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
#     AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")