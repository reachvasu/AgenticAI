"""
Setup script to create and configure the S3 bucket for resume storage.
Run this script once before deploying the application.
"""
import boto3
import json
import sys
from botocore.exceptions import ClientError

# Configuration
BUCKET_NAME = 'resume-job-matcher-bucket'
REGION = 'us-east-1'

def create_bucket():
    """Create S3 bucket with appropriate configuration"""
    s3_client = boto3.client('s3', region_name=REGION)
    
    try:
        # Create bucket
        if REGION == 'us-east-1':
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3_client.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': REGION}
            )
        print(f"✓ Created S3 bucket: {BUCKET_NAME}")
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("✓ Enabled versioning")
        
        # Block public access
        s3_client.put_public_access_block(
            Bucket=BUCKET_NAME,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print("✓ Configured security settings (blocked public access)")
        
        print(f"\n✓ S3 bucket setup complete!")
        print(f"  Bucket name: {BUCKET_NAME}")
        print(f"  Region: {REGION}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"✓ Bucket {BUCKET_NAME} already exists and is owned by you")
        else:
            print(f"✗ Error creating bucket: {e}")
            sys.exit(1)


if __name__ == '__main__':
    create_bucket()
