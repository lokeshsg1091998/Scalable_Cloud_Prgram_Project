from __future__ import annotations

from typing import Any, Dict

from services.base_client import BaseApiClient


class TaxApiClient:
    def __init__(self, calculate_url: str, health_url: str, timeout: int):
        self.calculator = BaseApiClient(calculate_url, timeout)
        self.health = BaseApiClient(health_url, timeout)

    def calculate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            'gross_income': float(payload.get('gross_income', 0) or 0),
            'deductions': float(payload.get('deductions', 0) or 0),
            'tax_year': str(payload.get('tax_year', '2026')),
        }
        return self.calculator.safe_post(normalized)

    def check_health(self) -> Dict[str, Any]:
        return self.health.safe_get()
