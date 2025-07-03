# Docker Deployment Guide for OCR Service

## 🐳 Docker Image Information

**Image Name**: `jackipro1509/ocr-service:latest`  
**Registry**: Docker Hub  
**Image Size**: ~2.6GB  
**Base Image**: Ubuntu 20.04  

## 🚀 Quick Start for Users

### Prerequisites
- Docker installed on your system
- At least 4GB of free disk space
- 2GB+ RAM recommended

### Pull and Run the Image

```bash
# Pull the image from Docker Hub
docker pull jackipro1509/ocr-service:latest

# Run the container
docker run -d \
  --name ocr-service \
  -p 5000:5000 \
  -v $(pwd)/uploads:/temp_uploads \
  jackipro1509/ocr-service:latest
```

### Windows PowerShell
```powershell
# Pull the image
docker pull jackipro1509/ocr-service:latest

# Run the container (Windows)
docker run -d --name ocr-service -p 5000:5000 -v ${PWD}/uploads:/temp_uploads jackipro1509/ocr-service:latest
```

## 🔧 Usage Examples

### 1. Basic Usage
Once the container is running, you can access the service at `http://localhost:5000`

### 2. Health Check
```bash
curl http://localhost:5000/
```

### 3. Extract Text from PDF
```bash
# Upload a PDF file for OCR processing
curl -X POST \
  -F "file=@your-document.pdf" \
  -F "language=en" \
  http://localhost:5000/extract-text
```

## 🛠️ Advanced Configuration

### Custom Port Mapping
```bash
# Run on port 8080 instead of 5000
docker run -d \
  --name ocr-service \
  -p 8080:5000 \
  -v $(pwd)/uploads:/temp_uploads \
  jackipro1509/ocr-service:latest
```

### Memory Limits
```bash
# Limit memory usage to 2GB
docker run -d \
  --name ocr-service \
  -p 5000:5000 \
  --memory=2g \
  -v $(pwd)/uploads:/temp_uploads \
  jackipro1509/ocr-service:latest
```

### Environment Variables
```bash
# Set timezone
docker run -d \
  --name ocr-service \
  -p 5000:5000 \
  -e TZ=America/New_York \
  -v $(pwd)/uploads:/temp_uploads \
  jackipro1509/ocr-service:latest
```

## 📂 Volume Mounting

The service uses `/temp_uploads` directory for temporary file storage. You should mount a local directory to this path:

```bash
# Create local uploads directory
mkdir -p uploads

# Mount it to the container
docker run -d \
  --name ocr-service \
  -p 5000:5000 \
  -v $(pwd)/uploads:/temp_uploads \
  jackipro1509/ocr-service:latest
```

## 🔍 Container Management

### Check Container Status
```bash
docker ps
```

### View Container Logs
```bash
docker logs ocr-service
```

### Stop the Container
```bash
docker stop ocr-service
```

### Remove the Container
```bash
docker rm ocr-service
```

### Update to Latest Version
```bash
# Stop and remove old container
docker stop ocr-service
docker rm ocr-service

# Pull latest image
docker pull jackipro1509/ocr-service:latest

# Run new container
docker run -d \
  --name ocr-service \
  -p 5000:5000 \
  -v $(pwd)/uploads:/temp_uploads \
  jackipro1509/ocr-service:latest
```

## 🌐 Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  ocr-service:
    image: jackipro1509/ocr-service:latest
    container_name: ocr-service
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/temp_uploads
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with Docker Compose:
```bash
# Start the service
docker-compose up -d

# Stop the service
docker-compose down

# View logs
docker-compose logs -f
```

## 🔐 Security Considerations

1. **File Size Limits**: The service accepts files up to 16MB
2. **Supported Formats**: Only PDF files are supported
3. **Network Security**: Consider running behind a reverse proxy (nginx/traefik) in production
4. **File Cleanup**: Temporary files are automatically cleaned up after processing

## 🐛 Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker logs ocr-service

# Check if port is already in use
netstat -tulpn | grep :5000
```

### Memory Issues
```bash
# Check container resource usage
docker stats ocr-service

# Increase memory limit
docker update --memory=4g ocr-service
```

### Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER uploads/
chmod 755 uploads/
```

## 📊 API Documentation

Once running, visit `http://localhost:5000` for complete API documentation.

### Supported Languages
- English (`en`)
- Vietnamese (`vi`)

### Supported Formats
- PDF files only

### Response Format
The API returns JSON responses with:
- Extracted text
- Performance metrics
- Page-by-page analysis
- Error handling

## 🔗 Links

- **Docker Hub**: https://hub.docker.com/r/jackipro1509/ocr-service
- **Source Code**: Available in this repository
- **API Documentation**: http://localhost:5000 (when running)

## 📝 Notes

- First run may take additional time as PaddleOCR downloads language models
- The container includes both English and Vietnamese OCR models
- Automatic cleanup ensures no temporary files accumulate
- Service supports concurrent requests 