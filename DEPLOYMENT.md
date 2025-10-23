# NRRC Arabic POV - Deployment Guide

## Docker Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- At least 2GB disk space

### Quick Start with Docker

1. **Clone and prepare the repository:**
```bash
git clone <repository-url>
cd nrrc_arabic_pov_windows
```

2. **Add your PDF documents:**
```bash
# Place your Arabic PDFs in the data/raw_pdfs directory
mkdir -p data/raw_pdfs
cp your_documents.pdf data/raw_pdfs/
```

3. **Build and run with Docker Compose:**
```bash
# Build the Docker image
docker-compose build

# Run the application
docker-compose up -d

# Check logs
docker-compose logs -f
```

4. **Access the application:**
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Manual Docker Commands

```bash
# Build the image
docker build -t nrrc-arabic-pov .

# Run the container
docker run -d \
  --name nrrc-arabic-pov \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/conf:/app/conf \
  nrrc-arabic-pov

# Check container status
docker ps

# View logs
docker logs nrrc-arabic-pov

# Stop the container
docker stop nrrc-arabic-pov

# Remove the container
docker rm nrrc-arabic-pov
```

### Data Persistence

The Docker setup uses volume mounts to persist:
- `./data` - Document indices and processed data
- `./conf` - Configuration files

### Environment Variables

You can customize the deployment using environment variables:

```bash
# In docker-compose.yml or docker run command
environment:
  - PYTHONIOENCODING=utf-8
  - TRANSFORMERS_CACHE=/app/.cache/transformers
  - LOG_LEVEL=INFO
```

### Health Monitoring

The application includes a health check endpoint:
- **Endpoint**: `/health`
- **Response**: JSON with status and message
- **Docker Health Check**: Configured in Dockerfile

### Scaling

For production deployment with multiple instances:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nrrc-arabic-pov:
    build: .
    ports:
      - "8000-8002:8000"
    volumes:
      - ./data:/app/data
      - ./conf:/app/conf
    deploy:
      replicas: 3
    restart: unless-stopped
```

### Troubleshooting

1. **Container won't start:**
```bash
# Check logs
docker logs nrrc-arabic-pov

# Check if ports are available
netstat -tulpn | grep 8000
```

2. **Out of memory:**
```bash
# Increase Docker memory limit
docker run -m 4g nrrc-arabic-pov
```

3. **Model download issues:**
```bash
# Pre-download models
docker run --rm -v $(pwd)/.cache:/app/.cache nrrc-arabic-pov python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base')"
```

### Production Considerations

1. **Security:**
   - Change default passwords
   - Use HTTPS with reverse proxy
   - Set strong JWT secret
   - Enable firewall rules

2. **Performance:**
   - Use SSD storage for indices
   - Allocate sufficient RAM (4GB+)
   - Consider GPU acceleration for large deployments

3. **Monitoring:**
   - Set up log aggregation
   - Monitor memory usage
   - Track API response times
   - Set up alerts for health check failures

### Backup and Recovery

```bash
# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/ conf/

# Restore data
tar -xzf backup-20250123.tar.gz
```

## Native Installation

For development or non-Docker environments, see the main README.md for detailed setup instructions.
