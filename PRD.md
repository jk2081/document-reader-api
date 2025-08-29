# Product Requirements Document (PRD)

## Document Reader API

### **1. Executive Summary**

**Product Name**: Document Reader API  
**Version**: 1.0.0  
**Target Users**: Developers needing simple PDF OCR and data extraction

### **2. Product Overview**

A simple RESTful API service for PDF processing with two main functions:

1. **OCR Processing**: Extract text from PDFs using document-reader-ocr
2. **AI Extraction**: Extract structured data using custom prompts

Designed for easy Docker deployment with minimal configuration.

### **3. Core Features**

#### **3.1 Document Analysis**

- **OCR Processing**: Extract text from PDF documents using document-reader-ocr
- **AI Analysis**: Use Claude AI to structure and analyze extracted text with user-provided prompts
- **Universal Document Support**: Works with any document type based on user's prompt
- **Structured Output**: Return clean JSON with extracted information

#### **3.2 Custom Prompts**

- **User-Defined**: Users provide their own extraction prompts
- **Flexible**: Works with any document type or extraction requirement
- **No Predefined Templates**: Complete user control over prompt engineering

#### **3.3 File Handling**

- **PDF Support**: Accept only PDF files
- **Max file size**: 50MB (configurable)
- **Processing timeout**: 90 seconds
- **Temporary storage**: Auto-cleanup after processing

### **4. Technical Requirements**

#### **4.1 Authentication**

- **Client API**: Bearer token authentication (`Authorization: Bearer <token>`)
- **Configuration**: Environment variables for keys

#### **4.2 File Processing**

- **Supported formats**: PDF only
- **Max file size**: 50MB (configurable)
- **Processing timeout**: 90 seconds
- **Temporary storage**: Auto-cleanup after processing

#### **4.3 Configuration**

**Environment Variables:**

- `API_KEY` - Client authentication token
- `ANTHROPIC_API_KEY` - Claude API key
- `MAX_FILE_SIZE` - File size limit (default: 50MB)
- `PORT` - Server port (default: 8000)

#### **4.4 API Endpoints**

**Core API Endpoints:**

**POST `/ocr`**

- **Purpose**: Extract text from PDF
- **Parameters**:
  - `file`: PDF file (multipart/form-data)
- **Response**: JSON with extracted text
- **Authentication**: Bearer token required

**POST `/extract`**

- **Purpose**: Extract structured data from PDF using AI with custom prompt
- **Parameters**:
  - `prompt`: User-defined extraction instructions (JSON field)
  - `file`: PDF file (multipart/form-data)
- **Response**: JSON with structured data extraction
- **Authentication**: Bearer token required

**GET `/health`**

- **Purpose**: Basic health check
- **Response**: Simple status response
- **Authentication**: None required

#### **4.5 Response Format**

**OCR Endpoint Response**:

```json
{
  "success": true,
  "text": "Extracted text content...",
  "text_length": 1542
}
```

**Extract Endpoint Response**:

```json
{
  "success": true,
  "extracted_data": {
    "policy_number": "POL123456",
    "coverage_details": "...",
    "dates": "..."
  }
}
```

**Error Response**:

```json
{
  "success": false,
  "error": "Invalid file format. Only PDF files are supported."
}
```

### **5. Technical Architecture**

#### **5.1 Technology Stack**

- **Framework**: FastAPI (Python 3.8+)
- **OCR Engine**: document-reader-ocr (EasyOCR backend)
- **AI Service**: Claude AI (Anthropic)
- **Deployment**: Docker + Uvicorn

#### **5.2 Dependencies**

```
# Core API framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# Document processing
document-reader-ocr>=0.3.0

# AI service
anthropic==0.7.8
```

#### **5.3 System Components**

**DocumentProcessor Class**:

```python
class DocumentProcessor:
    - extract_text_from_pdf()  # Uses document-reader-ocr
    - call_claude_ai()
    - return_structured_response()
```

**FileHandler Class**:

```python
class FileHandler:
    - save_uploaded_file()
    - validate_file_type()
    - cleanup_temp_file()
```

### **6. Implementation Requirements**

#### **6.1 Simplified File Structure**

```
/app.py                 # Main FastAPI app with all endpoints
/document_processor.py  # OCR + LLM processing logic
/config.py             # Configuration management
/requirements.txt      # Python dependencies
/Dockerfile           # Container configuration
/README.md            # Setup and usage guide
```

#### **6.2 Code Standards for Top 1% Quality**

**Core Principles:**

- **Simplicity First**: If it's not essential, don't add it
- **Readability Over Cleverness**: Code should be self-documenting
- **Fail Fast**: Validate inputs immediately and return clear errors
- **Single Responsibility**: Each function does one thing well

**Python Standards:**

**Function Design:**

```python
# ✅ Good: Clear, simple, focused
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using OCR."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        text = extract_text_from_pdf(file_path)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"OCR processing failed: {str(e)}")

# ❌ Bad: Complex, unclear purpose
def process_document_with_multiple_engines_and_fallbacks(file_path, engine_type="auto", fallback_mode=True, confidence_threshold=0.8):
    # 50 lines of complex logic...
```

**Error Handling:**

```python
# ✅ Good: Specific, actionable errors
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        text = process_pdf(file)
        return {"success": True, "text": text}
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )

# ❌ Bad: Generic error handling
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile):
    try:
        # Complex processing...
        return result
    except:
        return {"error": "Something went wrong"}
```

**Type Hints:**

```python
# ✅ Good: Clear type annotations
def process_pdf(file_path: str) -> Dict[str, Any]:
    """Process PDF and return structured data."""
    pass

# ❌ Bad: No type hints
def process_pdf(file_path):
    pass
```

**Configuration Management:**

```python
# ✅ Good: Simple, clear configuration
class Config:
    API_KEY: str = os.getenv("API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB

    @classmethod
    def validate(cls) -> None:
        if not cls.API_KEY:
            raise ValueError("API_KEY environment variable is required")
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

# ❌ Bad: Complex configuration with defaults everywhere
class Config:
    def __init__(self):
        self.api_key = os.getenv("API_KEY", "default_key")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "default_key")
        # ... many more with unclear defaults
```

**API Design Standards:**

**Response Format:**

```python
# ✅ Good: Consistent, predictable responses
def success_response(data: Any) -> Dict[str, Any]:
    return {"success": True, **data}

def error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    return {"success": False, "error": message}

# ❌ Bad: Inconsistent response formats
def endpoint1():
    return {"data": result, "status": "ok"}

def endpoint2():
    return {"result": data, "success": True, "timestamp": now()}
```

**Input Validation:**

```python
# ✅ Good: Validate at the boundary
@app.post("/extract")
async def extract_data(file: UploadFile, prompt: str):
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files supported")

    # Validate prompt
    if not prompt or len(prompt.strip()) < 10:
        raise HTTPException(400, "Prompt must be at least 10 characters")

    # Process with confidence
    return process_extraction(file, prompt)

# ❌ Bad: Validation scattered throughout
@app.post("/extract")
async def extract_data(file: UploadFile, prompt: str):
    result = process_extraction(file, prompt)  # Validation happens inside
    return result
```

**Logging Standards:**

```python
# ✅ Good: Structured, useful logging
import logging

logger = logging.getLogger(__name__)

def process_pdf(file_path: str) -> str:
    logger.info(f"Processing PDF: {file_path}")

    try:
        text = extract_text(file_path)
        logger.info(f"Successfully extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        raise

# ❌ Bad: No logging or excessive logging
def process_pdf(file_path: str) -> str:
    print(f"Processing {file_path}")  # Debug prints everywhere
    return extract_text(file_path)
```

**Testing Standards:**

**Simple Test Structure:**

```python
# ✅ Good: Clear test cases
def test_extract_text_from_pdf():
    # Arrange
    test_file = "test_document.pdf"

    # Act
    result = extract_text_from_pdf(test_file)

    # Assert
    assert isinstance(result, str)
    assert len(result) > 0

def test_invalid_file_handling():
    # Arrange
    invalid_file = "nonexistent.pdf"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(invalid_file)

# ❌ Bad: Complex test setup
def test_complex_scenario_with_many_mocks():
    # 20 lines of mock setup...
    # Complex test logic...
    # Unclear assertions...
```

**Documentation Standards:**

**Function Documentation:**

```python
# ✅ Good: Clear, concise docstrings
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using OCR.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text as string

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        RuntimeError: If OCR processing fails
    """
    pass

# ❌ Bad: No documentation or overly verbose
def extract_text_from_pdf(file_path: str) -> str:
    """
    This function takes a file path as input and then processes the PDF file
    using various OCR techniques including but not limited to EasyOCR and
    other advanced algorithms that are specifically designed for text
    extraction from scanned documents...
    """
    pass
```

**Code Organization:**

**File Structure:**

```python
# ✅ Good: Logical organization
# app.py - Main FastAPI app and endpoints
# document_processor.py - Business logic for document processing
# config.py - Configuration management
# Each file has a single, clear purpose

# ❌ Bad: Everything in one file or unclear organization
# main.py - 500 lines with everything mixed together
```

**Import Organization:**

```python
# ✅ Good: Clean imports
import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile
from document_processor import DocumentProcessor

# ❌ Bad: Wild imports or unused imports
from fastapi import *
import sys, os, logging, json, time, datetime, pathlib  # All mixed together
```

**Performance Standards:**

**Simple Optimizations:**

```python
# ✅ Good: Simple, effective optimizations
def process_large_pdf(file_path: str) -> str:
    # Process in chunks for large files
    if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB
        return process_in_chunks(file_path)
    return process_normal(file_path)

# ❌ Bad: Premature optimization
def process_pdf(file_path: str) -> str:
    # Complex caching, threading, async processing for simple case
    # 100 lines of optimization code...
```

**Security Standards:**

**Input Sanitization:**

```python
# ✅ Good: Validate and sanitize inputs
def safe_filename(filename: str) -> str:
    """Ensure filename is safe for file operations."""
    return os.path.basename(filename).replace("..", "")

@app.post("/upload")
async def upload_file(file: UploadFile):
    safe_name = safe_filename(file.filename)
    # Process with safe name

# ❌ Bad: Trust user input
@app.post("/upload")
async def upload_file(file: UploadFile):
    # Use filename directly without validation
    with open(file.filename, "wb") as f:
        f.write(file.file.read())
```

**Summary of Standards:**

1. **Write self-documenting code** - Function and variable names should be clear
2. **Fail fast with clear errors** - Validate inputs immediately
3. **Keep functions small and focused** - One responsibility per function
4. **Use type hints everywhere** - Makes code more reliable
5. **Log important events** - But don't over-log
6. **Write simple tests** - Test the happy path and error cases
7. **Document the "why", not the "what"** - Comments should explain reasoning
8. **Consistent formatting** - Use a linter/formatter
9. **Simple is better than complex** - Don't add features unless essential
10. **Handle errors gracefully** - Always provide useful error messages

#### **6.3 Technical Implementation Details**

**Document Reader Integration**:

```python
# Import pattern for OCR functionality
from document_reader import extract_text_from_pdf

# Usage in document processing
def process_pdf(file_path):
    text = extract_text_from_pdf(file_path)
    return text
```

**Requirements.txt Example**:

```txt
# Core API framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# Document processing
document-reader-ocr>=0.3.0

# AI service
anthropic==0.7.8
```

**Simple Dockerfile**:

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

**Simple Health Check**:

```python
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "document-reader-api"}
```

#### **6.3 Security Considerations**

- **File Validation**: Strict PDF file type checking
- **File Size Limits**: Implement reasonable file size limits
- **Input Sanitization**: Validate all inputs
- **Temporary File Security**: Secure temporary file handling

### **7. Deployment Guide**

#### **7.1 Docker Deployment**

**Build and Run**:

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

**Environment Setup**:

```bash
# Set environment variables directly
export API_KEY=your-secret-key
export ANTHROPIC_API_KEY=your-claude-key
```

#### **7.2 Cloud Platform Deployment**

**RunPod**:

- Use Docker template deployment
- Set environment variables in RunPod dashboard
- Expose port 8000

**DigitalOcean/AWS**:

- Deploy as Docker container
- Configure environment variables
- Set up load balancer if needed

### **8. Usage Examples**

**Extract Text from PDF**:

```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf"
```

**Extract Structured Data**:

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@insurance-policy.pdf" \
  -F "prompt=Extract policy number, dates, premium amount, and insured name from this document"
```

---

**Important Notes**:

- This PRD incorporates the document-reader-ocr package from [GitHub](https://github.com/jk2081/document-reader-ocr)
- The API provides simple, reliable PDF processing with minimal configuration
- Focus on core functionality: OCR text extraction and AI-powered data extraction
- Easy deployment and maintenance with Docker
