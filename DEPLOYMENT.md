# Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] Database backups scheduled
- [ ] SSL certificates generated
- [ ] Domain name registered
- [ ] Email SMTP configured
- [ ] Payment gateway keys set up
- [ ] Monitoring & logging configured
- [ ] Database indexes created
- [ ] Security headers configured

## Environment Setup

### 1. Production Environment File

Create `.env.production`:

```bash
# FastAPI
FASTAPI_ENV=production
DEBUG=False
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# MongoDB - Use managed service (MongoDB Atlas, AWS DocumentDB, etc.)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/vehicle_rental_saas?retryWrites=true&w=majority

# Redis - Use managed service (AWS ElastiCache, etc.)
REDIS_URL=redis://username:password@redis-server:6379/0
CELERY_BROKER_URL=redis://username:password@redis-server:6379/1
CELERY_RESULT_BACKEND=redis://username:password@redis-server:6379/2

# JWT
JWT_SECRET_KEY=generate-random-string-min-32-chars-here
JWT_ALGORITHM=HS256

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Vehicle Rental

# Stripe
STRIPE_API_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Frontend
FRONTEND_URL=https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

### 2. Generate Strong Secrets

```bash
# Generate JWT secret (32+ characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate random password
openssl rand -base64 32
```

## Deployment Options

### Option 1: Docker on VPS (Recommended for Starting)

#### Prerequisites
- VPS (AWS EC2, DigitalOcean, Linode, etc.)
- Ubuntu 20.04+ or similar
- Domain name
- SSH access

#### Steps

```bash
# 1. Connect to VPS
ssh root@your-vps-ip

# 2. Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Clone repository
git clone https://github.com/quinnne-tech/vehicle-rental-saas.git
cd vehicle-rental-saas

# 4. Create production environment
cp .env.example .env.production
# Edit with production values
nano .env.production

# 5. Configure Nginx with SSL
# Create nginx-ssl.conf with SSL certificates

# 6. Start services
docker-compose -f docker-compose.prod.yml up -d

# 7. View logs
docker-compose logs -f
```

#### production docker-compose.yml

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - mongodb_data:/data/db
      - ./backups:/backups
    ports:
      - "27017:27017"

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    restart: always
    env_file: .env.production
    expose:
      - "8000"
    depends_on:
      - mongodb
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery_worker:
    build: ./backend
    restart: always
    env_file: .env.production
    command: celery -A app.workers.celery_app worker --loglevel=info
    depends_on:
      - mongodb
      - redis

  celery_beat:
    build: ./backend
    restart: always
    env_file: .env.production
    command: celery -A app.workers.celery_app beat --loglevel=info
    depends_on:
      - mongodb
      - redis

  frontend:
    build: ./frontend
    restart: always
    expose:
      - "3000"

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/cert.pem:/etc/nginx/ssl/cert.pem:ro
      - ./ssl/key.pem:/etc/nginx/ssl/key.pem:ro
    depends_on:
      - backend
      - frontend

volumes:
  mongodb_data:
  redis_data:
```

### Option 2: Kubernetes (Advanced)

For large-scale deployments:

```bash
# 1. Create namespace
kubectl create namespace vehicle-rental-saas

# 2. Create secrets
kubectl create secret generic saas-secrets \
  --from-file=.env.production \
  -n vehicle-rental-saas

# 3. Deploy services
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### Option 3: Managed Services

**Recommended for maximum reliability:**

- **Database:** MongoDB Atlas, AWS DocumentDB
- **Cache:** AWS ElastiCache, Redis Cloud
- **Hosting:** AWS ECS/Fargate, Google Cloud Run, Heroku
- **CDN:** CloudFront, Cloudflare
- **Email:** SendGrid, AWS SES

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# 1. Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# 2. Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 3. Configure auto-renewal
sudo systemctl enable certbot.timer
```

### Nginx SSL Configuration

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
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
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ {
        proxy_pass http://backend/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Database Backups

### Automated MongoDB Backups

```bash
#!/bin/bash
# backup-mongodb.sh

BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec vehicle_rental_mongodb mongodump \
  --uri="mongodb://admin:password@localhost:27017/vehicle_rental_saas?authSource=admin" \
  --out=$BACKUP_DIR/backup_$DATE

# Keep only last 7 days
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR/backup_$DATE"
```

Schedule with cron:

```bash
crontab -e
# Add: 0 2 * * * /path/to/backup-mongodb.sh
```

## Monitoring & Logging

### Application Logs

```bash
# View logs
docker-compose logs -f backend

# Save logs to file
docker-compose logs > logs.txt
```

### Database Monitoring

```bash
# MongoDB monitoring
docker exec vehicle_rental_mongodb mongosh --eval "db.stats()"
```

### Performance Monitoring

Integrate with:
- **Sentry** - Error tracking
- **New Relic** - Performance monitoring
- **Datadog** - Infrastructure monitoring
- **Prometheus** - Metrics collection

## Database Indexes

Ensure these indexes exist for performance:

```bash
docker exec -it vehicle_rental_mongodb mongosh

use vehicle_rental_saas

# Tenant queries
db.users.createIndex({ "tenant_id": 1, "email": 1 })
db.vehicles.createIndex({ "tenant_id": 1, "status": 1 })
db.rentals.createIndex({ "tenant_id": 1, "vehicle_id": 1 })
db.rentals.createIndex({ "tenant_id": 1, "created_at": -1 })
db.transactions.createIndex({ "tenant_id": 1, "created_at": -1 })
```

## Scaling Considerations

### Horizontal Scaling

- **Backend:** Multiple FastAPI instances behind load balancer
- **Workers:** Multiple Celery workers for background jobs
- **Database:** MongoDB sharding on `tenant_id`
- **Cache:** Redis replication and clustering

### Database Sharding

```javascript
// Enable sharding on tenant_id
sh.enableSharding("vehicle_rental_saas")
sh.shardCollection("vehicle_rental_saas.users", { "tenant_id": 1 })
sh.shardCollection("vehicle_rental_saas.vehicles", { "tenant_id": 1 })
sh.shardCollection("vehicle_rental_saas.rentals", { "tenant_id": 1 })
```

## Security Hardening

1. **Rate Limiting** - Implement request throttling
2. **DDoS Protection** - Use Cloudflare or AWS Shield
3. **WAF** - Enable Web Application Firewall
4. **Secrets Management** - Use AWS Secrets Manager
5. **VPC Security** - Isolate database and cache
6. **IP Whitelisting** - Restrict admin access
7. **Regular Updates** - Keep dependencies updated
8. **Security Audits** - Regular penetration testing

## Rollback Procedures

```bash
# Rollback to previous version
git checkout previous-version
docker-compose build
docker-compose up -d

# Database rollback
mongorestore --uri="mongodb://..." /backups/mongodb/backup_date
```

## Troubleshooting Production

### High Memory Usage

```bash
# Check service memory
docker stats

# Increase limits in docker-compose
# services:
#   backend:
#     mem_limit: 2g
```

### Database Connection Issues

```bash
# Check MongoDB connectivity
docker-compose exec backend mongosh "mongodb://..."

# View connection pool
docker-compose logs mongodb | grep "connection"
```

### Slow Queries

```bash
# Enable MongoDB profiling
docker exec vehicle_rental_mongodb mongosh
db.setProfilingLevel(1)  # Log slow queries > 100ms
db.system.profile.find().pretty()
```

## Support

- 📚 [Docker Documentation](https://docs.docker.com/)
- 📚 [Kubernetes Documentation](https://kubernetes.io/docs/)
- 📧 Email: support@vehiclerental-saas.com
- 🐛 GitHub Issues: Report problems
