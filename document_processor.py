"""Document processing logic for OCR and AI extraction."""

import tempfile
import os
from typing import Dict, Any, Optional
from pathlib import Path
import anthropic
from document_reader import extract_text_with_confidence
import config


class DocumentProcessor:
    """Handles PDF processing with OCR and AI extraction."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.claude_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF using OCR with confidence scoring.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict with 'text', 'confidence', and 'text_length' keys
            
        Raises:
            Exception: If OCR processing fails
        """
        try:
            result = extract_text_with_confidence(
                file_path,
                language='en',
                enable_enhancement=True,
                enhancement_method="auto"
            )
            
            return {
                'text': result['text'],
                'confidence': result['confidence_data']['average_confidence'],
                'text_length': len(result['text'])
            }
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def extract_structured_data(self, text: str, prompt: str) -> Dict[str, Any]:
        """Extract structured data using Claude AI.
        
        Args:
            text: Extracted text from OCR
            prompt: User-provided extraction instructions
            
        Returns:
            Dict with structured data from Claude
            
        Raises:
            Exception: If AI processing fails
        """
        try:
            # Construct the final prompt
            final_prompt = f"{prompt}\n\n--- Begin Document ---\n{text}\n--- End Document ---"
            
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.2,
                system="You are a document information extractor. Return structured output as JSON.",
                messages=[
                    {
                        "role": "user",
                        "content": final_prompt
                    }
                ]
            )
            
            return {"extracted_data": response.content[0].text.strip()}
            
        except Exception as e:
            raise Exception(f"AI extraction failed: {str(e)}")
    
    def process_pdf_with_prompt(self, file_path: str, prompt: str) -> Dict[str, Any]:
        """Complete pipeline: OCR + AI extraction.
        
        Args:
            file_path: Path to the PDF file
            prompt: User-provided extraction instructions
            
        Returns:
            Dict with confidence score and extracted data
            
        Raises:
            Exception: If processing fails
        """
        # First extract text with OCR
        ocr_result = self.extract_text_from_pdf(file_path)
        
        # Then extract structured data with AI
        ai_result = self.extract_structured_data(ocr_result['text'], prompt)
        
        return {
            'confidence_score': ocr_result['confidence'],
            'extracted_data': ai_result['extracted_data']
        }


class FileHandler:
    """Handles file upload, validation, and cleanup."""
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Validate that file is a supported PDF.
        
        Args:
            filename: Name of the uploaded file
            
        Returns:
            True if file type is supported, False otherwise
        """
        return filename.lower().endswith('.pdf')
    
    @staticmethod
    def save_uploaded_file(file_content: bytes) -> str:
        """Save uploaded file to temporary location.
        
        Args:
            file_content: Raw bytes of the uploaded file
            
        Returns:
            Path to the temporary file
            
        Raises:
            Exception: If file saving fails
        """
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(file_content)
                return tmp.name
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Clean up temporary file.
        
        Args:
            file_path: Path to the temporary file to remove
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            # Don't raise exception for cleanup failures
            pass