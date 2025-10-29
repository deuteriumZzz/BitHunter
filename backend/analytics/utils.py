import boto3
from django.conf import settings

s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

def save_model_to_s3(model_path, bucket_name, key):
    s3.upload_file(model_path, bucket_name, key)

def load_model_from_s3(bucket_name, key, local_path):
    s3.download_file(bucket_name, key, local_path)
