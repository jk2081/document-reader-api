import os
import tempfile
import logging
from typing import Dict, Any, List, Optional
from document_reader import extract_text_from_pdf, extract_text_with_confidence
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
    
    def extract_text_with_layout(self, file_path: str) -> Dict[str, Any]:
        """Extract text with bounding boxes and confidence scores."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            # Use the more detailed extraction function
            result = extract_text_with_confidence(file_path)
            logger.info(f"Successfully extracted text with layout information")
            
            # Process the result to include bounding boxes and confidence
            if isinstance(result, dict):
                return {
                    "text": result.get("text", ""),
                    "text_length": len(result.get("text", "")),
                    "bounding_boxes": result.get("bounding_boxes", []),
                    "confidence_scores": result.get("confidence_scores", []),
                    "layout_info": result.get("layout_info", {})
                }
            else:
                # Fallback to simple text extraction
                text = str(result)
                return {
                    "text": text,
                    "text_length": len(text),
                    "bounding_boxes": [],
                    "confidence_scores": [],
                    "layout_info": {}
                }
                
        except Exception as e:
            logger.error(f"OCR processing with layout failed: {e}")
            # Fallback to simple text extraction
            try:
                text = extract_text_from_pdf(file_path)
                return {
                    "text": text,
                    "text_length": len(text),
                    "bounding_boxes": [],
                    "confidence_scores": [],
                    "layout_info": {}
                }
            except Exception as fallback_error:
                logger.error(f"Fallback OCR processing failed: {fallback_error}")
                raise RuntimeError(f"OCR processing failed: {str(e)}")
    
    def extract_structured_data(self, text: str, prompt: str) -> Dict[str, Any]:
        """Extract structured data using Claude AI."""
        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
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
    
