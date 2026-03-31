from __future__ import annotations

from services.base_client import BaseApiClient


class CurrencyApiClient:
    def __init__(self, rates_url: str, timeout: int):
        self.client = BaseApiClient(rates_url, timeout)

    def latest_rates(self):
        return self.client.safe_get()
