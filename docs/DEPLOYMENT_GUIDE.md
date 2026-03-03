# Deployment Guide

Complete guide for deploying PulseTasks to development, staging, and production environments.

---

## Quick Reference

| Environment | Docker | Database | Redis |
|-------------|--------|----------|-------|
| Development | `docker-compose up` | mongodb:27017 | redis:6379 |
| Production | `docker-compose -f docker-compose.prod.yml up -d` | Managed MongoDB | Managed Redis |

---

## Prerequisites

### Required Software

- **Docker** 20.10+ - Container orchestration
- **Docker Compose** 2.0+ - Multi-container management
- **Python** 3.11+ (for local development)
- **Git** - Version control

### Verify Installation

```bash
# Check Docker
docker --version
# Expected: Docker version 20.10.0 or higher

# Check Docker Compose
docker compose version
# Expected: Docker Compose version v2.0.0 or higher

# Check Python
python --version
# Expected: Python 3.11.x or higher
```

---

## Docker Setup

### Development Deployment

**Step 1: Create Environment File**

Create `.env` in project root:

```env
# Application
APP_NAME=pulsetasks
APP_ENV=development
FRONTEND_URL=http://localhost:3000

# Database
MONGODB_URL=mongodb://admin:password@localhost:27017/pulsetasks?authSource=admin
DATABASE_NAME=pulsetasks

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI (Optional - for AI features)
OPENAI_API_KEY=sk-proj-your-api-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Step 2: Start Infrastructure**

```bash
# Start MongoDB and Redis
docker compose up mongodb redis -d

# Verify services are running
docker ps
# Expected: mongodb and redis containers running

# Check logs
docker compose logs mongodb
docker compose logs redis
```

**Step 3: Start Backend**

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 4: Verify Deployment**

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "pulsetasks-backend",
#   "socketio": "running"
# }

# Access API docs
open http://localhost:8000/docs
```

---

## Production Deployment

### Option 1: Docker Compose (Simple)

**Create `docker-compose.prod.yml`:**

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - MONGODB_URL=${MONGODB_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - mongodb
      - redis
    restart: unless-stopped

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_USER}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
      - MONGO_INITDB_DATABASE=${DATABASE_NAME}
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  mongodb_data:
  redis_data:
```

**Create `.env.production`:**

```env
APP_ENV=production
FRONTEND_URL=https://yourdomain.com
MONGODB_URL=mongodb://admin:strong-password@localhost:27017/pulsetasks?authSource=admin
MONGO_USER=admin
MONGO_PASSWORD=strong-password-32-chars-min
DATABASE_NAME=pulsetasks
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=very-long-random-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
OPENAI_API_KEY=sk-proj-your-production-key
ALLOWED_ORIGINS=https://yourdomain.com
```

**Deploy:**

```bash
# Build and start production containers
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Verify deployment
docker compose -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

### Option 2: Cloud Deployment (AWS/DigitalOcean/GCP)

**Step 1: Prepare Database**

```bash
# Use managed MongoDB (e.g., MongoDB Atlas, AWS DocumentDB)
# Get connection string from cloud provider

# Example connection string:
# mongodb+srv://admin:password@cluster0.mongodb.net/pulsetasks?retryWrites=true&w=majority
```

**Step 2: Prepare Redis**

```bash
# Use managed Redis (e.g., AWS ElastiCache, Redis Cloud)
# Get connection URL from cloud provider

# Example connection string:
# redis://cluster-endpoint:6379/0
```

**Step 3: Deploy Backend**

```bash
# Build Docker image
docker build -t pulsetasks-backend:latest ./backend

# Tag for cloud registry
docker tag pulsetasks-backend:latest your-registry/pulsetasks-backend:latest

# Push to registry
docker push your-registry/pulsetasks-backend:latest

# Deploy to cloud (example with AWS ECS)
# Use cloud provider's CLI or web console to deploy
```

**Step 4: Configure Environment Variables**

Set these in your cloud provider's environment configuration:

```env
APP_ENV=production
FRONTEND_URL=https://yourdomain.com
MONGODB_URL=mongodb+srv://admin:password@cluster0.mongodb.net/pulsetasks
REDIS_URL=redis://cluster-endpoint:6379/0
JWT_SECRET_KEY=your-production-secret-key-32-chars-min
OPENAI_API_KEY=sk-proj-your-production-key
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `APP_ENV` | Environment (development/production) | `production` | ✅ Yes |
| `FRONTEND_URL` | Frontend URL for CORS | `https://app.example.com` | ✅ Yes |
| `MONGODB_URL` | MongoDB connection string | `mongodb://...` | ✅ Yes |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | ✅ Yes |
| `JWT_SECRET_KEY` | JWT signing secret | `random-32-char-string` | ✅ Yes |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_NAME` | MongoDB database name | `pulsetasks` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `OPENAI_API_KEY` | OpenAI API key | `null` |

### Development vs Production

**Development:**
```env
APP_ENV=development
FRONTEND_URL=http://localhost:3000
MONGODB_URL=mongodb://admin:password@localhost:27017/pulsetasks
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev-secret-key
```

**Production:**
```env
APP_ENV=production
FRONTEND_URL=https://app.example.com
MONGODB_URL=mongodb+srv://admin:strong-password@cluster.mongodb.net/pulsetasks
REDIS_URL=redis://prod-cluster:6379/0
JWT_SECRET_KEY=very-long-random-secret-key-minimum-32-characters
```

---

## Database Migrations

### MongoDB Setup

**Initial Database Setup:**

```bash
# Connect to MongoDB
docker exec -it pulsetask-mongodb-1 mongosh -u admin -p password

# Switch to database
use pulsetasks

# Create collections (optional - MongoDB creates automatically)
db.createCollection("users")
db.createCollection("tasks")
db.createCollection("ydocs")
db.createCollection("workspaces")
db.createCollection("refresh_tokens")

# Create indexes for performance
db.users.createIndex({ "email": 1 }, { unique: true })
db.tasks.createIndex({ "list_id": 1 })
db.tasks.createIndex({ "assignee_id": 1 })
db.tasks.createIndex({ "status": 1 })
db.tasks.createIndex({ "due_date": 1 })
db.ydocs.createIndex({ "list_id": 1 }, { unique: true })
db.refresh_tokens.createIndex({ "token": 1 }, { unique: true })
db.refresh_tokens.createIndex({ "user_id": 1 })
```

**Backup Database:**

```bash
# Backup MongoDB
docker exec pulsetask-mongodb-1 mongodump \
  --username=admin \
  --password=password \
  --db=pulsetasks \
  --archive=/backup/pulsetasks-backup-$(date +%Y%m%d).gz

# Copy backup from container
docker cp pulsetask-mongodb-1:/backup/pulsetasks-backup-$(date +%Y%m%d).gz ./backup/
```

**Restore Database:**

```bash
# Copy backup to container
docker cp ./backup/pulsetasks-backup-20260303.gz pulsetask-mongodb-1:/tmp/backup.gz

# Restore MongoDB
docker exec -it pulsetask-mongodb-1 mongorestore \
  --username=admin \
  --password=password \
  --db=pulsetasks \
  --archive=/tmp/backup.gz
```

---

## Production Deployment Steps

### Pre-Deployment Checklist

- [ ] All tests passing (`pytest --cov`)
- [ ] Code reviewed and merged
- [ ] Environment variables configured
- [ ] Database backup created
- [ ] SSL/TLS certificates configured
- [ ] Monitoring/alerting setup
- [ ] DNS configured

### Deployment Process

**Step 1: Backup Current State**

```bash
# Backup database
./scripts/backup-database.sh

# Tag current version
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

**Step 2: Deploy New Version**

```bash
# Pull latest code
git pull origin main

# Build new Docker image
docker compose -f docker-compose.prod.yml build

# Stop old containers
docker compose -f docker-compose.prod.yml down

# Start new containers
docker compose -f docker-compose.prod.yml up -d
```

**Step 3: Verify Deployment**

```bash
# Check container status
docker compose -f docker-compose.prod.yml ps

# Health check
curl https://api.yourdomain.com/health

# Check logs
docker compose -f docker-compose.prod.yml logs -f backend

# Test key endpoints
curl https://api.yourdomain.com/api/v1/auth/login
```

**Step 4: Monitor Rollout**

```bash
# Monitor for errors
docker compose -f docker-compose.prod.yml logs backend | grep -i error

# Check database connections
docker compose -f docker-compose.prod.yml logs backend | grep -i mongodb

# Monitor API response times
curl -w "@curl-format.txt" https://api.yourdomain.com/health
```

---

## Rollback Procedures

### Immediate Rollback

**Scenario: Deployment caused critical issues**

```bash
# Step 1: Stop current deployment
docker compose -f docker-compose.prod.yml down

# Step 2: Restore previous Docker image
docker tag pulsetasks-backend:previous pulsetasks-backend:latest

# Step 3: Start previous version
docker compose -f docker-compose.prod.yml up -d

# Step 4: Verify
curl https://api.yourdomain.com/health
```

### Database Rollback

**Scenario: Database migration caused issues**

```bash
# Step 1: Stop application
docker compose -f docker-compose.prod.yml stop backend

# Step 2: Restore database from backup
docker cp ./backup/pulsetasks-backup-pre-deployment.gz \
  pulsetask-mongodb-1:/tmp/restore.gz

docker exec -it pulsetask-mongodb-1 mongorestore \
  --username=admin \
  --password=production-password \
  --db=pulsetasks \
  --archive=/tmp/restore.gz --drop

# Step 3: Start application
docker compose -f docker-compose.prod.yml start backend

# Step 4: Verify
curl https://api.yourdomain.com/health
```

### Zero-Downtime Rolling Updates

**Using multiple containers:**

```yaml
# docker-compose.prod.yml with multiple replicas
services:
  backend:
    image: pulsetasks-backend:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
```

**Rolling update:**

```bash
# Update one replica at a time
docker compose -f docker-compose.prod.yml up -d --scale backend=3

# Wait for health check before updating next replica
docker compose -f docker-compose.prod.yml exec backend \
  python -c "import requests; requests.get('http://localhost:8000/health')"
```

---

## Monitoring and Maintenance

### Health Checks

```bash
# API health
curl https://api.yourdomain.com/health

# Socket.IO health
curl https://api.yourdomain.com/health/socket

# AI service health
curl https://api.yourdomain.com/ai/health
```

### Log Management

```bash
# View real-time logs
docker compose -f docker-compose.prod.yml logs -f backend

# View last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 backend

# Filter errors
docker compose -f docker-compose.prod.yml logs backend | grep ERROR
```

### Performance Monitoring

**Check resource usage:**

```bash
# Container resource usage
docker stats

# MongoDB performance
docker exec -it pulsetask-mongodb-1 mongosh --eval "db.serverStatus()"

# Redis performance
docker exec -it pulsetask-redis-1 redis-cli INFO stats
```

---

## Security Considerations

### Production Security Checklist

- [ ] Change default passwords
- [ ] Use strong `JWT_SECRET_KEY` (minimum 32 characters)
- [ ] Enable SSL/TLS for all connections
- [ ] Restrict MongoDB/Redis to private network
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates

### SSL/TLS Setup

**Using reverse proxy (Nginx):**

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## Troubleshooting Deployment Issues

### Container Won't Start

```bash
# Check container logs
docker compose logs backend

# Common issues:
# - Port already in use (change port mapping)
# - Environment variable missing (check .env file)
# - Database connection failed (check MONGODB_URL)
```

### Database Connection Failed

```bash
# Test MongoDB connection
docker exec -it pulsetask-mongodb-1 mongosh \
  -u admin -p password --eval "db.adminCommand('ping')"

# Check network
docker network inspect pulsetask_default
```

### Redis Connection Failed

```bash
# Test Redis connection
docker exec -it pulsetask-redis-1 redis-cli ping

# Expected response: PONG
```

---

## Support

**Documentation:** `/docs` (API documentation)

**Issues:** Report deployment issues with:
1. Error messages from logs
2. Environment configuration (with secrets removed)
3. Docker version and OS
4. Steps to reproduce

---

**Last Updated:** 2026-03-03
**Version:** 1.0.0
