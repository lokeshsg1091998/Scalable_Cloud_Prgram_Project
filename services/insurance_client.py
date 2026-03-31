from __future__ import annotations

from typing import Any, Dict

from services.base_client import BaseApiClient


class InsuranceApiClient:
    def __init__(self, estimate_url: str, timeout: int):
        self.client = BaseApiClient(estimate_url, timeout)

    def calculate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            'age': int(payload.get('age', 0) or 0),
            'term_years': int(payload.get('term_years', 0) or 0),
            'sum_assured': float(payload.get('sum_assured', 0) or 0),
            'gender': str(payload.get('gender', 'Male')),
            'smoker': str(payload.get('smoker', 'No')),
            'payment_frequency': str(payload.get('payment_frequency', 'Monthly')),
        }
        return self.client.safe_post(normalized)
