# 🚗 Multi-Tenant SaaS Vehicle Rental Management Platform

A production-grade, scalable SaaS platform for managing vehicle rental operations across multiple companies with true data isolation, subscription billing, and advanced analytics.

## 🏗️ Architecture Overview

```
Platform Architecture (Multi-Tenant)
├── Platform Owner (Super Admin)
│   ├── Tenant Management
│   ├── Billing & Subscriptions
│   ├── Global Analytics
│   └── System Configuration
│
├── Rental Company A (Tenant)
│   ├── Owner/Manager/Staff
│   ├── Vehicles
│   ├── Renters
│   ├── Rentals
│   └── Transactions
│
└── Rental Company B (Tenant)
    ├── Owner/Manager/Staff
    ├── Vehicles
    ├── Renters
    ├── Rentals
    └── Transactions
```

## 🚀 Tech Stack

**Backend:**
- FastAPI (async framework)
- MongoDB (document database)
- Motor (async MongoDB driver)
- JWT Authentication
- Redis (caching & sessions)
- Celery (background jobs)
- Pydantic (data validation)

**Frontend:**
- React 18+
- TailwindCSS (styling)
- SaaS Dashboard design (Indigo theme)
- Component-based architecture

**Infrastructure:**
- Docker & Docker Compose
- Environment-based configuration
- Production-ready deployment

## 📋 Features

### ✅ Multi-Tenant Architecture
- Complete data isolation per tenant
- Automatic tenant_id injection via middleware
- Secure cross-tenant access prevention

### ✅ User Roles & Permissions
- **Platform Level:** Super Admin
- **Tenant Level:** Owner, Manager, Staff

### ✅ Subscription Plans
- Starter (5 vehicles, 2 users)
- Growth (25 vehicles, 5 users)
- Enterprise (unlimited)
- 14-day trial period
- Expiration checking middleware

### ✅ Core Tenant Features
- 📊 Dashboard with KPIs & analytics
- 🚗 Vehicle Management (CRUD, status tracking)
- 👤 Renter Management (customer database)
- 🔄 Rental Operations (create, manage, complete)
- 💰 Cashflow System (transactions, revenue)
- 📄 Document Storage (contracts, files)
- 📈 Reporting & Analytics

### ✅ Advanced SaaS Features
- 💳 Billing integration hooks (Stripe/Midtrans/Xendit ready)
- 🎨 White-label customization (logo, color, branding)
- 📊 Usage limit engine (enforces subscription limits)
- 🔔 Multi-channel notifications (Email, WhatsApp hooks)
- 📁 Tenant-isolated file storage
- 🔐 Secure JWT with refresh tokens
- 📝 Audit logging & compliance

## 📁 Project Structure

```
vehicle-rental-saas/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Configuration & constants
│   │   │   ├── security.py        # JWT & password handling
│   │   │   └── constants.py       # App constants
│   │   ├── middleware/
│   │   │   ├── tenant.py          # Tenant extraction from JWT
│   │   │   ├── auth.py            # Authentication middleware
│   │   │   └── error_handler.py   # Global error handling
│   │   ├── models/
│   │   │   ├── schemas.py         # Pydantic request/response models
│   │   │   └── base.py            # Base model classes
│   │   ├── database/
│   │   │   ├── connection.py      # MongoDB connection
│   │   │   ├── models.py          # MongoDB document models
│   │   │   └── indexes.py         # Database indexes
│   │   ├── api/
│   │   │   ├── auth/              # Authentication endpoints
│   │   │   ├── platform/          # Super admin endpoints
│   │   │   ├── tenant/            # Tenant operations
│   │   │   ├── subscription/      # Billing endpoints
│   │   │   └── billing/           # Payment processing
│   │   ├── services/
│   │   │   ├── auth_service.py    # Auth business logic
│   │   │   ├── tenant_service.py  # Tenant management
│   │   │   ├── vehicle_service.py # Vehicle operations
│   │   │   └── subscription_service.py
│   │   ├── workers/
│   │   │   ├── celery_app.py      # Celery config
│   │   │   └── tasks.py           # Background tasks
│   │   ├── utils/
│   │   │   ├── helpers.py         # Utility functions
│   │   │   └── validators.py      # Data validation
│   │   └── main.py                # FastAPI app entry
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/            # Reusable components
│   │   ├── pages/                 # Page components
│   │   ├── layouts/               # Layout templates
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── services/              # API services
│   │   ├── assets/                # Images, icons
│   │   ├── styles/                # TailwindCSS config
│   │   └── App.jsx
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── GETTING_STARTED.md
├── DEPLOYMENT.md
└── README.md
```

## 🏃 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Installation & Running

```bash
# Clone repository
git clone https://github.com/quinnne-tech/vehicle-rental-saas.git
cd vehicle-rental-saas

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up --build

# Seed database with demo data (in another terminal)
docker-compose exec backend python scripts/seed_db.py
```

### Access the Platform

- 🌐 **Frontend:** http://localhost:3000
- 🔌 **Backend API:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs
- 🔐 **Admin Panel:** http://localhost:3000/admin

### Demo Credentials

**Tenant User:**
- Email: `company@example.com`
- Password: `Company@123456`

**Super Admin:**
- Email: `admin@platform.com`
- Password: `Admin@123456`

## 🔐 Authentication Flow

```
1. Company registers on landing page
   ↓
2. Tenant workspace created automatically
   ↓
3. Owner account provisioned
   ↓
4. 14-day free trial assigned
   ↓
5. JWT token issued (contains user_id, tenant_id, role)
   ↓
6. Tenant middleware validates on every request
   ↓
7. Access to tenant-specific resources only
```

## 📊 Subscription Plans

| Feature | Starter | Growth | Enterprise |
|---------|---------|--------|------------|
| Vehicles | 5 | 25 | Unlimited |
| Users | 2 | 5 | Unlimited |
| Storage | 10GB | 100GB | Unlimited |
| Support | Email | Priority | 24/7 Phone |
| Trial Period | 14 days | 14 days | 30 days |
| Price | $99/mo | $299/mo | Custom |

## 🗄️ Database Collections

```javascript
{
  tenants: {
    _id: ObjectId,
    name: String,
    slug: String,
    plan: String,
    trial_end: Date,
    subscription_status: String,
    created_at: Date
  },
  users: {
    _id: ObjectId,
    tenant_id: ObjectId,
    email: String,
    password_hash: String,
    role: String,
    created_at: Date
  },
  vehicles: {
    _id: ObjectId,
    tenant_id: ObjectId,
    brand: String,
    model: String,
    status: String,
    daily_rate: Float,
    created_at: Date
  },
  renters: {
    _id: ObjectId,
    tenant_id: ObjectId,
    name: String,
    email: String,
    phone: String,
    created_at: Date
  },
  rentals: {
    _id: ObjectId,
    tenant_id: ObjectId,
    vehicle_id: ObjectId,
    renter_id: ObjectId,
    start_date: Date,
    end_date: Date,
    status: String,
    total_cost: Float,
    created_at: Date
  },
  transactions: {
    _id: ObjectId,
    tenant_id: ObjectId,
    rental_id: ObjectId,
    amount: Float,
    type: String,
    created_at: Date
  },
  subscriptions: {
    _id: ObjectId,
    tenant_id: ObjectId,
    plan: String,
    status: String,
    started_at: Date,
    expires_at: Date,
    auto_renew: Boolean
  },
  payments: {
    _id: ObjectId,
    tenant_id: ObjectId,
    subscription_id: ObjectId,
    amount: Float,
    status: String,
    provider: String,
    created_at: Date
  },
  audit_logs: {
    _id: ObjectId,
    tenant_id: ObjectId,
    user_id: ObjectId,
    action: String,
    resource: String,
    created_at: Date
  }
}
```

## 🔑 API Endpoints

```
Authentication:
  POST   /api/auth/register              # Company registration
  POST   /api/auth/login                 # User login
  POST   /api/auth/refresh               # Refresh JWT token
  POST   /api/auth/logout                # Logout user

Platform (Super Admin):
  GET    /api/platform/tenants           # List all tenants
  GET    /api/platform/analytics         # Global analytics
  PATCH  /api/platform/tenant/{id}       # Suspend/manage tenant
  GET    /api/platform/revenue           # Revenue dashboard

Tenant Dashboard:
  GET    /api/tenant/dashboard           # Dashboard KPIs
  GET    /api/tenant/vehicles            # List vehicles
  POST   /api/tenant/vehicles            # Create vehicle
  GET    /api/tenant/renters             # List renters
  POST   /api/tenant/renters             # Add renter
  GET    /api/tenant/rentals             # List rentals
  POST   /api/tenant/rentals             # Create rental
  GET    /api/tenant/transactions        # Transaction history

Subscription:
  GET    /api/subscription/plans         # Available plans
  POST   /api/subscription/subscribe     # Subscribe to plan
  GET    /api/subscription/current       # Current subscription
  POST   /api/subscription/cancel        # Cancel subscription

Billing:
  GET    /api/billing/invoices           # Payment history
  POST   /api/billing/payment-intent     # Create payment
  POST   /api/billing/webhook            # Payment webhook
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start dev server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build
```

## 📈 Scalability Features

- ✅ Horizontal scaling (stateless API)
- ✅ MongoDB sharding ready (on tenant_id)
- ✅ Redis caching layer
- ✅ Async/await for concurrency
- ✅ Background job queue (Celery)
- ✅ Database indexing on tenant_id + query fields
- ✅ Connection pooling
- ✅ Rate limiting middleware

## 🚀 Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete production deployment guide.

### Quick Environment Setup

```bash
# .env configuration
FASTAPI_ENV=production
MONGODB_URI=mongodb+srv://...
REDIS_URL=redis://...
JWT_SECRET_KEY=your-secret-key
STRIPE_API_KEY=sk_live_...
```

## 📝 Documentation

- [GETTING_STARTED.md](./GETTING_STARTED.md) - Step-by-step setup guide
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design documentation

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE.md

## 📞 Support & Contact

- Email: support@vehiclerental-saas.com
- Issues: GitHub Issues
- Documentation: `/docs` (API docs at `/api/docs`)

---

**Built with ❤️ for scalable SaaS platforms**

Last Updated: 2026-05-24
