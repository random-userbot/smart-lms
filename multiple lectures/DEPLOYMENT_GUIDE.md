# Deployment Configuration Guide

## Production Deployment Checklist

### 1. Security Configuration

#### Change Default Passwords
```python
# In scripts/init_storage.py or via admin panel
# Change these default credentials:
admin: admin123 → [strong password]
teachers: teacher123 → [strong password]
students: student123 → [strong password]
```

#### Environment Variables
Create `.env` file (do NOT commit to git):
```bash
# Database
DB_TYPE=postgresql  # or mongodb, mysql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_lms
DB_USER=your_db_user
DB_PASSWORD=your_secure_db_password

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key

# Storage
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE=104857600  # 100MB
ALLOWED_EXTENSIONS=mp4,pdf,docx,pptx

# AI Services
OPENAI_API_KEY=your-openai-key  # Optional for GPT features
HUGGINGFACE_TOKEN=your-hf-token  # Optional

# Email (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password

# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

#### Update config.yaml
```yaml
# Production settings
app:
  environment: production
  debug: false
  host: "0.0.0.0"
  port: 8501
  
security:
  password_min_length: 12
  password_require_uppercase: true
  password_require_numbers: true
  password_require_special: true
  session_timeout_minutes: 30
  max_login_attempts: 5
  lockout_duration_minutes: 15
  
storage:
  backend: "database"  # Change from "json"
  connection_pool_size: 20
  backup_enabled: true
  backup_frequency_hours: 24
  
rate_limiting:
  enabled: true
  requests_per_minute: 60
  burst: 10
```

### 2. Database Migration

#### PostgreSQL Setup
```sql
-- Create database
CREATE DATABASE smart_lms;

-- Create user
CREATE USER lms_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE smart_lms TO lms_user;

-- Run migrations (implement in scripts/migrate_to_db.py)
```

#### MongoDB Setup
```bash
# Install MongoDB
# Create database and collections
mongosh
use smart_lms
db.createUser({
  user: "lms_user",
  pwd: "secure_password",
  roles: ["readWrite"]
})
```

#### Migration Script
```bash
# Migrate from JSON to Database
python scripts/migrate_to_db.py --source=json --target=postgresql
```

### 3. Server Deployment

#### Option A: Docker Deployment

**Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create storage directory
RUN mkdir -p storage

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=smart_lms
      - DB_USER=postgres
      - DB_PASSWORD=secure_password
    volumes:
      - ./storage:/app/storage
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=smart_lms
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  pgdata:
```

**Deploy Commands**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop
docker-compose down
```

#### Option B: Cloud Deployment (AWS/Azure/GCP)

**AWS EC2 + RDS**
```bash
# 1. Launch EC2 instance (t3.medium or larger)
# 2. Create RDS PostgreSQL instance
# 3. Configure security groups
# 4. SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# 5. Clone repository
git clone your-repo
cd smart-lms

# 6. Install dependencies
sudo apt update
sudo apt install python3-pip nginx
pip3 install -r requirements.txt

# 7. Configure environment
cp .env.example .env
nano .env  # Edit with your values

# 8. Setup systemd service
sudo nano /etc/systemd/system/smart-lms.service
```

**smart-lms.service**
```ini
[Unit]
Description=Smart LMS Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/smart-lms
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/home/ubuntu/.local/bin/streamlit run app/streamlit_app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable smart-lms
sudo systemctl start smart-lms
sudo systemctl status smart-lms
```

### 4. SSL/HTTPS Configuration

**Using Let's Encrypt (Certbot)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
```

**nginx.conf**
```nginx
upstream streamlit {
    server localhost:8501;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://streamlit;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }

    # File upload size
    client_max_body_size 100M;
}
```

### 5. Monitoring & Logging

**Setup Logging**
```python
# In app/streamlit_app.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

**Monitoring Tools**
- **Application Monitoring**: New Relic, DataDog, or Prometheus
- **Server Monitoring**: CloudWatch (AWS), Azure Monitor, or Grafana
- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Error Tracking**: Sentry

### 6. Backup Strategy

**Automated Backups**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
pg_dump -U lms_user smart_lms > "$BACKUP_DIR/db_$DATE.sql"

# Storage backup
tar -czf "$BACKUP_DIR/storage_$DATE.tar.gz" ./storage

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

**Crontab Setup**
```bash
# Run backup daily at 2 AM
crontab -e
0 2 * * * /path/to/backup.sh
```

### 7. Performance Optimization

**Enable Caching**
```python
# In app/streamlit_app.py
import streamlit as st

@st.cache_data(ttl=3600)
def load_courses():
    return storage.get_all_courses()

@st.cache_resource
def load_model():
    return load_ml_model()
```

**Database Indexing**
```sql
-- Create indexes for common queries
CREATE INDEX idx_user_id ON engagement_logs(user_id);
CREATE INDEX idx_course_id ON lectures(course_id);
CREATE INDEX idx_timestamp ON engagement_logs(timestamp);
```

**CDN for Static Files**
- Use CloudFront (AWS) or Azure CDN for video files
- Reduce server load and improve load times

### 8. Security Hardening

**Firewall Rules**
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

**Regular Updates**
```bash
# Auto-update security patches
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

**Security Headers**
```nginx
# Add to nginx.conf
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

### 9. Testing Before Deployment

```bash
# Run all tests
python -m pytest tests/

# Load testing
pip install locust
locust -f tests/load_test.py

# Security scan
pip install safety bandit
safety check
bandit -r app/ services/
```

### 10. Go-Live Checklist

- [ ] All default passwords changed
- [ ] Environment variables configured
- [ ] Database migrated and tested
- [ ] SSL certificate installed
- [ ] Backups configured and tested
- [ ] Monitoring tools set up
- [ ] Firewall rules configured
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Admin panel tested
- [ ] User acceptance testing completed

## Quick Deploy Commands

### Development
```bash
python scripts/init_storage.py
streamlit run app/streamlit_app.py
```

### Production
```bash
# Docker
docker-compose up -d

# Manual
sudo systemctl start smart-lms
sudo systemctl enable nginx
```

## Support & Maintenance

### Regular Maintenance Tasks
- Weekly: Review logs and error reports
- Monthly: Database optimization and cleanup
- Quarterly: Security updates and patches
- Yearly: SSL certificate renewal (automatic with Let's Encrypt)

### Troubleshooting
```bash
# Check application logs
tail -f logs/app.log

# Check system logs
sudo journalctl -u smart-lms -f

# Database connection test
psql -h localhost -U lms_user -d smart_lms

# Restart service
sudo systemctl restart smart-lms
```
