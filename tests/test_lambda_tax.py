from lambda_tax.lambda_function import IrelandTaxCalculator


def test_tax_calculation_returns_positive_values():
    calculator = IrelandTaxCalculator()
    result = calculator.calculate(52000, 3000, '2026')

    assert result.taxable_income == 49000
    assert result.net_income > 0
    assert result.total_tax > 0
