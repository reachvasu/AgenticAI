import os
import uuid
import json
from io import BytesIO
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import boto3
from botocore.exceptions import ClientError
from PyPDF2 import PdfReader
from docx import Document
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'resume-job-matcher-bucket')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_stream):
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(file_stream)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_docx(file_stream):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_stream)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")


def extract_text_from_file(file_stream, filename):
    """Extract text based on file extension"""
    file_extension = filename.rsplit('.', 1)[1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(file_stream)
    elif file_extension == 'docx':
        return extract_text_from_docx(file_stream)
    else:
        raise Exception(f"Unsupported file type: {file_extension}")


def upload_to_s3(file_stream, filename):
    """Upload file to S3 and return the key"""
    try:
        # Generate unique key
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_key = f"resumes/{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file_stream,
            S3_BUCKET,
            unique_key,
            ExtraArgs={'ContentType': 'application/pdf' if file_extension == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
        )
        
        return unique_key
    except ClientError as e:
        raise Exception(f"Error uploading to S3: {str(e)}")


def get_job_recommendations(resume_text):
    """Get job recommendations from AWS Bedrock"""
    try:
        # Create prompt for Bedrock
        prompt = f"""You are a career advisor AI. Analyze the following resume and suggest 5-7 relevant job roles that would be a good match based on the candidate's skills, experience, and background.

For each job role, provide:
1. Job Title
2. Why it's a good match (2-3 sentences)
3. Key skills from the resume that align with this role

Resume:
{resume_text}

Please provide your response in a structured format."""

        # Prepare request for Claude 3
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
        
        # Invoke Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        recommendations = response_body['content'][0]['text']
        
        return recommendations
    except ClientError as e:
        raise Exception(f"Error calling Bedrock: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error with Bedrock: {str(e)}")


@app.route('/')
def index():
    """Render the upload form"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_resume():
    """Handle resume upload and return job recommendations"""
    try:
        # Check if file is present
        if 'resume' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Validate file type
        if not allowed_file(file.filename):
            flash('Only PDF and DOCX files are supported', 'error')
            return redirect(url_for('index'))
        
        # Read file
        filename = secure_filename(file.filename)
        file_content = file.read()
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            flash('File size exceeds 10MB limit', 'error')
            return redirect(url_for('index'))
        
        # Upload to S3
        file_stream = BytesIO(file_content)
        s3_key = upload_to_s3(file_stream, filename)
        
        # Extract text
        file_stream.seek(0)
        resume_text = extract_text_from_file(file_stream, filename)
        
        # Get job recommendations from Bedrock
        recommendations = get_job_recommendations(resume_text)
        
        return render_template('results.html', recommendations=recommendations, filename=filename)
        
    except Exception as e:
        flash(f'Error processing resume: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
