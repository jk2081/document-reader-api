# Document Reader API

Simple REST API for PDF OCR and data extraction using EasyOCR and Claude AI.

## Features

- **OCR Processing**: Extract text from PDFs with confidence scoring
- **AI Extraction**: Extract structured data using custom prompts
- **Admin Interface**: Simple web UI for configuration and API key management
- **Docker Ready**: Easy deployment with Docker

## Quick Start

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
API_KEY=your-secret-api-key-here
ADMIN_PASSWORD=admin123
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:8000`

### 4. Admin Interface

Access the admin interface at `http://localhost:8000/admin`
- Login with the password from `ADMIN_PASSWORD`
- Manage API keys and configuration

## API Endpoints

### Health Check
```bash
GET /health
```

### Extract Text (OCR Only)
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf"
```

### Extract Structured Data (OCR + AI)
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf" \
  -F "prompt=Extract policy number, dates, and premium amount"
```

## Docker Deployment

### Build and Run
```bash
# Build image
docker build -t document-reader-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e ADMIN_PASSWORD=admin123 \
  -e ANTHROPIC_API_KEY=your-claude-key \
  --name doc-reader \
  document-reader-api
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `API_KEY` | Client authentication token | Required |
| `ADMIN_PASSWORD` | Admin UI password | Required |
| `ANTHROPIC_API_KEY` | Claude API key | Required |
| `MAX_FILE_SIZE` | File size limit in bytes | 52428800 (50MB) |
| `PORT` | Server port | 8000 |

## File Support

- **Supported formats**: PDF only
- **Max file size**: 50MB (configurable)
- **Processing timeout**: 90 seconds

## Dependencies

- FastAPI for REST API
- Document Reader package (local wheel)
- EasyOCR for text extraction
- Claude AI for data extraction
- Jinja2 for admin templates