# Frappe RunPod Integration Settings

This document outlines the connection settings needed to integrate a Frappe Policy Reader app with the RunPod document reader API.

## RunPod Connection Settings

Based on the working curl command:
```bash
curl -X POST "https://newh9pbsqw7csx-8000.proxy.runpod.net/extract" \
  -H "Authorization: Bearer doc-reader-1123" \
  -F "file=@document.pdf" \
  -F "prompt=Extract policy information"
```

### Core Settings Required

#### 1. RunPod Instance ID
- **Field**: `runpod_instance_id`
- **Type**: Data
- **Example**: `newh9pbsqw7csx`
- **Description**: The unique instance identifier from your RunPod endpoint

#### 2. Port Number
- **Field**: `runpod_port`
- **Type**: Int
- **Default**: `8000`
- **Description**: The port your document reader API runs on

#### 3. API Authentication Token
- **Field**: `api_bearer_token`
- **Type**: Password
- **Example**: `doc-reader-1123`
- **Description**: Bearer token for API authentication

#### 4. Base RunPod Domain
- **Field**: `runpod_base_domain`
- **Type**: Data
- **Default**: `proxy.runpod.net`
- **Description**: The standard RunPod proxy domain

### URL Construction Logic

```python
def get_runpod_url(instance_id, port, base_domain="proxy.runpod.net"):
    """Construct RunPod API URL from components"""
    return f"https://{instance_id}-{port}.{base_domain}"

# Example output: https://newh9pbsqw7csx-8000.proxy.runpod.net
```

### Optional Settings

- **Request Timeout**
  - Field: `request_timeout`
  - Type: Int
  - Default: `60`
  - Description: API request timeout in seconds

- **Enable SSL Verification**
  - Field: `ssl_verify`
  - Type: Check
  - Default: `1` (True)
  - Description: Verify SSL certificates for HTTPS requests

- **Connection Retry Attempts**
  - Field: `retry_attempts`
  - Type: Int
  - Default: `3`
  - Description: Number of retry attempts for failed requests

## API Endpoints

The RunPod instance provides two main endpoints:

### 1. OCR Endpoint
- **URL**: `/ocr`
- **Method**: POST
- **Purpose**: Extract raw text from PDF documents

### 2. Extract Endpoint
- **URL**: `/extract`
- **Method**: POST
- **Purpose**: Extract structured data using AI with custom prompts

## Example Frappe Integration

```python
import requests
import frappe

def call_runpod_api(file_content, operation="extract", prompt=None):
    """Call RunPod document reader API from Frappe"""
    
    # Get settings
    settings = frappe.get_single("RunPod Settings")
    
    # Construct URL
    url = f"https://{settings.runpod_instance_id}-{settings.runpod_port}.{settings.runpod_base_domain}/{operation}"
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {settings.api_bearer_token}"
    }
    
    # Prepare form data
    files = {"file": file_content}
    data = {"prompt": prompt} if prompt else {}
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            files=files, 
            data=data,
            timeout=settings.request_timeout
        )
        return response.json()
    except Exception as e:
        frappe.log_error(f"RunPod API Error: {str(e)}")
        return {"error": str(e)}
```

This modular approach separates the dynamic parts (instance ID, port) from the static RunPod URL structure, making it easier to manage and update instance configurations.