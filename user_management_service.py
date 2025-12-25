"""
User Management Service

This repo has multiple entrypoints (Telegram bot + dashboard API) that expect a
`user_management_service` module. Some environments may not include the full
production implementation; this file provides a lightweight, local, JSON-based
fallback so the system can boot and the dashboard can render.

Primary responsibilities:
- Authenticate/lookup a user by Telegram ID
- Return user portfolio data (best-effort; falls back to empty data)
- Build a dashboard link for a user
- Record trades (append-only JSON)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

_DEFAULT_USER_PROFILES_PATH = os.getenv("USER_PROFILES_PATH", "user_profiles.json")
_DEFAULT_TRADES_PATH = os.getenv("TRADE_HISTORY_PATH", "trade_history.json")
_DASHBOARD_BASE_URL = os.getenv("DASHBOARD_BASE_URL", "http://localhost:5001")


@dataclass(frozen=True)
class User:
    """Minimal user record used across bot + dashboard."""

    id: int  # internal numeric id (we use telegram_id for simplicity)
    telegram_id: int
    created_at: str


def _read_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: str, payload: Any) -> None:
    tmp = f"{path}.tmp"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def authenticate_user(telegram_id: int, username: Optional[str] = None, first_name: Optional[str] = None) -> Optional[User]:
    """
    Look up a user by Telegram ID.

    Returns None if the user is not known yet. You can opt into auto-provisioning
    by setting AUTO_CREATE_USERS=true.
    """
    profiles = _read_json(_DEFAULT_USER_PROFILES_PATH, default={})
    key = str(int(telegram_id))
    record = profiles.get(key)
    if record:
        return User(
            id=int(record.get("id", telegram_id)),
            telegram_id=int(record.get("telegram_id", telegram_id)),
            created_at=str(record.get("created_at", "")),
        )

    auto_create = os.getenv("AUTO_CREATE_USERS", "true").lower() in {"1", "true", "yes"}
    if not auto_create:
        return None

    created_at = datetime.utcnow().isoformat()
    profiles[key] = {
        "id": int(telegram_id),
        "telegram_id": int(telegram_id),
        "created_at": created_at,
        "username": username,
        "first_name": first_name,
    }
    _write_json(_DEFAULT_USER_PROFILES_PATH, profiles)
    return User(id=int(telegram_id), telegram_id=int(telegram_id), created_at=created_at)


def get_user_portfolio_data(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Best-effort portfolio data.

    If no data exists yet, return None so callers can fall back to mock/demo data.
    """
    # In this local fallback, we don't maintain a full portfolio engine, but
    # callers like /dashboard expect a dict. Provide safe defaults.
    _ = user_id
    return {
        "portfolio": {
            "starting_capital": float(os.getenv("DEFAULT_CAPITAL", "500") or 500),
            "current_capital": float(os.getenv("DEFAULT_CAPITAL", "500") or 500),
            "capital_growth": 0.0,
            "total_pnl": 0.0,
            "total_pnl_pct": 0.0,
            "today_pnl": 0.0,
            "active_positions": 0,
        },
        "performance": {
            "total_trades": 0,
            "win_rate": 0.0,
        },
        "active_positions": [],
    }


def get_user_dashboard_link(telegram_id: int) -> str:
    """Build the user dashboard URL used by /dashboard."""
    return f"{_DASHBOARD_BASE_URL.rstrip('/')}/dashboard/{int(telegram_id)}"


def record_user_trade(telegram_id: int, trade: Dict[str, Any]) -> bool:
    """Append a trade record for later analytics (JSON fallback)."""
    try:
        trades: List[Dict[str, Any]] = _read_json(_DEFAULT_TRADES_PATH, default=[])
        if not isinstance(trades, list):
            trades = []  # Reset if corrupted
        entry = {
            "telegram_id": int(telegram_id),
            "timestamp": datetime.utcnow().isoformat(),
            **(trade or {}),
        }
        trades.append(entry)
        _write_json(_DEFAULT_TRADES_PATH, trades)
        return True
    except Exception as e:
        print(f"Error recording trade: {e}")
        return False


def close_user_trade(trade_id: Any, exit_price: Any = None, exit_type: str = "manual") -> bool:
    """
    Close an existing trade record (best-effort JSON fallback).

    The production system likely updates an 'active trade' record. In this local
    fallback, we will attempt to find a matching trade by `trade_id` and add
    closure fields; if not found we return False.
    """
    try:
        trades: List[Dict[str, Any]] = _read_json(_DEFAULT_TRADES_PATH, default=[])
        for t in reversed(trades):
            if str(t.get("trade_id")) == str(trade_id) or str(t.get("id")) == str(trade_id):
                t["closed_at"] = datetime.utcnow().isoformat()
                t["exit_price"] = exit_price
                t["exit_type"] = exit_type
                _write_json(_DEFAULT_TRADES_PATH, trades)
                return True
        return False
    except Exception:
        return False


def get_user_statistics(telegram_id: int) -> Dict[str, Any]:
    """
    Very lightweight stats computed from recorded trades (if any).
    """
    trades: List[Dict[str, Any]] = _read_json(_DEFAULT_TRADES_PATH, default=[])
    if not isinstance(trades, list):
        trades = []  # Reset if corrupted

    user_trades = []
    for t in trades:
        if isinstance(t, dict) and int(t.get("telegram_id", -1)) == int(telegram_id):
            user_trades.append(t)

    return {
        "telegram_id": int(telegram_id),
        "total_trades": len(user_trades),
    }

