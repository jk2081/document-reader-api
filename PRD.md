# Product Requirements Document (PRD)

## Document Reader API

### **1. Executive Summary**

**Product Name**: Document Reader API  
**Version**: 1.0.0  
**Target Users**: Developers needing simple PDF OCR and data extraction  
**Timeline**: 1-2 weeks development

### **2. Product Overview**

A lightweight RESTful API service for PDF processing with two main functions:
1. **OCR Processing**: Extract text from PDFs with confidence scoring
2. **AI Extraction**: Extract structured data using configurable prompts

Designed for easy Docker deployment on cloud platforms (RunPod, DigitalOcean, AWS) with a simple admin interface for configuration.

### **3. Core Features**

#### **3.1 Document Analysis**

- **OCR Processing**: Extract text from PDF documents using EasyOCR
- **Confidence Scoring**: OCR confidence assessment for quality transparency
- **AI Analysis**: Use Claude AI to structure and analyze extracted text with user-provided prompts
- **Universal Document Support**: Works with any document type based on user's prompt
- **Structured Output**: Return clean JSON with extracted information

#### **3.2 Custom Prompts**

- **User-Defined**: Users provide their own extraction prompts
- **Flexible**: Works with any document type or extraction requirement
- **No Predefined Templates**: Complete user control over prompt engineering

#### **3.3 File Handling**

- **PDF Support**: Accept only PDF files
- **Temporary Storage**: Secure temporary file handling
- **Cleanup**: Automatic cleanup of temporary files

### **4. Technical Requirements**

#### **4.1 Authentication**
- **Client API**: Bearer token authentication (`Authorization: Bearer <token>`)
- **Admin UI**: Password-based login with sessions
- **Configuration**: Environment variables for keys and passwords

#### **4.2 File Processing**
- **Supported formats**: PDF only
- **Max file size**: 50MB (configurable)
- **Processing timeout**: 90 seconds
- **Temporary storage**: Auto-cleanup after processing

#### **4.3 Configuration**
**Environment Variables:**
- `API_KEY` - Client authentication token
- `ADMIN_PASSWORD` - Admin UI password  
- `ANTHROPIC_API_KEY` - Claude API key
- `MAX_FILE_SIZE` - File size limit (default: 50MB)
- `PORT` - Server port (default: 8000)

#### **4.4 API Endpoints**

**Core API Endpoints:**

**POST `/ocr`**
- **Purpose**: Extract text from PDF with confidence scoring
- **Parameters**: `file`: PDF file (multipart/form-data)
- **Response**: JSON with extracted text and confidence score
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

**Admin UI Endpoints:**

**GET `/admin`**
- **Purpose**: Admin login page
- **Authentication**: Session-based login

**GET `/admin/dashboard`**
- **Purpose**: Configuration dashboard
- **Authentication**: Admin session required

**GET `/admin/keys`**
- **Purpose**: Manage API keys
- **Authentication**: Admin session required


#### **4.5 Response Format**

**OCR Endpoint Response**:
```json
{
  "success": true,
  "text": "Extracted text content...",
  "confidence_score": 0.85,
  "text_length": 1542
}
```

**Extract Endpoint Response**:
```json
{
  "success": true,
  "confidence_score": 0.85,
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

### **4.6 Admin Interface**

**Simple Web UI for Configuration:**

**Login System:**
- Admin password set via `ADMIN_PASSWORD` environment variable
- Session-based authentication
- Basic HTML login form

**Dashboard Features:**
- Service health status
- Basic usage statistics
- Configuration overview

**API Key Management:**
- Add/remove client API keys
- Update LLM API key (Anthropic)
- View key usage (basic)

**Technical Implementation:**
- FastAPI with Jinja2 templates
- Simple HTML forms with basic CSS
- Local file storage for configuration
- No external database required

### **5. Technical Architecture**

#### **5.1 Technology Stack**

- **Framework**: FastAPI (Python 3.11+)
- **OCR Engine**: EasyOCR (stable on macOS ARM)
- **AI Service**: Claude AI (Anthropic)
- **File Processing**: PyMuPDF (fitz)
- **Image Processing**: PIL/Pillow
- **Deployment**: Docker + Uvicorn

#### **5.2 Dependencies**

```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
easyocr==1.7.0
pymupdf==1.23.8
pillow==10.1.0
numpy==1.24.3
anthropic==0.7.8
```

#### **5.3 System Components**

**DocumentProcessor Class**:

```python
class DocumentProcessor:
    - validate_prompt_type()
    - extract_text_from_pdf()
    - assess_ocr_confidence()
    - apply_prompt_template()
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

**PromptManager Class**:

```python
class PromptManager:
    - load_prompts()
    - validate_prompt_type()
    - get_prompt_template()
```

### **6. Implementation Requirements**

#### **6.1 Simplified File Structure**

```
/app.py                 # Main FastAPI app with all endpoints
/admin.py              # Admin UI routes and templates
/document_processor.py  # OCR + LLM processing logic
/config.py             # Configuration management
/templates/            # HTML templates for admin UI
  /login.html
  /dashboard.html
  /keys.html
/static/               # CSS for admin UI
  /style.css
/data/                 # Local storage
  /config.json         # API keys and settings
/requirements.txt      # Python dependencies
/Dockerfile           # Container configuration
/.env.example         # Environment template
/README.md            # Setup and usage guide
```

**Dependencies from existing codebase:**
- Reuse `document_reader/` OCR functionality
- Install `../document-reader/dist/document_reader-0.3.0-py3-none-any.whl`

#### **6.2 Technical Implementation Details**

**Document Reader Integration:**
```python
# Import pattern for OCR functionality
from document_reader import extract_text_with_confidence

# Usage in document processing
def process_pdf(file_path):
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

**Requirements.txt Example:**
```txt
# Local wheel installation
../document-reader/dist/document_reader-0.3.0-py3-none-any.whl

# FastAPI stack
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
jinja2==3.1.2

# AI service
anthropic==0.7.8

# Document reader dependencies (included via wheel)
# easyocr>=1.6.0
# PyMuPDF>=1.23.0
# pillow>=9.0.0
# numpy>=1.21.0
# opencv-python>=4.5.0
# scikit-image>=0.19.0
```



**Simple Dockerfile:**
```dockerfile
FROM python:3.11

WORKDIR /app

# Copy wheel file and requirements
COPY ../document-reader/dist/document_reader-0.3.0-py3-none-any.whl /tmp/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Simple health check
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Simple Health Check:**
```python
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "document-reader-api"}
```


#### **6.2 Integration Points**

- **Source Repository**: This API will be built in a separate repository (`document-reader-api`)
- **Existing Code**: Leverage current `orchestrator.py` logic from `document-reader` repo
- **OCR Engine**: Import and use existing `src/document_reader/ocr_reader.py` functionality
- **Prompt System**: Copy and adapt existing `prompts.json` structure
- **Code Reuse**: Reference existing `document-reader` codebase as foundation
- **Error Handling**: Comprehensive error handling and logging

#### **6.3 Security Considerations**

- **File Validation**: Strict PDF file type checking
- **File Size Limits**: Implement reasonable file size limits
- **Rate Limiting**: Prevent API abuse
- **Input Sanitization**: Validate all inputs
- **Temporary File Security**: Secure temporary file handling

### **7. Deployment Guide**

#### **7.1 Docker Deployment**

**Build and Run:**
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

**Environment Setup:**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

#### **7.2 Cloud Platform Deployment**

**RunPod:**
- Use Docker template deployment
- Set environment variables in RunPod dashboard
- Expose port 8000

**DigitalOcean/AWS:**
- Deploy as Docker container
- Configure environment variables
- Set up load balancer if needed

#### **7.3 Initial Configuration**

1. **Access Admin UI**: Navigate to `http://your-server:8000/admin`
2. **Login**: Use `ADMIN_PASSWORD` from environment
3. **Configure API Keys**: Set client API keys in admin panel
4. **Update Prompts**: Customize prompt templates as needed
5. **Test API**: Use `/health` endpoint to verify deployment

### **8. Usage Example**

**Extract Text from PDF:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf"
```

**Extract Structured Data:**
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@insurance-policy.pdf" \
  -F "prompt=Extract policy number, dates, premium amount, and insured name from this document"
```

---

**Important Notes**:

- This PRD is based on the existing `document-reader` repository functionality and orchestrator script
- The API will be built as a separate project (`document-reader-api`) while leveraging existing code
- The implementation should reuse the current codebase components while providing a clean, scalable API interface
- The new API repository should reference and adapt functionality from the existing `document-reader` project
