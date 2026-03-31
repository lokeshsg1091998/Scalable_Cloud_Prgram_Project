import json
from dataclasses import asdict, dataclass


@dataclass
class TaxBreakdown:
    gross_income: float
    deductions: float
    taxable_income: float
    income_tax: float
    usc: float
    prsi: float
    total_tax: float
    net_income: float
    effective_tax_rate: float
    tax_year: str


class IrelandTaxCalculator:
    STANDARD_RATE_BAND = 44000.0
    STANDARD_RATE = 0.20
    HIGHER_RATE = 0.40
    USC_BANDS = [
        (12012.0, 0.005),
        (27382.0, 0.02),
        (70044.0, 0.03),
    ]
    USC_TOP_RATE = 0.08
    PRSI_RATE = 0.041

    def calculate(self, gross_income: float, deductions: float, tax_year: str) -> TaxBreakdown:
        taxable_income = max(gross_income - deductions, 0.0)
        income_tax = self._income_tax(taxable_income)
        usc = self._usc(taxable_income)
        prsi = taxable_income * self.PRSI_RATE
        total_tax = income_tax + usc + prsi
        net_income = gross_income - total_tax
        effective_tax_rate = round((total_tax / gross_income) * 100, 2) if gross_income else 0.0

        return TaxBreakdown(
            gross_income=round(gross_income, 2),
            deductions=round(deductions, 2),
            taxable_income=round(taxable_income, 2),
            income_tax=round(income_tax, 2),
            usc=round(usc, 2),
            prsi=round(prsi, 2),
            total_tax=round(total_tax, 2),
            net_income=round(net_income, 2),
            effective_tax_rate=effective_tax_rate,
            tax_year=tax_year,
        )

    def _income_tax(self, taxable_income: float) -> float:
        standard_tax = min(taxable_income, self.STANDARD_RATE_BAND) * self.STANDARD_RATE
        higher_tax = max(taxable_income - self.STANDARD_RATE_BAND, 0.0) * self.HIGHER_RATE
        return standard_tax + higher_tax

    def _usc(self, taxable_income: float) -> float:
        total = 0.0
        previous_limit = 0.0
        for band_limit, rate in self.USC_BANDS:
            taxable_at_band = max(min(taxable_income, band_limit) - previous_limit, 0.0)
            total += taxable_at_band * rate
            previous_limit = band_limit
        if taxable_income > self.USC_BANDS[-1][0]:
            total += (taxable_income - self.USC_BANDS[-1][0]) * self.USC_TOP_RATE
        return total


class LambdaResponseBuilder:
    @staticmethod
    def success(data: dict) -> dict:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data),
        }

    @staticmethod
    def error(message: str, status_code: int = 400) -> dict:
        return {
            'statusCode': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': message}),
        }


class TaxLambdaHandler:
    def __init__(self):
        self.calculator = IrelandTaxCalculator()

    def handle(self, event, context):
        path = event.get('rawPath') or event.get('path', '')
        method = event.get('requestContext', {}).get('http', {}).get('method') or event.get('httpMethod', 'GET')

        if path.endswith('/tax/health'):
            return LambdaResponseBuilder.success({'status': 'healthy', 'service': 'tax-calculator', 'version': '1.0.0'})

        if path.endswith('/tax/calculate') and method.upper() == 'POST':
            payload = json.loads(event.get('body') or '{}')
            gross_income = float(payload.get('gross_income', 0) or 0)
            deductions = float(payload.get('deductions', 0) or 0)
            tax_year = str(payload.get('tax_year', '2026'))

            if gross_income <= 0 or deductions < 0:
                return LambdaResponseBuilder.error('Invalid input. gross_income must be positive and deductions cannot be negative.')

            result = self.calculator.calculate(gross_income, deductions, tax_year)
            return LambdaResponseBuilder.success(asdict(result))

        return LambdaResponseBuilder.error('Route not found', 404)


handler_instance = TaxLambdaHandler()


def lambda_handler(event, context):
    return handler_instance.handle(event, context)
