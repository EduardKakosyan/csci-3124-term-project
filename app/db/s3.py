import boto3
import os
from dotenv import load_dotenv
from fastapi import UploadFile
import uuid
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_REGION"),
)

# Bucket name
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "dalhousie-course-files")


def create_bucket():
    """Create S3 bucket if it doesn't exist."""
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} already exists")
    except:
        try:
            region = os.getenv("AWS_REGION", "us-east-1")

            # For us-east-1, we don't specify LocationConstraint
            if region == "us-east-1":
                s3.create_bucket(Bucket=BUCKET_NAME)
            else:
                s3.create_bucket(
                    Bucket=BUCKET_NAME,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            print(f"Created bucket {BUCKET_NAME}")

        except Exception as e:
            print(f"Error creating bucket: {str(e)}")
            raise e


def generate_presigned_url(object_key: str, expiration: int = 3600) -> str:
    """
    Generate a presigned URL for an S3 object.
    expiration: URL expiration time in seconds (default 1 hour)
    """
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": object_key},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {str(e)}")
        raise e


async def upload_file(file: UploadFile, course_code: str) -> tuple[str, str, str]:
    """
    Upload a file to S3.
    Returns tuple of (object_key, presigned_url, filename)
    """
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{course_code}/{str(uuid.uuid4())}{file_extension}"

        # Upload file
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type},
        )

        # Generate presigned URL
        presigned_url = generate_presigned_url(unique_filename)

        return unique_filename, presigned_url, file.filename
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise e


async def delete_file(object_key: str):
    """Delete a file from S3."""
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=object_key)
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        raise e


def refresh_presigned_url(object_key: str) -> str:
    """Refresh a presigned URL for an existing object."""
    return generate_presigned_url(object_key)
