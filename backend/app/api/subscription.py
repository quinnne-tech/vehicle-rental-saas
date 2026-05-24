"""Subscription management API endpoints"""

from fastapi import APIRouter, HTTPException, status, Request
from typing import List
from bson import ObjectId
from datetime import datetime
from app.core.constants import SubscriptionPlan, Plan_PRICES, PLAN_LIMITS
from app.models.schemas import PlanResponse, SubscriptionResponse
from app.database.connection import get_db

router = APIRouter()


@router.get("/plans", response_model=List[PlanResponse])
async def get_plans():
    """Get available subscription plans"""
    plans = [
        PlanResponse(
            id="starter",
            name="Starter",
            price=99,
            vehicles_limit=5,
            users_limit=2,
            storage_limit=10,
        ),
        PlanResponse(
            id="growth",
            name="Growth",
            price=299,
            vehicles_limit=25,
            users_limit=5,
            storage_limit=100,
        ),
        PlanResponse(
            id="enterprise",
            name="Enterprise",
            price=0,
            vehicles_limit=None,
            users_limit=None,
            storage_limit=None,
        ),
    ]
    return plans


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(request: Request):
    """Get current tenant subscription"""
    if not hasattr(request.state, "tenant_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context not found"
        )
    
    tenant_id = ObjectId(request.state.tenant_id)
    db = get_db()
    
    tenant = await db.tenants.find_one({"_id": tenant_id})
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return SubscriptionResponse(
        plan=tenant["plan"],
        status=tenant["subscription_status"],
        started_at=tenant.get("created_at", datetime.utcnow()),
        expires_at=tenant.get("trial_end"),
        auto_renew=True,
    )
