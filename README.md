# OCR API Service

A powerful REST API service for extracting text from PDF files using PaddleOCR. Supports both English and Vietnamese languages with detailed metrics and performance information.

## 🚀 Features

- **PDF Text Extraction**: Extract text from PDF files with high accuracy
- **Multi-language Support**: English (`en`) and Vietnamese (`vi`)
- **Performance Metrics**: Execution time, character count, word count, line count
- **Page-by-page Analysis**: Detailed breakdown per PDF page
- **RESTful API**: Easy integration with any application
- **File Upload**: Support for PDF files up to 16MB
- **Error Handling**: Comprehensive error responses
- **Clean Architecture**: Automatic temporary file cleanup

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🛠️ Installation & Setup

### 1. Clone or Download the Project

Save the `ocr-api.py` and `requirements.txt` files in your project directory.

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv ocr-env

# Activate virtual environment
# On Windows:
ocr-env\Scripts\activate
# On macOS/Linux:
source ocr-env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The first time you run the service, PaddleOCR will automatically download the required models for English and Vietnamese. This may take a few minutes.

### 4. Run the Service

```bash
python ocr-api.py
```

You should see output like:
```
🚀 Starting OCR API Service...
📚 Supported languages: English (en), Vietnamese (vi)
📄 Supported formats: PDF
🌐 Access the API at: http://localhost:5000
📖 API Documentation: http://localhost:5000
🔧 Test endpoint: POST http://localhost:5000/extract-text
```

## 📖 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
- **URL**: `/`
- **Method**: `GET`
- **Description**: Check if the service is running

**Response:**
```json
{
  "service": "OCR API Service",
  "status": "running",
  "supported_languages": ["en", "vi"],
  "supported_formats": ["pdf"],
  "version": "1.0.0",
  "endpoints": {
    "extract_text": "/extract-text (POST)",
    "health": "/ (GET)"
  }
}
```

#### 2. Extract Text from PDF
- **URL**: `/extract-text`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

**Parameters:**
- `file` (required): PDF file to process
- `language` (optional): Language for OCR (`en` or `vi`). Default: `en`

**Response Example:**
```json
{
  "success": true,
  "data": {
    "extracted_text": "Your extracted text here...",
    "language": "en",
    "metrics": {
      "execution_time_seconds": 2.45,
      "character_count": 1250,
      "word_count": 180,
      "line_count": 25,
      "page_count": 3
    },
    "file_info": {
      "filename": "document.pdf",
      "size_mb": 0.85
    },
    "page_details": [
      {
        "page": 1,
        "character_count": 450,
        "line_count": 8,
        "has_error": false
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:45.123456",
  "processing_info": {
    "ocr_engine": "PaddleOCR",
    "version": "1.0.0"
  }
}
```

## 🧪 Testing with Postman

### Method 1: Using Postman GUI

1. **Open Postman**

2. **Create a New Request**
   - Set method to `POST`
   - URL: `http://localhost:5000/extract-text`

3. **Set up the Request**
   - Go to the `Body` tab
   - Select `form-data`
   - Add key `file` with type `File`
   - Choose your PDF file
   - (Optional) Add key `language` with value `en` or `vi`

4. **Send the Request**
   - Click `Send`
   - Review the response

### Method 2: Using cURL

```bash
# Test health check
curl http://localhost:5000/

# Extract text (English)
curl -X POST \
  -F "file=@/path/to/your/document.pdf" \
  -F "language=en" \
  http://localhost:5000/extract-text

# Extract text (Vietnamese)
curl -X POST \
  -F "file=@/path/to/your/document.pdf" \
  -F "language=vi" \
  http://localhost:5000/extract-text
```

### Method 3: Postman Collection

You can import this collection into Postman:

```json
{
  "info": {
    "name": "OCR API Service",
    "description": "Collection for testing OCR API endpoints"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:5000/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": [""]
        }
      }
    },
    {
      "name": "Extract Text (English)",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": []
            },
            {
              "key": "language",
              "value": "en",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:5000/extract-text",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["extract-text"]
        }
      }
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables (Optional)

You can customize the service by modifying these variables in `ocr-api.py`:

```python
# File size limit (default: 16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Server port (default: 5000)
app.run(port=5000)

# Upload folder (default: temp_uploads)
UPLOAD_FOLDER = 'temp_uploads'
```

## ⚠️ Important Notes

1. **First Run**: The service will download OCR models on first startup (may take 5-10 minutes)
2. **File Size**: Maximum file size is 16MB
3. **Supported Formats**: Currently only PDF files are supported
4. **Memory Usage**: Large PDFs may require significant memory
5. **Temporary Files**: Files are automatically cleaned up after processing

## 🐛 Troubleshooting

### Common Issues

1. **PaddleOCR Installation Failed**
   ```bash
   pip install --upgrade pip
   pip install paddlepaddle paddleocr
   ```

2. **PyMuPDF Installation Issues**
   ```bash
   pip install --upgrade pymupdf
   ```

3. **Memory Issues with Large PDFs**
   - Reduce PDF file size
   - Increase system memory
   - Process pages in batches

4. **Model Download Issues**
   - Ensure stable internet connection
   - Clear PaddleOCR cache: `~/.paddleocr/`

### Error Responses

The API returns detailed error messages:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Detailed error message",
  "execution_time_seconds": 0.123,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

## 📊 Performance

- **Average processing time**: 2-5 seconds per page
- **Accuracy**: High for clear, well-formatted documents
- **Supported languages**: English and Vietnamese
- **Maximum file size**: 16MB
- **Concurrent requests**: Supported (Flask threaded mode)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error messages in the API response
3. Check the console logs where the service is running

## 📝 License

This project is open source and available under the MIT License. 