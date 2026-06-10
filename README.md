# Resume Job Matcher

A web application that accepts resume uploads, stores them securely in AWS S3, and returns relevant job recommendations powered by AWS Bedrock AI.

## Features

- **Resume Upload**: Support for PDF and DOCX file formats
- **Secure Storage**: Resumes stored in AWS S3 with unique keys
- **AI-Powered Analysis**: Uses AWS Bedrock (Claude 3 or Llama 3) to analyze resumes
- **Job Recommendations**: Get personalized job role suggestions based on skills and experience
- **Clean UI**: Simple, responsive web interface
- **Error Handling**: Comprehensive error handling for file types and API failures

## Architecture

```
User → Flask App → AWS S3 (Storage)
                → Text Extraction (PyPDF2/python-docx)
                → AWS Bedrock (AI Analysis)
                → Job Recommendations
```

## Prerequisites

- Python 3.8 or higher
- AWS Account with:
  - S3 access
  - Bedrock access (with Claude 3 or Llama 3 model enabled)
  - Appropriate IAM permissions
- AWS CLI configured with credentials

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd resume-job-matcher
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AWS credentials

Make sure your AWS credentials are configured. You can set them up using:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=us-east-1
```

### 5. Set up environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```
SECRET_KEY=your-random-secret-key
S3_BUCKET_NAME=your-unique-bucket-name
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### 6. Create S3 Bucket

Run the setup script to create and configure the S3 bucket:

```bash
python setup_s3.py
```

Or manually create an S3 bucket with:
- Versioning enabled
- Public access blocked
- Server-side encryption enabled (recommended)

## Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## Usage

1. Open the web application in your browser
2. Click "Choose Resume File" and select your PDF or DOCX resume
3. Click "Get Job Recommendations"
4. View your personalized job role recommendations

## IAM Permissions Required

Your AWS user/role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

## Project Structure

```
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── setup_s3.py           # S3 bucket setup script
├── templates/
│   ├── index.html        # Upload form page
│   └── results.html      # Results display page
├── static/
│   ├── css/
│   │   └── style.css     # Application styling
│   └── js/
│       └── script.js     # Client-side JavaScript
└── README.md             # This file
```

## Technical Details

### Supported File Types
- PDF (.pdf)
- Microsoft Word (.docx)

### File Size Limit
- Maximum: 10MB

### AWS Services Used
- **S3**: Secure resume storage with unique UUID-based keys
- **Bedrock**: AI-powered resume analysis and job matching

### AI Models Supported
- Claude 3 Sonnet (default): `anthropic.claude-3-sonnet-20240229-v1:0`
- Llama 3 70B: `meta.llama3-70b-instruct-v1:0`
- Other Bedrock models can be configured via environment variable

## Error Handling

The application includes error handling for:
- Invalid file types (only PDF/DOCX allowed)
- File size exceeding limit
- S3 upload failures
- Bedrock API errors
- Text extraction errors

## Security Considerations

- Resumes are stored in S3 with blocked public access
- Unique UUID-based keys prevent file name collisions
- File type validation prevents malicious uploads
- File size limits prevent DoS attacks
- AWS credentials should never be hardcoded (use environment variables or IAM roles)

## Out of Scope

- User authentication and authorization
- Database storage for job listings
- Real-time job board integration
- Resume history tracking
- Multi-user support

## Troubleshooting

### Bedrock Model Not Available
Ensure the model is enabled in your AWS region. Go to AWS Bedrock console → Model access → Enable the required model.

### S3 Access Denied
Verify your IAM permissions include s3:PutObject and s3:GetObject for the bucket.

### Text Extraction Fails
Ensure the uploaded file is a valid PDF or DOCX file and not corrupted.

## License

This project is provided as-is for demonstration purposes.
