# Python Best Practices - Document Reader API

## Simple & Robust Code Standards

### **1. Project Structure**

Keep it simple - flat file structure for easy maintenance:

```
document-reader-api/
├── app.py                   # Main FastAPI app
├── admin.py                 # Admin UI routes  
├── document_processor.py    # OCR + LLM logic
├── config.py                # Configuration
├── templates/               # HTML templates
│   ├── login.html
│   ├── dashboard.html
│   └── keys.html
├── static/                  # CSS files
│   └── style.css
├── data/                    # Local storage
│   └── config.json
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

### **2. Python Best Practices**

#### **2.1 Naming Conventions**
- **Files**: `snake_case.py`
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

#### **2.2 Type Hints (Essential)**

Always use type hints for function parameters and returns:

```python
# ✅ GOOD - Clear types
from pathlib import Path
from typing import Dict, Optional

def process_pdf(file_path: Path) -> Dict[str, any]:
    """Process PDF with clear types."""
    pass

async def extract_data(text: str, prompt: str) -> Optional[Dict]:
    """Extract data with async typing."""
    pass

# ❌ BAD - No type hints
def process_pdf(file_path):
    pass
```

#### **2.3 Docstrings (Required for Public Functions)**

Use simple, clear docstrings:

```python
def extract_text_from_pdf(file_path: Path) -> Dict[str, any]:
    """Extract text from PDF using OCR.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dict with 'text' and 'confidence' keys
        
    Raises:
        FileNotFoundError: If PDF doesn't exist
    """
    pass
```

#### **2.4 Simple Error Handling**

Keep error handling simple and clear:

```python
# ✅ GOOD - Simple and clear
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile):
    try:
        # Basic validation
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Only PDF files supported")
            
        # Process file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(await file.read())
            result = extract_text_with_confidence(tmp.name)
            os.unlink(tmp.name)
            
        return {
            "success": True,
            "text": result['text'],
            "confidence": result['confidence_data']['average_confidence']
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ✅ GOOD - Log errors for debugging
import logging
logger = logging.getLogger(__name__)

try:
    # risky operation
    pass
except Exception as e:
    logger.error(f"Processing failed: {e}")
    raise HTTPException(500, "Processing failed")
```

### **3. FastAPI Patterns**

#### **3.1 Simple API Endpoints**

Keep endpoints simple and focused:

```python
from fastapi import FastAPI, UploadFile, HTTPException
from document_reader import extract_text_with_confidence
import tempfile
import os

app = FastAPI(title="Document Reader API")

@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "healthy", "service": "document-reader-api"}

@app.post("/ocr")
async def extract_text(file: UploadFile):
    """Extract text from PDF with confidence score."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files supported")
    
    # Process file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        result = extract_text_with_confidence(tmp.name)
        os.unlink(tmp.name)
    
    return {
        "success": True,
        "text": result['text'],
        "confidence": result['confidence_data']['average_confidence']
    }

@app.post("/extract")
async def extract_structured_data(file: UploadFile, prompt: str):
    """Extract structured data using custom prompt."""
    # OCR first
    ocr_result = await extract_text(file)
    
    # Then call Claude AI
    claude_result = await call_claude_api(ocr_result['text'], prompt)
    
    return {
        "success": True,
        "confidence": ocr_result['confidence'],
        "extracted_data": claude_result
    }
```

#### **3.2 Simple Response Format**

Keep responses consistent and simple:

```python
# ✅ Success responses
{
    "success": true,
    "text": "extracted text...",
    "confidence": 0.85
}

# ✅ Error responses  
{
    "success": false,
    "error": "File too large"
}
```

### **4. Configuration**

#### **4.1 Simple Environment Variables**

Use environment variables for configuration:

```python
# config.py
import os

# Required settings
API_KEY = os.getenv("API_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") 
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Optional settings with defaults
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 52428800))  # 50MB
PORT = int(os.getenv("PORT", 8000))

# Validate required settings
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable required")
```

#### **4.2 .env Example**

```bash
# .env.example
API_KEY=your-secret-api-key-here
ADMIN_PASSWORD=admin123
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
MAX_FILE_SIZE=52428800
PORT=8000
```

### **5. Basic Testing**

#### **5.1 Simple Test Structure**

Keep tests simple and focused on core functionality:

```python
# test_app.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ocr_endpoint_no_file():
    """Test OCR endpoint without file."""
    response = client.post("/ocr")
    assert response.status_code == 422  # Validation error

def test_ocr_endpoint_invalid_file():
    """Test OCR endpoint with non-PDF file."""
    files = {"file": ("test.txt", b"content", "text/plain")}
    response = client.post("/ocr", files=files)
    assert response.status_code == 400
```

#### **5.2 Testing Guidelines**

- **Test core functionality**: Health check, file upload, basic processing
- **Test error cases**: Invalid files, missing parameters
- **Keep tests simple**: Focus on behavior, not implementation
- **Use real files sparingly**: Mock when possible to speed up tests

### **6. Basic Security**

#### **6.1 File Validation**

Always validate uploaded files:

```python
# ✅ Basic file validation
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile):
    # Check file extension
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files supported")
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    
    # Process file...
```

#### **6.2 API Authentication**

Simple Bearer token authentication:

```python
from fastapi import Depends, HTTPException, Header

def verify_api_key(authorization: str = Header(None)):
    """Verify API key from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "API key required")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(401, "Invalid API key")
    
    return True

@app.post("/ocr", dependencies=[Depends(verify_api_key)])
async def protected_endpoint(file: UploadFile):
    # Protected endpoint logic
    pass
```

#### **6.3 Don't Log Sensitive Data**

```python
# ✅ GOOD - Safe logging
logger.info(f"Processing file: {file.filename}")
logger.info(f"File size: {len(content)} bytes")

# ❌ BAD - Don't log content
logger.info(f"Document text: {extracted_text}")  # Never do this
```

### **7. Document Reader Integration**

#### **7.1 Using the Document Reader Package**

Install and use the local wheel package:

```python
# Import from the installed package
from document_reader import extract_text_with_confidence

# Basic usage
def process_pdf_file(file_path: str) -> Dict[str, any]:
    """Process PDF and get text with confidence."""
    result = extract_text_with_confidence(
        file_path,
        language='en',
        enable_enhancement=True,
        enhancement_method="auto"
    )
    
    return {
        'text': result['text'],
        'confidence': result['confidence_data']['average_confidence']
    }
```

#### **7.2 File Processing Pattern**

Always use temporary files for processing:

```python
import tempfile
import os

@app.post("/ocr")
async def process_pdf(file: UploadFile):
    """Process uploaded PDF file."""
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name
    
    try:
        # Process with document reader
        result = extract_text_with_confidence(temp_path)
        return {
            "success": True,
            "text": result['text'],
            "confidence": result['confidence_data']['average_confidence']
        }
    finally:
        # Always clean up
        os.unlink(temp_path)
```

### **8. Essential Dependencies**

#### **8.1 Requirements.txt**

```txt
# Local wheel package
../document-reader/dist/document_reader-0.3.0-py3-none-any.whl

# FastAPI stack
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
jinja2==3.1.2

# AI service
anthropic==0.7.8

# Development (optional)
pytest==7.4.3
black==23.9.1
```

### **9. Code Formatting**

#### **9.1 Use Black for Formatting**

```bash
# Install and run black
pip install black
black *.py

# Or with specific line length
black --line-length 88 *.py
```

#### **9.2 Basic Linting**

```bash
# Check for basic issues
python -m py_compile app.py
python -m flake8 app.py --max-line-length=88
```

---

## **Key Reminders**

- **Keep it simple**: Favor readable code over clever code
- **Use type hints**: Always type your functions
- **Handle errors gracefully**: Don't let exceptions crash the API
- **Validate inputs**: Check file types and sizes
- **Clean up resources**: Always remove temporary files
- **Test core functionality**: Health check and main endpoints
- **Follow the PRD**: Stick to the simplified architecture

