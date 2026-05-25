# Getting Started with Vehicle Rental SaaS

## Prerequisites

Before you begin, ensure you have installed:

- **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Git** - [Install Git](https://git-scm.com/)
- **Node.js 18+** (optional, for local frontend development) - [Install Node.js](https://nodejs.org/)
- **Python 3.11+** (optional, for local backend development) - [Install Python](https://www.python.org/)

## Quick Start (Docker)

The easiest way to run the entire platform is with Docker Compose.

### Step 1: Clone the Repository

```bash
git clone https://github.com/quinnne-tech/vehicle-rental-saas.git
cd vehicle-rental-saas
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

The `.env` file contains default development values. For production, update these values:

```bash
# .env
FASTAPI_ENV=development          # Change to 'production'
JWT_SECRET_KEY=your-secret-key   # Change this!
MONGODB_PASSWORD=password123     # Change this!
SMTP_USER=your-email@gmail.com   # Your email
SMTP_PASSWORD=your-app-password  # Your email app password
```

### Step 3: Start All Services

```bash
docker-compose up --build
```

This starts:
- ✅ MongoDB (Database)
- ✅ Redis (Cache & Sessions)
- ✅ FastAPI Backend (API Server)
- ✅ Celery Worker (Background Jobs)
- ✅ Celery Beat (Job Scheduler)
- ✅ React Frontend (Web UI)
- ✅ Nginx (Reverse Proxy)

**Wait 30-60 seconds for services to fully initialize.**

### Step 4: Access the Platform

| Service | URL | Purpose |
|---------|-----|----------|
| Frontend | http://localhost:3000 | Web Application |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger Documentation |
| Admin Panel | http://localhost:3000/admin | Super Admin Dashboard |

### Step 5: Seed Demo Data

In a new terminal:

```bash
docker-compose exec backend python scripts/seed_db.py
```

This creates demo tenants, users, vehicles, and rentals.

### Demo Credentials

After seeding, use these to login:

**Tenant 1 - Fast Rentals Co**
- Email: `company@example.com`
- Password: `Company@123456`
- Plan: Starter (5 vehicles, 2 users)

**Tenant 2 - Premium Vehicle Rentals**
- Email: `admin@premium.com`
- Password: `Admin@123456`
- Plan: Growth (25 vehicles, 5 users)

## Local Development

### Backend Development

If you want to run the backend locally (not in Docker):

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

### Frontend Development

If you want to run the frontend locally:

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start
```

App will be available at `http://localhost:3000`

## Common Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v

# Rebuild specific service
docker-compose build backend

# Execute command in container
docker-compose exec backend python -c "import app"

# View database
docker exec -it vehicle_rental_mongodb mongosh
```

## API Testing

### Using Swagger UI (Interactive)

Go to http://localhost:8000/docs - Full interactive API documentation

### Using cURL

```bash
# Register a company
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "My Rental Company",
    "email": "mycompany@example.com",
    "password": "SecurePassword123",
    "owner_name": "John Doe"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "company@example.com",
    "password": "Company@123456"
  }'

# Get dashboard (add your access token)
curl -X GET "http://localhost:8000/api/tenant/dashboard" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Access

### MongoDB Connection

```bash
# Connect to MongoDB shell
docker exec -it vehicle_rental_mongodb mongosh

# Inside mongosh
use vehicle_rental_saas
db.tenants.find()
db.users.find()
db.vehicles.find()
```

### MongoDB Connection String

```
mongodb://admin:password123@localhost:27017/vehicle_rental_saas?authSource=admin
```

Use with MongoDB Compass or other tools.

## Troubleshooting

### Ports Already in Use

If ports 3000, 8000, 27017, 6379 are already in use:

```bash
# Edit docker-compose.yml and change port mappings
# Example: Change 3000:3000 to 3001:3000
```

### MongoDB Connection Failed

```bash
# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Services Won't Start

```bash
# Clean up and rebuild
docker-compose down -v
docker-compose up --build
```

### Permission Denied Errors

On Linux/Mac, you may need to use `sudo`:

```bash
sudo docker-compose up --build
```

## Next Steps

1. **Customize Branding** - Update logo and colors in settings
2. **Configure Email** - Set SMTP credentials for notifications
3. **Setup Payment Gateway** - Integrate Stripe, Midtrans, or Xendit
4. **Deploy to Production** - See [DEPLOYMENT.md](./DEPLOYMENT.md)
5. **Add Users** - Create manager and staff accounts for your team
6. **Configure Vehicles** - Add your vehicle inventory
7. **Monitor Performance** - Check logs and metrics

## Getting Help

- 📚 **API Documentation** - http://localhost:8000/docs
- 🐛 **Report Issues** - GitHub Issues
- 💬 **Discussions** - GitHub Discussions
- 📧 **Email Support** - support@vehiclerental-saas.com

## Security Notes

⚠️ **IMPORTANT FOR PRODUCTION:**

1. **Change all default passwords** in `.env`
2. **Set strong JWT_SECRET_KEY** (minimum 32 characters)
3. **Enable HTTPS** - Use Let's Encrypt in production
4. **Configure CORS** - Restrict to your domain
5. **Enable database backups** - Protect your data
6. **Set up SSL certificates** - Use Nginx with SSL
7. **Use environment secrets** - Never commit `.env` to git

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production security checklist.
