# Document Reader API

A simple RESTful API for PDF processing with OCR and AI extraction using document-reader-ocr and Claude AI.

## Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Setup
```bash
# 1. Clone and enter directory
git clone <your-repo-url>
cd document-reader-api

# 2. Set environment variables
export API_KEY="your-secret-api-key"
export ANTHROPIC_API_KEY="sk-ant-api03-your-anthropic-key"

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Test It Works
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"document-reader-api"}
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Extract Text from PDF
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf"

# Returns: {"success": true, "text": "extracted text...", "text_length": 1234}
```

### Extract Structured Data with AI
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf" \
  -F "prompt=Extract names, dates, and amounts from this document"

# Returns: {"success": true, "extracted_data": "Name: John Doe\nDate: 2024-01-15..."}
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## Local Development

### Environment Setup
Copy `.env.example` to `.env` and fill in your values:
```bash
API_KEY=your-secret-api-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here
MAX_FILE_SIZE=52428800  # 50MB (optional)
PORT=8000               # optional
```

### Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with a sample PDF
curl -X POST "http://localhost:8000/ocr" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@sample.pdf"
```

## Deployment

### Docker (Recommended)
```bash
# Build and run
docker build -t document-reader-api .
docker run -d -p 8000:8000 \
  -e API_KEY="your-api-key" \
  -e ANTHROPIC_API_KEY="your-anthropic-key" \
  --name doc-reader document-reader-api

# Test deployment
curl http://localhost:8000/health
```

### RunPod
1. Create new pod with Docker template
2. Upload your code or `git clone`
3. Set environment variables in RunPod dashboard
4. Run:
```bash
docker build -t document-reader-api . && docker run -d -p 8000:8000 \
  -e API_KEY="$API_KEY" -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --name doc-reader document-reader-api
```

### DigitalOcean
1. Create Ubuntu droplet with Docker
2. SSH in and clone your repo
3. Set environment variables and run:
```bash
export API_KEY="your-api-key" && export ANTHROPIC_API_KEY="your-anthropic-key"
docker build -t document-reader-api . && docker run -d -p 8000:8000 \
  -e API_KEY="$API_KEY" -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --name doc-reader document-reader-api
```

### AWS EC2
1. Launch Ubuntu instance with Docker
2. Open port 8000 in security groups
3. SSH in and deploy same as DigitalOcean above

## Troubleshooting

### API Not Starting
```bash
# Check if container is running
docker ps

# Check logs for errors
docker logs doc-reader

# Check if port is in use
netstat -tlnp | grep 8000
```

### Authentication Errors
- Verify `API_KEY` environment variable is set
- Check that Bearer token in request matches your API key
- Make sure Anthropic API key is valid

### File Upload Issues
- Only PDF files are supported
- Check file size (default limit: 50MB)
- Verify file isn't corrupted: `file document.pdf`

### OCR Processing Errors
- Check container has sufficient memory (2GB+ recommended)
- View detailed logs: `docker logs doc-reader | grep -i error`

## Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | Authentication token for API access | - | Yes |
| `ANTHROPIC_API_KEY` | Claude AI API key | - | Yes |
| `MAX_FILE_SIZE` | Max file size in bytes | 52428800 (50MB) | No |
| `PORT` | Server port | 8000 | No |

## File Limits
- **Format**: PDF only
- **Size**: 50MB max (configurable)
- **Processing**: ~30-60 seconds per document

---

**Need help?** Check the interactive docs at `/docs` or view logs with `docker logs doc-reader`