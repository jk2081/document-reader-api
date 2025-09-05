import os
import tempfile
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, Depends, Header, Form
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

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(
            status_code=400,
            detail="Uploaded file could not be processed"
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"OCR processing failed: {e}")
        
        # Provide more specific error messages
        if "document-reader" in error_message.lower():
            detail = "OCR processing failed. The PDF may be corrupted or unsupported."
        elif "memory" in error_message.lower() or "resource" in error_message.lower():
            detail = "Insufficient resources to process document. Try a smaller file."
        else:
            detail = f"OCR processing failed: {error_message}"
            
        raise HTTPException(
            status_code=500,
            detail=detail
        )


@app.post("/ocr-detailed")
async def ocr_detailed_endpoint(
    file: UploadFile,
    _: None = Depends(verify_api_key)
):
    """Extract text from PDF with bounding boxes and layout information."""
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

        # Extract text with layout information
        result = document_processor.extract_text_with_layout(temp_file_path)

        # Clean up temporary file
        os.unlink(temp_file_path)

        return {
            "success": True,
            **result
        }

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(
            status_code=400,
            detail="Uploaded file could not be processed"
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"OCR processing failed: {e}")
        
        # Provide more specific error messages
        if "document-reader" in error_message.lower():
            detail = "OCR processing failed. The PDF may be corrupted or unsupported."
        elif "memory" in error_message.lower() or "resource" in error_message.lower():
            detail = "Insufficient resources to process document. Try a smaller file."
        else:
            detail = f"OCR processing failed: {error_message}"
            
        raise HTTPException(
            status_code=500,
            detail=detail
        )


@app.post("/extract")
async def extract_endpoint(
    file: UploadFile,
    prompt: str = Form(...),
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

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(
            status_code=400,
            detail="Uploaded file could not be processed"
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Extraction failed: {e}")
        
        # Provide more specific error messages based on error type
        if "404" in error_message and "model" in error_message.lower():
            detail = "AI model not available. Please contact support."
        elif "401" in error_message or "authentication" in error_message.lower():
            detail = "AI service authentication failed. Check API configuration."
        elif "400" in error_message or "invalid" in error_message.lower():
            detail = "Invalid request to AI service. Check your prompt and try again."
        elif "timeout" in error_message.lower():
            detail = "AI processing timed out. Try with a shorter document or simpler prompt."
        elif "document-reader" in error_message.lower():
            detail = "OCR processing failed. The PDF may be corrupted or unsupported."
        elif "memory" in error_message.lower() or "resource" in error_message.lower():
            detail = "Insufficient resources. Try a smaller file or simpler prompt."
        else:
            detail = f"Processing failed: {error_message}"
            
        raise HTTPException(
            status_code=500,
            detail=detail
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=Config.PORT)