import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# AWS S3 Configuration
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'resume-job-matcher-bucket')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# AWS Bedrock Configuration
# Default to Claude 3 Sonnet, can also use: meta.llama3-70b-instruct-v1:0
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

# File upload settings
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
MAX_CONTENT_LENGTH = MAX_FILE_SIZE
