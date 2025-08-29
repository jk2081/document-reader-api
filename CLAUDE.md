# Claude Code Instructions

## Document Reader API

### Project Overview

Build a simple RESTful API for PDF processing with OCR and AI extraction using the document-reader-ocr package.

### Core Requirements

- **Framework**: FastAPI
- **OCR Engine**: document-reader-ocr (from PyPI)
- **AI Service**: Claude AI (Anthropic)
- **Authentication**: Bearer token
- **File Support**: PDF only
- **Deployment**: Docker

### File Structure

```
/app.py                 # Main FastAPI app with endpoints
/document_processor.py  # OCR + LLM processing logic
/config.py             # Configuration management
/requirements.txt      # Python dependencies
/Dockerfile           # Container configuration
/README.md            # Setup guide
```

### Implementation Steps

#### 1. Create `config.py`

```python
import os
from typing import Optional

class Config:
    API_KEY: str = os.getenv("API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB
    PORT: int = int(os.getenv("PORT", "8000"))

    @classmethod
    def validate(cls) -> None:
        if not cls.API_KEY:
            raise ValueError("API_KEY environment variable is required")
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
```

#### 2. Create `document_processor.py`

```python
import os
import tempfile
import logging
from typing import Dict, Any
from document_reader import extract_text_from_pdf
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, anthropic_api_key: str):
        self.anthropic = Anthropic(api_key=anthropic_api_key)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using OCR."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            text = extract_text_from_pdf(file_path)
            logger.info(f"Successfully extracted {len(text)} characters")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise RuntimeError(f"OCR processing failed: {str(e)}")

    def extract_structured_data(self, text: str, prompt: str) -> Dict[str, Any]:
        """Extract structured data using Claude AI."""
        try:
            response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract structured data from this text based on the following prompt:\n\nPrompt: {prompt}\n\nText:\n{text}"
                    }
                ]
            )

            # Parse the response to extract structured data
            content = response.content[0].text
            # For simplicity, return as text - can be enhanced with JSON parsing
            return {"extracted_data": content}

        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            raise RuntimeError(f"AI extraction failed: {str(e)}")
```

#### 3. Create `app.py`

```python
import os
import tempfile
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, Depends, Header
from fastapi.responses import JSONResponse
from document_processor import DocumentProcessor
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Document Reader API", version="1.0.0")

# Validate configuration on startup
Config.validate()

# Initialize document processor
document_processor = DocumentProcessor(Config.ANTHROPIC_API_KEY)

def verify_api_key(authorization: str = Header(None)) -> None:
    """Verify API key from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")
    if token != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "document-reader-api"}

@app.post("/ocr")
async def ocr_endpoint(
    file: UploadFile,
    _: None = Depends(verify_api_key)
):
    """Extract text from PDF using OCR."""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # Validate file size
    if file.size and file.size > Config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {Config.MAX_FILE_SIZE} bytes"
        )

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Extract text
        text = document_processor.extract_text_from_pdf(temp_file_path)

        # Clean up temporary file
        os.unlink(temp_file_path)

        return {
            "success": True,
            "text": text,
            "text_length": len(text)
        }

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

@app.post("/extract")
async def extract_endpoint(
    file: UploadFile,
    prompt: str,
    _: None = Depends(verify_api_key)
):
    """Extract structured data from PDF using AI."""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # Validate prompt
    if not prompt or len(prompt.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be at least 10 characters"
        )

    # Validate file size
    if file.size and file.size > Config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {Config.MAX_FILE_SIZE} bytes"
        )

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Extract text first
        text = document_processor.extract_text_from_pdf(temp_file_path)

        # Extract structured data using AI
        result = document_processor.extract_structured_data(text, prompt)

        # Clean up temporary file
        os.unlink(temp_file_path)

        return {
            "success": True,
            "extracted_data": result["extracted_data"]
        }

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=Config.PORT)
```

#### 4. Create `requirements.txt`

```txt
# Core API framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# Document processing
git+https://github.com/jk2081/document-reader-ocr.git

# AI service
anthropic==0.64.0
```

#### 5. Create `Dockerfile`

```dockerfile
FROM python:3.11

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 6. Create `README.md`

````markdown
# Document Reader API

A simple RESTful API for PDF processing with OCR and AI extraction.

## Features

- Extract text from PDFs using OCR
- Extract structured data using Claude AI
- Simple authentication with API key
- Docker deployment ready

## Setup

### Environment Variables

```bash
export API_KEY=your-secret-key
export ANTHROPIC_API_KEY=your-claude-key
export MAX_FILE_SIZE=52428800  # 50MB (optional)
export PORT=8000  # optional
```
````

### Docker Deployment

```bash
# Build image
docker build -t document-reader-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e API_KEY=your-secret-key \
  -e ANTHROPIC_API_KEY=your-claude-key \
  --name doc-reader \
  document-reader-api
```

## API Endpoints

### POST /ocr

Extract text from PDF.

```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf"
```

### POST /extract

Extract structured data from PDF using AI.

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf" \
  -F "prompt=Extract policy number, dates, and premium amount"
```

### GET /health

Health check endpoint.

```bash
curl "http://localhost:8000/health"
```

```

### Key Implementation Notes

1. **Simple Authentication**: Bearer token validation
2. **File Validation**: PDF files only, size limits enforced
3. **Error Handling**: Clear, actionable error messages
4. **Temporary Files**: Secure handling with automatic cleanup
5. **Logging**: Structured logging for debugging
6. **Type Hints**: Full type annotations for reliability
7. **Configuration**: Environment-based configuration
8. **Docker Ready**: Simple containerization

### Testing the API

1. **Health Check**: `GET /health` (no auth required)
2. **OCR Test**: Upload a PDF to `/ocr` with valid API key
3. **Extraction Test**: Upload a PDF with prompt to `/extract`

### Common Issues

1. **Missing API Keys**: Ensure both `API_KEY` and `ANTHROPIC_API_KEY` are set
2. **File Size**: Check `MAX_FILE_SIZE` environment variable
3. **File Type**: Only PDF files are supported
4. **Network**: Ensure internet access for Anthropic API calls

This implementation follows the simplified PRD requirements and produces clean, maintainable code that "just works."
```
