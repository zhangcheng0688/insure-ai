"""User authentication and quota management API."""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
import hashlib
import uuid

router = APIRouter()

# --- In-memory user store (MVP) → move to PostgreSQL for production ---
# In production, this syncs with Supabase Auth via webhook
_users: dict[str, dict] = {}
_api_keys: dict[str, str] = {}  # api_key → user_id

# Plan definitions
PLANS = {
    "trial": {
        "name": "7天免费试用",
        "requests_per_day": 100,
        "max_pages": 0,  # unlimited
        "output_formats": ["markdown", "pdf", "docx"],
        "price": 0,
        "trial_days": 7,
    },
    "free": {
        "name": "免费版",
        "requests_per_day": 3,
        "max_pages": 5,
        "output_formats": ["markdown"],
        "price": 0,
    },
    "pro": {
        "name": "专业版 Pro",
        "requests_per_day": 50,
        "max_pages": 0,
        "output_formats": ["markdown", "pdf", "docx"],
        "price": 39,
    },
    "enterprise": {
        "name": "企业版 Enterprise",
        "requests_per_day": 500,
        "max_pages": 0,
        "output_formats": ["markdown", "pdf", "docx"],
        "price": 199,
    },
}

# Trial duration in days
TRIAL_DAYS = 7


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:16]


class UserCreate(BaseModel):
    email: str
    supabase_uid: str
    plan: str = "trial"  # 默认7天免费试用


class APIKeyCreate(BaseModel):
    name: str = "Default"


@router.post("/register")
async def register_user(user: UserCreate):
    """Register or sync user from Supabase Auth. New users get 7-day free trial."""
    uid = user.supabase_uid
    if uid not in _users:
        now = datetime.now()
        _users[uid] = {
            "email": user.email,
            "supabase_uid": uid,
            "plan": "trial",  # 新用户默认7天试用
            "daily_requests": 0,
            "total_requests": 0,
            "request_date": str(date.today()),
            "api_keys": [],
            "created_at": now.isoformat(),
            "trial_start": now.isoformat(),
        }
    return {
        "status": "ok",
        "user_id": uid,
        "plan": _users[uid]["plan"],
        "plan_name": PLANS[_users[uid]["plan"]]["name"],
        "trial_start": _users[uid].get("trial_start"),
    }


@router.post("/api-keys")
async def create_api_key(
    key_data: APIKeyCreate,
    authorization: str = Header(None),
):
    """Generate an API key for the authenticated user."""
    user_id = await _get_user_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    raw_key = f"insureai_{uuid.uuid4().hex}{uuid.uuid4().hex}"
    hashed = _hash_key(raw_key)
    _api_keys[hashed] = user_id
    _users[user_id]["api_keys"].append({
        "name": key_data.name,
        "key_prefix": raw_key[:12] + "...",
        "key_hash": hashed,
        "created_at": datetime.now().isoformat(),
    })
    # Return the raw key ONCE — user must save it
    return {"api_key": raw_key, "name": key_data.name}


def _check_trial_expiry(user: dict) -> str:
    """Check if trial has expired and auto-downgrade. Returns current plan key."""
    if user.get("plan") == "trial" and user.get("trial_start"):
        trial_start = datetime.fromisoformat(user["trial_start"])
        days_elapsed = (datetime.now() - trial_start).days
        if days_elapsed >= TRIAL_DAYS:
            user["plan"] = "free"
            return "free"
    return user.get("plan", "free")


def _days_left_in_trial(user: dict) -> int:
    """Return days remaining in trial, or 0 if not in trial."""
    if user.get("plan") != "trial" or not user.get("trial_start"):
        return 0
    trial_start = datetime.fromisoformat(user["trial_start"])
    days_elapsed = (datetime.now() - trial_start).days
    return max(0, TRIAL_DAYS - days_elapsed)


@router.get("/quota")
async def check_quota(authorization: str = Header(None)):
    """Check current user's quota and trial status."""
    user_id = await _get_user_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = _users[user_id]
    today = str(date.today())

    # Check trial expiry
    _check_trial_expiry(user)
    days_left = _days_left_in_trial(user)

    # Reset daily counter if new day
    if user.get("request_date") != today:
        user["daily_requests"] = 0
        user["request_date"] = today

    plan = PLANS.get(user["plan"], PLANS["free"])
    remaining = max(0, plan["requests_per_day"] - user["daily_requests"])

    return {
        "plan": plan["name"],
        "plan_key": user["plan"],
        "daily_limit": plan["requests_per_day"],
        "used_today": user["daily_requests"],
        "remaining_today": remaining,
        "total_requests": user["total_requests"],
        "output_formats": plan["output_formats"],
        "trial_days_left": days_left,
        "is_trial": user["plan"] == "trial",
    }


@router.post("/quota/consume")
async def consume_quota(authorization: str = Header(None)):
    """Consume one request from quota. Checks trial expiry first."""
    user_id = await _get_user_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = _users[user_id]
    today = str(date.today())

    # Check trial expiry
    current_plan = _check_trial_expiry(user)
    days_left = _days_left_in_trial(user)

    if user.get("request_date") != today:
        user["daily_requests"] = 0
        user["request_date"] = today

    plan = PLANS.get(current_plan, PLANS["free"])
    if user["daily_requests"] >= plan["requests_per_day"]:
        if current_plan == "trial":
            detail = f"试用期每天{plan['requests_per_day']}次，今日已用完。明天再来！"
        else:
            detail = f"今日{plan['requests_per_day']}次已用完。升级Pro解锁每日50次。"
        raise HTTPException(status_code=429, detail=detail)

    user["daily_requests"] += 1
    user["total_requests"] += 1
    remaining = plan["requests_per_day"] - user["daily_requests"]

    return {
        "consumed": True,
        "remaining_today": remaining,
        "total_requests": user["total_requests"],
        "trial_days_left": days_left,
    }


@router.post("/plan/upgrade")
async def upgrade_plan(
    plan_key: str,
    authorization: str = Header(None),
):
    """Upgrade user plan (called after Lemon Squeezy payment webhook)."""
    user_id = await _get_user_from_auth(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    if plan_key not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan_key}")

    _users[user_id]["plan"] = plan_key
    plan = PLANS[plan_key]
    return {"status": "upgraded", "plan": plan["name"], "daily_limit": plan["requests_per_day"]}


@router.post("/lemon-squeezy-webhook")
async def lemon_squeezy_webhook(payload: dict):
    """Handle Lemon Squeezy payment webhook."""
    event_type = payload.get("meta", {}).get("event_name", "")
    custom_data = payload.get("data", {}).get("attributes", {}).get("custom_data", {})
    supabase_uid = custom_data.get("supabase_uid", "")
    variant_name = payload.get("data", {}).get("attributes", {}).get("variant_name", "")

    if not supabase_uid:
        return {"status": "skipped", "reason": "no supabase_uid"}

    # Map Lemon Squeezy variant to plan
    plan_map = {"Pro": "pro", "Enterprise": "enterprise", "Free": "free", "Trial": "trial"}
    plan_key = plan_map.get(variant_name, "free")

    if supabase_uid in _users:
        _users[supabase_uid]["plan"] = plan_key

    return {"status": "ok", "user": supabase_uid, "plan": plan_key}


async def _get_user_from_auth(authorization: Optional[str]) -> Optional[str]:
    """Resolve user from Authorization header (Bearer {api_key}) or direct supabase_uid."""
    if not authorization:
        return None

    token = authorization.replace("Bearer ", "")

    # Check if it's an API key
    hashed = _hash_key(token)
    if hashed in _api_keys:
        return _api_keys[hashed]

    # Check if it's a direct supabase_uid (from Supabase JWT)
    if token in _users:
        return token

    return None


def verify_api_key(api_key: str) -> Optional[str]:
    """Verify an API key and return user_id. Used as middleware."""
    hashed = _hash_key(api_key)
    return _api_keys.get(hashed)
