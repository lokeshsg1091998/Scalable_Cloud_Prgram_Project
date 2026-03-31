from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class BaseApiClient:
    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout

    def post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(self.base_url, json=payload, timeout=self.timeout)
        return self._build_response(response)

    def get(self) -> Dict[str, Any]:
        response = requests.get(self.base_url, timeout=self.timeout)
        return self._build_response(response)

    @staticmethod
    def _build_response(response: requests.Response) -> Dict[str, Any]:
        data: Dict[str, Any]
        try:
            data = response.json()
        except ValueError:
            data = {'raw_response': response.text}
        data['status_code'] = response.status_code
        return data

    def safe_get(self) -> Dict[str, Any]:
        return self._safe_request(self.get)

    def safe_post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._safe_request(lambda: self.post(payload))

    @staticmethod
    def _safe_request(callback) -> Dict[str, Any]:
        try:
            return callback()
        except requests.RequestException as exc:
            return {
                'status_code': 503,
                'error': 'Service temporarily unavailable',
                'details': str(exc),
            }
