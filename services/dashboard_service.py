from __future__ import annotations

from typing import Any, Dict

from services.currency_client import CurrencyApiClient
from services.insurance_client import InsuranceApiClient
from services.loan_client import LoanApiClient
from services.tax_simple_ireland import SimpleIrelandTaxCalculator


class DashboardService:
    def __init__(self, config: Dict[str, Any]):
        timeout = config['REQUEST_TIMEOUT']

        self.insurance_client = InsuranceApiClient(config['INSURANCE_API_URL'], timeout)
        self.loan_client = LoanApiClient(config['LOAN_API_URL'], config['LOAN_HEALTH_URL'], timeout)
        self.currency_client = CurrencyApiClient(config['CURRENCY_API_URL'], timeout)
        self.tax_calculator = SimpleIrelandTaxCalculator()

    def build_initial_context(self) -> Dict[str, Any]:
        status = self.health_check()
        rates = self.get_currency_rates()

        return {
            'status': status,
            'currency_rates': rates.get('rates', {}),
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            'tax': {'status': 'local', 'status_code': 200},  # now local
            'insurance': {'status': 'connected', 'status_code': 200},
            'loan': self.loan_client.check_health(),
        }

    def calculate_tax(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            gross = float(payload.get('gross', 0))
            deductions = float(payload.get('deductions', 0))

            result = self.tax_calculator.calculate(gross, deductions)

            return {
                'status': 'success',
                'status_code': 200,
                **result
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'status_code': 400
            }

    def calculate_insurance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.insurance_client.calculate(payload)

    def calculate_loan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.loan_client.calculate(payload)

    def get_currency_rates(self) -> Dict[str, Any]:
        return self.currency_client.latest_rates()