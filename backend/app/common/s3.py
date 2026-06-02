import boto3
from botocore.exceptions import ClientError
from app.config import settings

_s3 = None


def get_s3():
    global _s3
    if _s3 is None:
        _s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return _s3


async def upload_file(file_bytes: bytes, s3_key: str, content_type: str = "application/octet-stream") -> str:
    s3 = get_s3()
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=s3_key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"s3://{settings.S3_BUCKET}/{s3_key}"


def generate_presigned_url(s3_key: str, expires_in: int = 3600) -> str:
    s3 = get_s3()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": s3_key},
        ExpiresIn=expires_in,
    )
