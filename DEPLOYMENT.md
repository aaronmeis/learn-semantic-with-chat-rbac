# Deployment Guide

## Overview

This guide covers deployment options for the Semantic Data Chatbot multi-agent system.

## Prerequisites

- Python 3.10+
- OpenAI API key (or other LLM provider)
- 2GB+ RAM
- 10GB+ disk space (for vector database)

## Local Deployment

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### Step 3: Initialize System

```bash
python -m src.setup
```

This will:
- Create necessary directories
- Initialize RBAC database
- Create default users
- Initialize semantic store

### Step 4: Start API Server

```bash
python -m src.api
# or
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./databases:/app/databases
      - ./logs:/app/logs
    restart: unless-stopped
```

### Build and Run

```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

1. **EC2 Instance**:
   - Use Ubuntu 22.04 LTS
   - t3.medium or larger
   - Install Python 3.10+
   - Follow local deployment steps

2. **Elastic Beanstalk**:
   - Create Python application
   - Upload application code
   - Configure environment variables
   - Deploy

3. **ECS/Fargate**:
   - Use Docker image
   - Configure task definition
   - Set up load balancer
   - Configure auto-scaling

### Google Cloud Deployment

1. **Cloud Run**:
   ```bash
   gcloud run deploy chatbot \
     --source . \
     --platform managed \
     --region us-central1 \
     --set-env-vars OPENAI_API_KEY=your_key
   ```

2. **Compute Engine**:
   - Create VM instance
   - Install dependencies
   - Follow local deployment steps

### Azure Deployment

1. **App Service**:
   - Create Web App
   - Configure Python runtime
   - Set environment variables
   - Deploy via Git or ZIP

2. **Container Instances**:
   - Build Docker image
   - Push to Azure Container Registry
   - Deploy container instance

## Production Considerations

### Security

1. **API Keys**: Store in environment variables or secret management service
2. **HTTPS**: Use reverse proxy (nginx) with SSL certificates
3. **Authentication**: Implement proper authentication (JWT, OAuth)
4. **Rate Limiting**: Implement rate limiting per user/role
5. **Input Validation**: Validate all inputs at API level

### Performance

1. **Caching**: Implement Redis for caching frequent queries
2. **Load Balancing**: Use load balancer for multiple instances
3. **Database**: Use PostgreSQL instead of SQLite for production
4. **Vector DB**: Consider Pinecone or Weaviate for cloud vector storage
5. **Monitoring**: Set up APM (Application Performance Monitoring)

### Scaling

1. **Horizontal Scaling**: Run multiple API instances behind load balancer
2. **Database Scaling**: Use managed database service
3. **Vector DB Scaling**: Use managed vector database service
4. **Caching**: Use distributed cache (Redis Cluster)

### Monitoring

1. **Logging**: Centralized logging (ELK, CloudWatch, etc.)
2. **Metrics**: Prometheus + Grafana
3. **Alerts**: Set up alerts for errors and performance issues
4. **Health Checks**: Implement health check endpoints

### Example Nginx Configuration

```nginx
upstream chatbot {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://chatbot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key

Optional:
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `LLM_MODEL`: LLM model (default: gpt-4)
- `RBAC_DB_PATH`: RBAC database path
- `QUALITY_DB_PATH`: Quality metrics database path
- `LOG_LEVEL`: Logging level (default: INFO)

## Health Checks

The API includes a status endpoint:

```bash
curl http://localhost:8000/status
```

## Backup and Recovery

1. **Database Backups**: Regularly backup SQLite databases
2. **Vector Store**: Backup ChromaDB persistence directory
3. **Configuration**: Version control all configuration files
4. **Recovery Plan**: Document recovery procedures

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Locked**: Check for concurrent access issues
3. **API Key Invalid**: Verify OPENAI_API_KEY is set correctly
4. **Port Already in Use**: Change API_PORT or stop conflicting service
5. **Permission Denied**: Check RBAC configuration and user roles

### Logs

Check logs in:
- `logs/chatbot.log` (if configured)
- Application stdout/stderr
- System logs (journalctl on Linux)

## Support

For issues and questions:
- Check README.md for usage examples
- Review ARCHITECTURE.md for system design
- Check logs for error details
