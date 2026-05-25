# Architecture & Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Browsers                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                          │
│              (SSL Termination, Load Balancing)                  │
└──────────┬──────────────────────────────────┬────────────────────┘
           │                                  │
           ▼ HTTP                            ▼ HTTP
  ┌─────────────────┐            ┌────────────────────────┐
  │   Frontend      │            │  Backend API           │
  │  (React)        │            │  (FastAPI)             │
  │  Port: 3000     │            │  Port: 8000            │
  │                 │            │                        │
  │ - Landing Page  │            │ - Auth Routes          │
  │ - Dashboard     │            │ - Tenant Routes        │
  │ - Admin Panel   │            │ - Platform Routes      │
  └─────────────────┘            │ - Subscription Routes  │
                                 │ - Billing Routes       │
                                 └────────────┬───────────┘
                                              │ TCP
                                              ▼
                   ┌──────────────────────────┴─────────────────┐
                   │                                            │
                   ▼                                            ▼
        ┌────────────────────┐                    ┌──────────────────┐
        │  MongoDB Database  │                    │   Redis Cache    │
        │  (Port: 27017)     │                    │ (Port: 6379)     │
        │                    │                    │                  │
        │ Collections:       │                    │ - Sessions       │
        │ - tenants          │                    │ - Cache Layers   │
        │ - users            │                    │ - Rate Limiting  │
        │ - vehicles         │                    │ - Task Queue     │
        │ - renters          │                    │                  │
        │ - rentals          │                    └──────────────────┘
        │ - transactions     │
        │ - subscriptions    │          ┌─────────────────────┐
        │ - payments         │          │ Celery Worker       │
        │ - audit_logs       │          │ (Background Jobs)   │
        └────────────────────┘          └─────────────────────┘
                                                    ▲
                                                    │
                                        ┌───────────┴───────────┐
                                        │   Celery Beat         │
                                        │  (Task Scheduler)     │
                                        └───────────────────────┘
```

## Multi-Tenant Data Isolation

```
Request from Tenant A
         │
         ▼
┌─────────────────────┐
│  Tenant Middleware  │  ← Extracts tenant_id from JWT
│  Extracts tenant_id │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Request State                  │
│  {                              │
│    tenant_id: "ObjectId(...)",  │
│    user_id: "ObjectId(...)",    │
│    user_role: "owner",          │
│    is_authenticated: true        │
│  }                              │
└──────────┬──────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  Route Handler                     │
│  - Validates tenant context        │
│  - Queries with tenant_id filter   │
│  - Returns only tenant data        │
└──────────┬───────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  MongoDB Query                     │
│  db.vehicles.find({               │
│    tenant_id: ObjectId("..."),   │
│    ...other filters               │
│  })                               │
│                                   │
│  Result: Only Tenant A vehicles   │
└────────────────────────────────────┘
```

## Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    1. Registration                           │
└──────────────────────────────────────────────────────────────┘

Company Details          Validation          Database
   │                        │                   │
   └──────► Email Check ────┼─────────────────►│ users.email unique
            Password Hash   │                   │
            Create Tenant ──┼─────────────────►│ tenants collection
            Create Owner ───┼─────────────────►│ users collection
            Trial Period ───┼─────────────────►│ tenants.trial_end

┌──────────────────────────────────────────────────────────────┐
│                    2. Login                                  │
└──────────────────────────────────────────────────────────────┘

Email + Password         Verification        Token Generation
   │                        │                     │
   └──────► Find User ──────┼──────────────────┐  │
            Verify Hash     │                  │  │
                            ▼                  │  │
                    ┌──────────────────┐      │  │
                    │ Credentials Valid│      │  │
                    └──────────────────┘      │  │
                                              ▼  ▼
                                    ┌─────────────────────┐
                                    │ Create Access Token │
                                    │ {                   │
                                    │  sub: user_id       │
                                    │  tenant_id: ...     │
                                    │  role: owner        │
                                    │  exp: datetime      │
                                    │ }                   │
                                    │                     │
                                    │ Create Refresh Token│
                                    │ {                   │
                                    │  sub: user_id       │
                                    │  type: refresh      │
                                    │  exp: datetime      │
                                    │ }                   │
                                    └─────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 3. API Request with Token                    │
└──────────────────────────────────────────────────────────────┘

Client Request            Middleware              Route
   │                          │                     │
   └──► Authorization: Bearer [TOKEN]
        │                     ▼
        │            ┌─────────────────────┐
        │            │ Extract Token       │
        │            │ Decode JWT          │
        │            │ Validate Signature  │
        │            │ Check Expiration    │
        │            └──────────┬──────────┘
        │                       │
        │                       ▼
        │            ┌──────────────────────────┐
        │            │ Attach to Request State  │
        │            │ - tenant_id              │
        │            │ - user_id                │
        │            │ - user_role              │
        │            └──────────┬───────────────┘
        │                       │
        └───────────────────────┼──► Process Request with tenant context
                                │
                                ▼
                    ┌───────────────────────────────┐
                    │ Return Tenant-Scoped Response │
                    └───────────────────────────────┘
```

## Subscription & Billing Flow

```
┌─────────────────────────────────────────────────────────────┐
│               Registration → Auto Trial                     │
└─────────────────────────────────────────────────────────────┘

Company Registered
      │
      ▼
┌──────────────────────────────────────────┐
│ Create Tenant Document                   │
│ {                                        │
│   plan: "free_trial"                    │
│   subscription_status: "trial"           │
│   trial_end: now + 14 days               │
│   created_at: now                        │
│ }                                        │
└──────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────┐
│ Trial Features Available                 │
│ - 10 vehicles                            │
│ - 3 users                                │
│ - 5GB storage                            │
│ - Email support                          │
└──────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            Daily Background Job: Check Expiry               │
└─────────────────────────────────────────────────────────────┘

Celery Beat (Every 24h)
      │
      ▼
┌────────────────────────────┐
│ check_subscription_expiry  │
└────────────────────────────┘
      │
      ├──► Find trials expiring in 7 days
      │    └──► Send email reminder
      │
      ├──► Find expired trials
      │    └──► Update status to "expired"
      │    └──► Block access
      │
      └──► Find active subs expiring
           └──► Send renewal reminder

┌─────────────────────────────────────────────────────────────┐
│              Subscription Upgrade Flow                      │
└─────────────────────────────────────────────────────────────┘

User Clicks "Upgrade"
      │
      ▼
┌──────────────────────────────────────┐
│ Show Pricing Plans                   │
│ - Starter: $99/mo (5 vehicles)       │
│ - Growth: $299/mo (25 vehicles)      │
│ - Enterprise: Custom                 │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ User Selects Plan & Provides Payment │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Create Payment Intent                │
│ (Stripe/Midtrans/Xendit)             │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Redirect to Payment Gateway          │
│ (Secure Payment Processing)          │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Payment Gateway Webhook Received      │
│ POST /api/billing/webhook             │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Update Tenant Document               │
│ {                                    │
│   plan: "growth"                    │
│   subscription_status: "active"      │
│   expires_at: now + 30 days          │
│   auto_renew: true                   │
│ }                                    │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Features Unlocked                    │
│ - 25 vehicles available              │
│ - 5 user accounts                    │
│ - 100GB storage                      │
└──────────────────────────────────────┘
```

## Usage Limit Enforcement

```
When User Tries to Create Vehicle
      │
      ▼
┌──────────────────────────────────────┐
│ Get Tenant Subscription Plan         │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Check Plan Vehicle Limit             │
│ (e.g., Starter = 5 vehicles)         │
└──────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────┐
│ Count Current Vehicles               │
│ db.vehicles.countDocuments(           │
│   {tenant_id: ...}                   │
│ )                                    │
└──────────────────────────────────────┘
      │
      ├─► COUNT < LIMIT ─────► ✅ Allow Creation
      │
      └─► COUNT >= LIMIT ─────► ❌ Block Creation
                                 └─► Show Upgrade Prompt
```

## Celery Background Jobs

```
┌──────────────────────────────────────────────────────────────┐
│                  Job Scheduling with Celery Beat             │
└──────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  Celery Beat Scheduler                 │
│  (Runs on schedule)                    │
└────────────────────────────────────────┘
         │
         ├──► Every 24 hours:
         │    - check_subscription_expiry
         │    - send_trial_ending_reminder
         │    - check_overdue_rentals
         │
         ├──► Every 6 hours:
         │    - cleanup_old_sessions
         │
         └──► Every hour:
              - update_vehicle_statistics

┌────────────────────────────────────────┐
│  Task Queue (Redis)                    │
│  - Scheduled tasks waiting execution   │
└────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│  Celery Worker                         │
│  (Processes tasks from queue)          │
│  (Multiple workers can run)            │
└────────────────────────────────────────┘
         │
         ├──► Send Emails
         ├──► Update Database
         ├──► Generate Reports
         └──► Send Notifications

┌────────────────────────────────────────┐
│  Result Backend (Redis)                │
│  - Store task results                  │
│  - Track task status                   │
└────────────────────────────────────────┘
```

## Database Indexing Strategy

```
Optimized Indexes for Performance:

1. Tenant Isolation Indexes
   ├── users: { tenant_id: 1, email: 1 }
   ├── vehicles: { tenant_id: 1, status: 1 }
   ├── renters: { tenant_id: 1, email: 1 }
   └── rentals: { tenant_id: 1, vehicle_id: 1 }

2. Query Performance Indexes
   ├── rentals: { tenant_id: 1, created_at: -1 }
   ├── transactions: { tenant_id: 1, created_at: -1 }
   └── subscriptions: { tenant_id: 1, status: 1 }

3. Unique Constraint Indexes
   ├── users: { email: 1 } (UNIQUE)
   ├── tenants: { slug: 1 } (UNIQUE)
   └── vehicles: { license_plate: 1, tenant_id: 1 } (UNIQUE per tenant)

Index Strategy Benefits:
- Fast tenant-scoped queries
- Efficient sorting by date
- Support for sharding on tenant_id
- Unique constraints per tenant
```

## API Request/Response Flow

```
Client                      Nginx              Backend
  │                           │                  │
  ├──► HTTP Request ──────────┼─────────────────►│
  │    /api/tenant/vehicles   │                  │
  │    Authorization: Bearer  │                  │
  │                           │                  ▼
  │                           │          ┌──────────────────┐
  │                           │          │ Tenant Middleware│
  │                           │          │ Extract tenant_id│
  │                           │          └──────────────────┘
  │                           │                  │
  │                           │                  ▼
  │                           │          ┌──────────────────┐
  │                           │          │ Auth Middleware  │
  │                           │          │ Validate JWT     │
  │                           │          └──────────────────┘
  │                           │                  │
  │                           │                  ▼
  │                           │          ┌──────────────────┐
  │                           │          │ Route Handler    │
  │                           │          │ (tenant.py)      │
  │                           │          └──────────────────┘
  │                           │                  │
  │                           │                  ▼
  │                           │          ┌──────────────────┐
  │                           │          │ MongoDB Query    │
  │                           │          │ {tenant_id: ...} │
  │                           │          └──────────────────┘
  │                           │                  │
  │◄──────────────────────────┼──────────────────┤
  │    JSON Response          │                  │
  │    200 OK                 │                  │
  │    [vehicles...]          │                  │
  │                           │                  │
```

## Scalability Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Load Balancer (ALB)                        │
│            Distributes traffic across zones                │
└─────────────────────────────────────────────────────────────┘
                    │                          │
                    ▼                          ▼
        ┌─────────────────────┐    ┌─────────────────────┐
        │ Zone 1              │    │ Zone 2              │
        │ Backend Instances   │    │ Backend Instances   │
        │ (Stateless)         │    │ (Stateless)         │
        │ Replicas: 2-4       │    │ Replicas: 2-4       │
        └─────────────────────┘    └─────────────────────┘
                    │                          │
                    └──────────────┬───────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │  MongoDB Replica Set     │
                    │  (Primary + Secondaries) │
                    │                          │
                    │ Sharded on tenant_id    │
                    │ Shard 1: Tenants A-M    │
                    │ Shard 2: Tenants N-Z    │
                    └──────────────────────────┘
                                   │
                    ┌──────────────┴───────────┐
                    ▼                          ▼
            ┌────────────────┐        ┌────────────────┐
            │ Redis Cluster  │        │ Redis Cluster  │
            │ (Cache)        │        │ (Cache)        │
            └────────────────┘        └────────────────┘
```

This architecture supports:
- **Horizontal scaling:** Add more backend instances
- **Database sharding:** Distribute data across shards
- **Geographic distribution:** Replicas in multiple zones
- **Auto-recovery:** Automatic failover for replicas
- **Performance:** Sub-100ms queries for 1000+ tenants
