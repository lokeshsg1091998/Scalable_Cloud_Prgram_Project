console.log("APP JS LOADED");

let netIncome = 0;

function formDataToJson(form) {
    const data = new FormData(form);
    const obj = Object.fromEntries(data.entries());

    Object.keys(obj).forEach(k => {
        if (!isNaN(obj[k]) && obj[k] !== "") obj[k] = Number(obj[k]);
    });

    return obj;
}

function currency(value, code = "EUR") {
    const localeMap = {
        EUR: "en-IE",
        USD: "en-US",
        GBP: "en-GB",
        INR: "en-IN",
        AUD: "en-AU",
        CAD: "en-CA"
    };

    return new Intl.NumberFormat(localeMap[code] || "en-US", {
        style: "currency",
        currency: code,
        maximumFractionDigits: 2
    }).format(value || 0);
}

const taxForm = document.getElementById("tax-form");

if (taxForm) {
    taxForm.onsubmit = async (e) => {
        e.preventDefault();

        const resultBox = document.getElementById("tax-result");
        resultBox.innerHTML = `<div class="metric"><span>⏳ Processing...</span></div>`;

        try {
            const res = await fetch("/tax", {
                method: "POST",
                body: JSON.stringify(formDataToJson(e.target)),
                headers: { "Content-Type": "application/json" }
            });

            const d = await res.json();

            if (d.error) {
                resultBox.innerHTML = `<div class="metric"><span>${d.error}</span></div>`;
                return;
            }

            netIncome = d.net_income;

            resultBox.innerHTML = `
                <div class="metric"><span>Income Tax</span><strong>${currency(d.income_tax)}</strong></div>
                <div class="metric"><span>USC</span><strong>${currency(d.usc)}</strong></div>
                <div class="metric"><span>PRSI</span><strong>${currency(d.prsi)}</strong></div>
                <div class="metric"><span>Net Income</span><strong>${currency(d.net_income)}</strong></div>
            `;

        } catch (err) {
            resultBox.innerHTML = `<div class="metric"><span>Error connecting to tax service</span></div>`;
        }
    };
}

const countrySelect = document.getElementById("country-select");

if (countrySelect) {
    countrySelect.onchange = async function () {
        const resultBox = document.getElementById("comparison-result");

        const incomeInput = document.getElementById("gross");
        const baseIncome = netIncome || Number(incomeInput?.value);

        if (!baseIncome) {
            resultBox.innerHTML = `<div class="metric"><span>Enter income first</span></div>`;
            return;
        }

        resultBox.innerHTML = `<div class="metric"><span>⏳ Processing...</span></div>`;

        try {
            const res = await fetch("/tax/convert", {
                method: "POST",
                body: JSON.stringify({
                    net_income: baseIncome,
                    currency: this.value
                }),
                headers: { "Content-Type": "application/json" }
            });

            const d = await res.json();

            if (d.error) {
                resultBox.innerHTML = `<div class="metric"><span>${d.error}</span></div>`;
                return;
            }

            resultBox.innerHTML = `
                <div class="metric">
                    <span>💶 Net Income (EUR)</span>
                    <strong>${currency(baseIncome, "EUR")}</strong>
                </div>
                <div class="metric">
                    <span>💱 Equivalent Income (${d.currency})</span>
                    <strong>${currency(d.converted, d.currency)}</strong>
                </div>
            `;

        } catch (err) {
            resultBox.innerHTML = `<div class="metric"><span>Error converting currency</span></div>`;
        }
    };
}

const insuranceForm = document.getElementById("insurance-form");

if (insuranceForm) {
    insuranceForm.onsubmit = async (e) => {
        e.preventDefault();

        const resultBox = document.getElementById("insurance-result");
        resultBox.innerHTML = `<div class="metric"><span>⏳ Processing...</span></div>`;

        try {
            const res = await fetch("/insurance", {
                method: "POST",
                body: JSON.stringify(formDataToJson(e.target)),
                headers: { "Content-Type": "application/json" }
            });

            const d = await res.json();

            if (d.error) {
                resultBox.innerHTML = `<div class="metric"><span>${d.error}</span></div>`;
                return;
            }

            resultBox.innerHTML = `
                <div class="metric"><span>Premium</span><strong>${currency(d.premium)}</strong></div>
                <div class="metric"><span>Frequency</span><strong>${d.frequency}</strong></div>
                <div class="metric"><span>Coverage</span><strong>${currency(e.target.sum_assured.value)}</strong></div>
            `;

        } catch (err) {
            resultBox.innerHTML = `<div class="metric"><span>Error connecting to insurance service</span></div>`;
        }
    };
}

const loanForm = document.getElementById("loan-form");

if (loanForm) {
    loanForm.onsubmit = async (e) => {
        e.preventDefault();

        const resultBox = document.getElementById("loan-result");
        resultBox.innerHTML = `<div class="metric"><span>⏳ Processing...</span></div>`;

        try {
            const res = await fetch("/loan", {
                method: "POST",
                body: JSON.stringify(formDataToJson(e.target)),
                headers: { "Content-Type": "application/json" }
            });

            const d = await res.json();

            if (d.error || !d || d.emi === undefined) {
                resultBox.innerHTML = `<div class="metric"><span>❌ Unable to calculate loan</span></div>`;
                return;
            }

            resultBox.innerHTML = `
                <div class="metric"><span>Monthly EMI</span><strong>${currency(d.emi)}</strong></div>
                <div class="metric"><span>Total Repayment</span><strong>${currency(d.total_payment)}</strong></div>
                <div class="metric"><span>Total Interest</span><strong>${currency(d.total_interest)}</strong></div>
            `;

        } catch (err) {
            resultBox.innerHTML = `<div class="metric"><span>Error connecting to loan service</span></div>`;
        }
    };
}