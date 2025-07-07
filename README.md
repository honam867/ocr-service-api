# OCR Service API

A robust REST API service for extracting text from PDF documents using advanced OCR technology. Built with Flask and PaddleOCR, this service provides high-quality text extraction with support for multiple languages.

## 🚀 Features

- **PDF Text Extraction**: Extract text from PDF documents with high accuracy
- **Multi-language Support**: Currently supports English (`en`) and Vietnamese (`vi`)
- **RESTful API**: Simple and intuitive REST endpoints
- **Docker Support**: Containerized deployment for easy scaling
- **Health Monitoring**: Built-in health check endpoints
- **Error Handling**: Comprehensive error handling with detailed responses
- **File Size Limits**: Configurable file size limits (default: 16MB)
- **CORS Enabled**: Cross-origin resource sharing support

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask
- **OCR Engine**: PaddleOCR
- **PDF Processing**: PyMuPDF (fitz)
- **Image Processing**: Pillow, OpenCV
- **Containerization**: Docker
- **Deployment**: Docker Compose

## 📋 Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- At least 2GB RAM (recommended for OCR processing)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ocr-service
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Verify the service is running**
   ```bash
   curl http://localhost:5000/
   ```

### Manual Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the service**
   ```bash
   python ocr-api.py
   ```

The service will be available at `http://localhost:5000`

## 📖 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "service": "OCR API Service",
  "status": "running",
  "supported_languages": ["en", "vi"],
  "supported_formats": ["pdf"],
  "version": "1.0.2",
  "endpoints": {
    "extract_text": "/extract-text (POST)",
    "health": "/ (GET)"
  }
}
```

#### 2. Extract Text from PDF
```http
POST /extract-text
```

**Request Parameters:**
- `file` (required): PDF file (max 16MB)
- `language` (optional): Language code (`en` or `vi`, default: `en`)

**Content-Type:** `multipart/form-data`

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "extracted_text": "Full extracted text from all pages",
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
        "text": "Page 1 content...",
        "line_count": 15
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses:**

- **400 Bad Request**: Invalid file format or missing file
- **413 Payload Too Large**: File exceeds 16MB limit
- **500 Internal Server Error**: OCR processing failed

## 💻 Usage Examples

### cURL
```bash
curl -X POST http://localhost:5000/extract-text \
  -F "file=@document.pdf" \
  -F "language=en"
```

### Python
```python
import requests

with open('document.pdf', 'rb') as file:
    files = {'file': file}
    data = {'language': 'en'}
    
    response = requests.post(
        'http://localhost:5000/extract-text',
        files=files,
        data=data
    )
    
    result = response.json()
    print(result['data']['extracted_text'])
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('language', 'en');

fetch('http://localhost:5000/extract-text', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Extracted text:', data.data.extracted_text);
});
```

## 🚢 Deployment

### Docker Deployment

The service includes Docker configurations for easy deployment:

- **Development**: `docker-compose.yml`
- **Production**: `docker-compose.production.yml`

#### Production Deployment
```bash
docker-compose -f docker-compose.production.yml up -d
```

### VPS Deployment

See `VPS_DEPLOYMENT.md` for detailed VPS deployment instructions.

### Docker Hub

Pre-built images are available on Docker Hub:
```bash
docker pull jackipro1509/ocr-service:latest
```

## 🔧 Configuration

### Environment Variables

- `TZ`: Timezone (default: `Asia/Shanghai`)
- `MAX_CONTENT_LENGTH`: Maximum file size in bytes (default: 16MB)

### File Structure
```
ocr-service/
├── ocr-api.py              # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose for development
├── docker-compose.production.yml  # Production configuration
├── api-specs.md          # Detailed API specifications
├── temp_uploads/         # Temporary file storage
├── uploads/              # File upload directory
├── VPS_DEPLOYMENT.md     # VPS deployment guide
└── DOCKER_DEPLOYMENT.md  # Docker deployment guide
```

## 🧪 Health Monitoring

The service includes health check endpoints that can be used for monitoring:

```bash
# Check service status
curl http://localhost:5000/

# Docker health check is automatically configured
docker ps  # Shows health status
```

## 🔍 Troubleshooting

### Common Issues

1. **Memory Issues**: OCR processing requires significant memory. Ensure at least 2GB RAM is available.

2. **File Size Limits**: Default limit is 16MB. Larger files will be rejected with a 413 error.

3. **Language Support**: Currently supports English (`en`) and Vietnamese (`vi`) only.

4. **PDF Compatibility**: The service works with standard PDF files. Scanned images within PDFs are processed via OCR.

### Logs

View service logs:
```bash
# Docker logs
docker logs ocr-service

# Direct Python execution
python ocr-api.py  # Logs printed to console
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API specifications in `api-specs.md`
3. Open an issue on the repository

## 🔄 Version History

- **v1.0.2**: Current version with improved error handling and stability
- **v1.0.1**: Added multi-language support
- **v1.0.0**: Initial release with basic OCR functionality 