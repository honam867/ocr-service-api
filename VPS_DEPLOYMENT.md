# VPS Deployment Guide for OCR Service

## 🌐 Production Deployment on VPS

This guide explains how to deploy your OCR service on a Virtual Private Server (VPS) for production use.

## 📋 VPS Requirements

### Minimum Server Specifications
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 10GB free space minimum
- **CPU**: 2 cores minimum
- **OS**: Ubuntu 20.04/22.04, CentOS 7/8, or similar Linux distribution
- **Network**: Public IP address

### Why These Requirements?
- **RAM**: OCR processing and PaddleOCR models need significant memory
- **Storage**: Docker image is ~2.6GB + model downloads + temporary files
- **CPU**: OCR processing is CPU-intensive

## 🛠️ VPS Setup Steps

### 1. Initial Server Setup

#### Connect to Your VPS
```bash
# SSH into your VPS (replace with your server IP)
ssh root@YOUR_VPS_IP
# or if you have a user account:
ssh username@YOUR_VPS_IP
```

#### Update System
```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git htop nano
```

### 2. Install Docker on VPS

#### For Ubuntu/Debian:
```bash
# Remove old Docker versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install Docker dependencies
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

#### For CentOS/RHEL:
```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 4. Deploy Your OCR Service

#### Create Project Directory
```bash
# Create project directory
mkdir -p /opt/ocr-service
cd /opt/ocr-service

# Create uploads directory
mkdir -p uploads
```

#### Create Production Docker Compose File
```bash
# Create docker-compose.yml for production
nano docker-compose.yml
```

Add this content (optimized for VPS):
```yaml
version: '3.8'

services:
  ocr-service:
    image: jackipro1509/ocr-service:latest
    container_name: ocr-service
    ports:
      - "80:5000"  # Use port 80 for web access
    volumes:
      - ./uploads:/temp_uploads
      - ./logs:/var/log/ocr  # Log persistence
    environment:
      - TZ=UTC  # Or your preferred timezone
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5000/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s  # Longer startup time for VPS
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Deploy the Service
```bash
# Pull and start the service
docker-compose up -d

# Check if it's running
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔒 Security Configuration

### 1. Firewall Setup
```bash
# Install UFW (Ubuntu Firewall)
sudo apt install -y ufw

# Allow SSH (important!)
sudo ufw allow ssh
sudo ufw allow 22

# Allow HTTP traffic
sudo ufw allow 80
sudo ufw allow 443  # For HTTPS later

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 2. Reverse Proxy with Nginx (Recommended)

#### Install Nginx
```bash
sudo apt install -y nginx
```

#### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/ocr-service
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;
    
    client_max_body_size 20M;  # Allow larger file uploads
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for OCR processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

#### Enable the Site
```bash
# Enable the configuration
sudo ln -s /etc/nginx/sites-available/ocr-service /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

#### Update Docker Compose for Nginx
```yaml
# Change port mapping in docker-compose.yml
ports:
  - "5000:5000"  # Internal only, not exposed publicly
```

### 3. SSL Certificate (HTTPS) - Optional but Recommended

#### Using Let's Encrypt (Free SSL)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace YOUR_DOMAIN)
sudo certbot --nginx -d YOUR_DOMAIN

# Auto-renewal
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Maintenance

### 1. System Monitoring
```bash
# Check system resources
htop

# Check Docker containers
docker ps

# Check service logs
docker-compose logs -f ocr-service

# Check disk usage
df -h

# Check memory usage
free -h
```

### 2. Log Management
```bash
# View service logs
sudo journalctl -u docker -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 3. Automatic Updates
```bash
# Create update script
nano /opt/ocr-service/update.sh
```

Add this content:
```bash
#!/bin/bash
cd /opt/ocr-service

echo "Updating OCR Service..."
docker-compose pull
docker-compose up -d

echo "Cleaning up old images..."
docker image prune -f

echo "Update completed!"
```

Make it executable:
```bash
chmod +x /opt/ocr-service/update.sh

# Schedule weekly updates (optional)
sudo crontab -e
# Add: 0 2 * * 0 /opt/ocr-service/update.sh
```

## 🌍 Access Your Service

### Public Access
- **HTTP**: `http://YOUR_VPS_IP/` or `http://YOUR_DOMAIN/`
- **HTTPS**: `https://YOUR_DOMAIN/` (if SSL configured)

### Test the Service
```bash
# Health check
curl http://YOUR_VPS_IP/

# Test OCR (from your local machine)
curl -X POST \
  -F "file=@test.pdf" \
  -F "language=en" \
  http://YOUR_VPS_IP/extract-text
```

## 🛠️ Troubleshooting VPS Issues

### Service Won't Start
```bash
# Check Docker logs
docker-compose logs ocr-service

# Check system resources
free -h
df -h

# Restart the service
docker-compose restart
```

### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart with memory limit
# Add to docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 3G
```

### Network Issues
```bash
# Check if port is open
netstat -tulpn | grep :80

# Check firewall
sudo ufw status

# Test internal connection
curl http://localhost:5000/
```

## 📱 Production Best Practices

1. **Regular Backups**: Backup your uploads directory
2. **Monitoring**: Set up system monitoring (optional: use tools like Grafana)
3. **Log Rotation**: Configure log rotation to prevent disk space issues
4. **Security Updates**: Keep your VPS and Docker updated
5. **Domain Name**: Use a proper domain instead of IP address
6. **Load Balancing**: For high traffic, consider multiple instances

## 🔄 Scaling for High Traffic

### Multiple Instances
```yaml
# In docker-compose.yml
services:
  ocr-service:
    # ... existing configuration
    deploy:
      replicas: 3  # Run 3 instances
```

### Load Balancer Configuration
```nginx
# In Nginx configuration
upstream ocr_backend {
    server localhost:5000;
    server localhost:5001;
    server localhost:5002;
}

server {
    # ... existing configuration
    location / {
        proxy_pass http://ocr_backend;
        # ... existing proxy settings
    }
}
```

## 📞 Support

Your OCR service is now running on a production VPS and accessible from anywhere on the internet! 🎉

For issues:
1. Check the logs: `docker-compose logs -f`
2. Verify system resources: `htop` and `df -h`
3. Test connectivity: `curl http://localhost:5000/` 