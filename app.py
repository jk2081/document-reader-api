"""Main FastAPI application for Document Reader API."""

import os
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import config
from document_processor import DocumentProcessor, FileHandler
from admin import admin_router


# Initialize FastAPI app
app = FastAPI(
    title="Document Reader API",
    description="Simple API for PDF OCR and data extraction",
    version="1.0.0"
)

# Initialize processors
doc_processor = DocumentProcessor()
file_handler = FileHandler()

# Create data directory if it doesn't exist
os.makedirs(config.DATA_DIR, exist_ok=True)

# Include admin router
app.include_router(admin_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


def verify_api_key(authorization: str = Header(None)) -> bool:
    """Verify API key from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        True if valid API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="API key required")
    
    token = authorization.replace("Bearer ", "")
    if token != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True


@app.get("/health")
async def health() -> Dict[str, str]:
    """Basic health check endpoint.
    
    Returns:
        Simple status response
    """
    return {"status": "healthy", "service": "document-reader-api"}


@app.post("/ocr", dependencies=[Depends(verify_api_key)])
async def extract_text(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Extract text from PDF with confidence scoring.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        JSON with extracted text and confidence score
        
    Raises:
        HTTPException: If file processing fails
    """
    try:
        # Validate file type
        if not file.filename or not file_handler.validate_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail="File too large"
            )
        
        # Save to temporary file
        temp_path = file_handler.save_uploaded_file(content)
        
        try:
            # Process with OCR
            result = doc_processor.extract_text_from_pdf(temp_path)
            
            return {
                "success": True,
                "text": result['text'],
                "confidence_score": result['confidence'],
                "text_length": result['text_length']
            }
            
        finally:
            # Always clean up
            file_handler.cleanup_temp_file(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Processing failed: {str(e)}"
        )


@app.post("/extract", dependencies=[Depends(verify_api_key)])
async def extract_structured_data(
    file: UploadFile = File(...),
    prompt: str = Form(...)
) -> Dict[str, Any]:
    """Extract structured data from PDF using AI with custom prompt.
    
    Args:
        file: Uploaded PDF file
        prompt: User-defined extraction instructions
        
    Returns:
        JSON with structured data extraction
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Validate file type
        if not file.filename or not file_handler.validate_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail="File too large"
            )
        
        # Validate prompt
        if not prompt.strip():
            raise HTTPException(
                status_code=400, 
                detail="Prompt is required"
            )
        
        # Save to temporary file
        temp_path = file_handler.save_uploaded_file(content)
        
        try:
            # Process with OCR + AI
            result = doc_processor.process_pdf_with_prompt(temp_path, prompt)
            
            return {
                "success": True,
                "confidence_score": result['confidence_score'],
                "extracted_data": result['extracted_data']
            }
            
        finally:
            # Always clean up
            file_handler.cleanup_temp_file(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Processing failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)