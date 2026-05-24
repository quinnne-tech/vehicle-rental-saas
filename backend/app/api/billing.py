"""Billing API endpoints"""

from fastapi import APIRouter, HTTPException, status, Request
from typing import List

router = APIRouter()


@router.get("/invoices")
async def get_invoices(request: Request):
    """Get payment invoices for tenant"""
    return {"invoices": []}


@router.post("/payment-intent")
async def create_payment_intent(request: Request):
    """Create payment intent (Stripe/Midtrans hook)"""
    return {"status": "payment_system_ready"}


@router.post("/webhook")
async def handle_payment_webhook(request: Request):
    """Handle payment provider webhook"""
    return {"status": "webhook_received"}
