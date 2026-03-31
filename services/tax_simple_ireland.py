class SimpleIrelandTaxCalculator:

    def calculate(self, gross, deductions):
        gross = float(gross or 0)
        deductions = float(deductions or 0)

        taxable_income = max(gross - deductions, 0)

        if taxable_income <= 44000:
            income_tax = taxable_income * 0.20
            marginal_rate = 20
        else:
            income_tax = (44000 * 0.20) + ((taxable_income - 44000) * 0.40)
            marginal_rate = 40

        tax_credit = 4000
        income_tax = max(income_tax - tax_credit, 0)

        usc = 0

        if gross > 13000:
            if gross <= 12012:
                usc = gross * 0.005
            elif gross <= 27382:
                usc = (12012 * 0.005) + ((gross - 12012) * 0.02)
            elif gross <= 70044:
                usc = (
                    (12012 * 0.005)
                    + ((27382 - 12012) * 0.02)
                    + ((gross - 27382) * 0.045)
                )
            else:
                usc = (
                    (12012 * 0.005)
                    + ((27382 - 12012) * 0.02)
                    + ((70044 - 27382) * 0.045)
                    + ((gross - 70044) * 0.08)
                )

        prsi = gross * 0.04 if gross > 18304 else 0

        total_tax = income_tax + usc + prsi
        net_income = gross - total_tax

        effective_rate = (total_tax / gross * 100) if gross > 0 else 0

        return {
            "gross_income": round(gross, 2),
            "taxable_income": round(taxable_income, 2),

            "income_tax": round(income_tax, 2),
            "usc": round(usc, 2),
            "prsi": round(prsi, 2),

            "total_tax": round(total_tax, 2),
            "net_income": round(net_income, 2),

            "marginal_rate": marginal_rate,      # 20% or 40%
            "effective_rate": round(effective_rate, 2)
        }