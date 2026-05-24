"""Tenant operations API endpoints"""

from fastapi import APIRouter, HTTPException, status, Request
from typing import List
from bson import ObjectId
from datetime import datetime
from app.models.schemas import (
    VehicleCreate, VehicleResponse, RenterCreate, RenterResponse,
    RentalCreate, RentalResponse, DashboardResponse, DashboardStats
)
from app.database.connection import get_db

router = APIRouter()


def get_tenant_id(request: Request) -> str:
    """Extract tenant_id from request state"""
    if not hasattr(request.state, "tenant_id") or not request.state.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context not found"
        )
    return request.state.tenant_id


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(request: Request):
    """Get tenant dashboard"""
    tenant_id = get_tenant_id(request)
    db = get_db()
    tenant_oid = ObjectId(tenant_id)
    
    # Get statistics
    total_vehicles = await db.vehicles.count_documents({"tenant_id": tenant_oid})
    available_vehicles = await db.vehicles.count_documents(
        {"tenant_id": tenant_oid, "status": "available"}
    )
    active_rentals = await db.rentals.count_documents(
        {"tenant_id": tenant_oid, "status": "active"}
    )
    
    # Get revenue
    transactions = await db.transactions.find(
        {"tenant_id": tenant_oid}
    ).to_list(None)
    total_revenue = sum(t.get("amount", 0) for t in transactions if t.get("type") == "payment")
    
    # Recent rentals
    recent_rentals = await db.rentals.find(
        {"tenant_id": tenant_oid}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "stats": DashboardStats(
            total_vehicles=total_vehicles,
            available_vehicles=available_vehicles,
            active_rentals=active_rentals,
            total_revenue=total_revenue,
            monthly_revenue=0,
        ),
        "recent_rentals": [
            VehicleResponse(
                id=str(r["_id"]),
                brand="",
                model="",
                year=0,
                license_plate="",
                status=r.get("status", "active"),
                daily_rate=r.get("daily_rate", 0),
                created_at=r.get("created_at", datetime.utcnow())
            )
            for r in recent_rentals
        ],
        "upcoming_returns": [],
    }


@router.get("/vehicles", response_model=List[VehicleResponse])
async def list_vehicles(request: Request):
    """List all vehicles for tenant"""
    tenant_id = get_tenant_id(request)
    db = get_db()
    vehicles = await db.vehicles.find(
        {"tenant_id": ObjectId(tenant_id)}
    ).to_list(None)
    
    return [
        VehicleResponse(
            id=str(v["_id"]),
            brand=v["brand"],
            model=v["model"],
            year=v["year"],
            license_plate=v["license_plate"],
            status=v["status"],
            daily_rate=v["daily_rate"],
            created_at=v["created_at"]
        )
        for v in vehicles
    ]


@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(request: Request, vehicle: VehicleCreate):
    """Create a new vehicle"""
    tenant_id = get_tenant_id(request)
    db = get_db()
    
    vehicle_data = {
        "tenant_id": ObjectId(tenant_id),
        "brand": vehicle.brand,
        "model": vehicle.model,
        "year": vehicle.year,
        "license_plate": vehicle.license_plate,
        "daily_rate": vehicle.daily_rate,
        "status": "available",
        "description": vehicle.description,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.vehicles.insert_one(vehicle_data)
    
    return VehicleResponse(
        id=str(result.inserted_id),
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        license_plate=vehicle.license_plate,
        status="available",
        daily_rate=vehicle.daily_rate,
        created_at=datetime.utcnow()
    )


@router.get("/renters", response_model=List[RenterResponse])
async def list_renters(request: Request):
    """List all renters for tenant"""
    tenant_id = get_tenant_id(request)
    db = get_db()
    renters = await db.renters.find(
        {"tenant_id": ObjectId(tenant_id)}
    ).to_list(None)
    
    return [
        RenterResponse(
            id=str(r["_id"]),
            name=r["name"],
            email=r["email"],
            phone=r["phone"],
            created_at=r["created_at"]
        )
        for r in renters
    ]


@router.post("/renters", response_model=RenterResponse, status_code=status.HTTP_201_CREATED)
async def create_renter(request: Request, renter: RenterCreate):
    """Create a new renter"""
    tenant_id = get_tenant_id(request)
    db = get_db()
    
    renter_data = {
        "tenant_id": ObjectId(tenant_id),
        "name": renter.name,
        "email": renter.email,
        "phone": renter.phone,
        "id_number": renter.id_number,
        "address": renter.address,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.renters.insert_one(renter_data)
    
    return RenterResponse(
        id=str(result.inserted_id),
        name=renter.name,
        email=renter.email,
        phone=renter.phone,
        created_at=datetime.utcnow()
    )


@router.get("/rentals", response_model=List[RentalResponse])
async def list_rentals(request: Request):
    """List all rentals for tenant"""
    tenant_id = get_tenant_id(request)
    db = get_db()
    rentals = await db.rentals.find(
        {"tenant_id": ObjectId(tenant_id)}
    ).to_list(None)
    
    return [
        RentalResponse(
            id=str(r["_id"]),
            vehicle_id=str(r["vehicle_id"]),
            renter_id=str(r["renter_id"]),
            start_date=r["start_date"],
            end_date=r["end_date"],
            status=r["status"],
            total_cost=r["total_cost"],
            created_at=r["created_at"]
        )
        for r in rentals
    ]


@router.post("/rentals", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(request: Request, rental: RentalCreate):
    """Create a new rental"""
    tenant_id = get_tenant_id(request)
    db = get_db()
    tenant_oid = ObjectId(tenant_id)
    
    # Verify vehicle exists and belongs to tenant
    vehicle = await db.vehicles.find_one(
        {"_id": ObjectId(rental.vehicle_id), "tenant_id": tenant_oid}
    )
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Calculate total cost
    days = (rental.end_date - rental.start_date).days
    total_cost = days * vehicle["daily_rate"]
    
    rental_data = {
        "tenant_id": tenant_oid,
        "vehicle_id": ObjectId(rental.vehicle_id),
        "renter_id": ObjectId(rental.renter_id),
        "start_date": rental.start_date,
        "end_date": rental.end_date,
        "status": "active",
        "daily_rate": vehicle["daily_rate"],
        "total_cost": total_cost,
        "notes": rental.notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.rentals.insert_one(rental_data)
    
    # Update vehicle status
    await db.vehicles.update_one(
        {"_id": ObjectId(rental.vehicle_id)},
        {"$set": {"status": "rented"}}
    )
    
    return RentalResponse(
        id=str(result.inserted_id),
        vehicle_id=rental.vehicle_id,
        renter_id=rental.renter_id,
        start_date=rental.start_date,
        end_date=rental.end_date,
        status="active",
        total_cost=total_cost,
        created_at=datetime.utcnow()
    )
