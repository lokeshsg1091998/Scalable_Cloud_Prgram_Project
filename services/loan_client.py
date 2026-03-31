from __future__ import annotations

from typing import Any, Dict

from services.base_client import BaseApiClient


class LoanApiClient:
    def __init__(self, calculate_url: str, health_url: str, timeout: int):
        self.calculator = BaseApiClient(calculate_url, timeout)
        self.health = BaseApiClient(health_url, timeout)

    def calculate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            'principal': float(payload.get('principal', 0) or 0),
            'annual_rate': float(payload.get('annual_rate', 0) or 0),
            'years': int(payload.get('years', 0) or 0),
        }
        return self.calculator.safe_post(normalized)

    def check_health(self) -> Dict[str, Any]:
        return self.health.safe_get()
