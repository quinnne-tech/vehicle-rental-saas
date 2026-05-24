"""Database seeding script with demo data"""

import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncClient
from app.core.config import settings
from app.core.security import hash_password
from app.core.constants import (
    UserRole, SubscriptionPlan, VehicleStatus, RentalStatus, TRIAL_DAYS
)


async def seed_database():
    """Seed database with demo data"""
    # Connect to MongoDB
    client = AsyncClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    
    try:
        print("🌱 Starting database seeding...")
        
        # Clear existing data
        print("🗑️  Clearing existing data...")
        await db.tenants.delete_many({})
        await db.users.delete_many({})
        await db.vehicles.delete_many({})
        await db.renters.delete_many({})
        await db.rentals.delete_many({})
        
        # Create demo tenants
        print("👥 Creating demo tenants...")
        tenant1 = {
            "name": "Fast Rentals Co",
            "slug": "fast-rentals-co",
            "plan": SubscriptionPlan.STARTER,
            "status": "active",
            "trial_end": datetime.utcnow() + timedelta(days=TRIAL_DAYS),
            "subscription_status": "trial",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result1 = await db.tenants.insert_one(tenant1)
        tenant1_id = result1.inserted_id
        
        tenant2 = {
            "name": "Premium Vehicle Rentals",
            "slug": "premium-vehicle-rentals",
            "plan": SubscriptionPlan.GROWTH,
            "status": "active",
            "trial_end": datetime.utcnow() + timedelta(days=TRIAL_DAYS),
            "subscription_status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result2 = await db.tenants.insert_one(tenant2)
        tenant2_id = result2.inserted_id
        
        # Create demo users
        print("👤 Creating demo users...")
        user1 = {
            "tenant_id": tenant1_id,
            "email": "company@example.com",
            "password_hash": hash_password("Company@123456"),
            "role": UserRole.OWNER,
            "first_name": "John",
            "last_name": "Doe",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result_user1 = await db.users.insert_one(user1)
        
        user2 = {
            "tenant_id": tenant2_id,
            "email": "admin@premium.com",
            "password_hash": hash_password("Admin@123456"),
            "role": UserRole.OWNER,
            "first_name": "Jane",
            "last_name": "Smith",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result_user2 = await db.users.insert_one(user2)
        
        # Update tenants with owner_id
        await db.tenants.update_one({"_id": tenant1_id}, {"$set": {"owner_id": result_user1.inserted_id}})
        await db.tenants.update_one({"_id": tenant2_id}, {"$set": {"owner_id": result_user2.inserted_id}})
        
        # Create demo vehicles
        print("🚗 Creating demo vehicles...")
        vehicles = [
            {
                "tenant_id": tenant1_id,
                "brand": "Toyota",
                "model": "Camry",
                "year": 2023,
                "license_plate": "ABC123",
                "status": VehicleStatus.AVAILABLE,
                "daily_rate": 50.0,
                "mileage": 15000,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "tenant_id": tenant1_id,
                "brand": "Honda",
                "model": "CR-V",
                "year": 2023,
                "license_plate": "XYZ789",
                "status": VehicleStatus.AVAILABLE,
                "daily_rate": 75.0,
                "mileage": 8000,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "tenant_id": tenant2_id,
                "brand": "BMW",
                "model": "3 Series",
                "year": 2023,
                "license_plate": "BM001",
                "status": VehicleStatus.AVAILABLE,
                "daily_rate": 120.0,
                "mileage": 5000,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
        vehicle_results = await db.vehicles.insert_many(vehicles)
        
        # Create demo renters
        print("👨 Creating demo renters...")
        renters = [
            {
                "tenant_id": tenant1_id,
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "phone": "555-0101",
                "id_number": "DL12345",
                "address": "123 Main St",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "tenant_id": tenant1_id,
                "name": "Bob Williams",
                "email": "bob@example.com",
                "phone": "555-0102",
                "id_number": "DL67890",
                "address": "456 Oak Ave",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
        renter_results = await db.renters.insert_many(renters)
        
        # Create demo rentals
        print("📅 Creating demo rentals...")
        rentals = [
            {
                "tenant_id": tenant1_id,
                "vehicle_id": vehicle_results[0],
                "renter_id": renter_results[0],
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=3),
                "status": RentalStatus.ACTIVE,
                "daily_rate": 50.0,
                "total_cost": 150.0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
        await db.rentals.insert_many(rentals)
        
        print("✅ Database seeding completed successfully!")
        print("\n📝 Demo Credentials:")
        print("Tenant 1:")
        print("  Email: company@example.com")
        print("  Password: Company@123456")
        print("\nTenant 2:")
        print("  Email: admin@premium.com")
        print("  Password: Admin@123456")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
