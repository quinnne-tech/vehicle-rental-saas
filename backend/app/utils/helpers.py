"""Helper utility functions"""

from typing import Optional
from datetime import datetime
import slug as slug_lib
from bson import ObjectId


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    return slug_lib.slug(text)


def is_valid_objectid(oid: str) -> bool:
    """Check if string is valid MongoDB ObjectId"""
    try:
        ObjectId(oid)
        return True
    except:
        return False


def calculate_rental_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate number of rental days"""
    delta = end_date - start_date
    return max(1, delta.days)


def calculate_rental_cost(daily_rate: float, days: int) -> float:
    """Calculate total rental cost"""
    return daily_rate * days
