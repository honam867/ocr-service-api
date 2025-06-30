# OCR API Specifications

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Health Check
```
GET /
```
**Response:**
```json
{
  "service": "OCR API Service",
  "status": "running",
  "supported_languages": ["en", "vi"],
  "supported_formats": ["pdf"],
  "version": "1.0.0"
}
```

### 2. Extract Text from PDF
```
POST /extract-text
```

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): PDF file upload
  - `language` (optional): `"en"` or `"vi"` (default: `"en"`)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "extracted_text": "string",
    "language": "en",
    "metrics": {
      "execution_time_seconds": 1.234,
      "character_count": 1500,
      "word_count": 250,
      "line_count": 45,
      "page_count": 3
    },
    "file_info": {
      "filename": "document.pdf",
      "size_mb": 2.5
    },
    "page_details": [
      {
        "page": 1,
        "character_count": 500,
        "line_count": 15,
        "has_error": false
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses:**

**400 - Bad Request:**
```json
{
  "error": "No file provided",
  "message": "Please upload a PDF file using the 'file' parameter"
}
```

**413 - File Too Large:**
```json
{
  "error": "File too large",
  "message": "Maximum file size is 16MB"
}
```

**500 - Server Error:**
```json
{
  "success": false,
  "error": "Processing failed",
  "message": "Error details",
  "execution_time_seconds": 0.123,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Integration Examples

### cURL
```bash
curl -X POST http://localhost:5000/extract-text \
  -F "file=@document.pdf" \
  -F "language=en"
```

### JavaScript (Fetch)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('language', 'en');

fetch('http://localhost:5000/extract-text', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python (requests)
```python
import requests

files = {'file': open('document.pdf', 'rb')}
data = {'language': 'en'}

response = requests.post('http://localhost:5000/extract-text', 
                        files=files, data=data)
result = response.json()
``` 