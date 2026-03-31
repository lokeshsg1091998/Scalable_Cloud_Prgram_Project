import boto3
import uuid
import requests
from decimal import Decimal
from datetime import datetime
from flask import Flask, request, jsonify, render_template

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("finance-records")

application = Flask(__name__)

LOAN_API = "https://72xiv7vsp6.execute-api.us-east-1.amazonaws.com/prod"
TAX_API = "https://ouagt7mepszmrfw47uhb3fdcly0mbgqi.lambda-url.us-east-1.on.aws"
INSURANCE_API = "https://dx9lk0qa66.execute-api.us-east-1.amazonaws.com/prod/premium/estimate"

def convert_to_decimal(obj):
    if isinstance(obj, list):
        return [convert_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    return obj


def convert_decimal_to_float(obj):
    if isinstance(obj, list):
        return [convert_decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj


@application.route("/")
def home():
    return render_template("index.html")

@application.route("/tax-page")
def tax_page():
    return render_template("tax.html")

@application.route("/insurance-page")
def insurance_page():
    return render_template("insurance.html")

@application.route("/loan-page")
def loan_page():
    return render_template("loan.html")

@application.route("/tax", methods=["POST"])
def tax():
    try:
        response = requests.post(
            f"{TAX_API}/calculate",
            json=request.json,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        result = response.json()

        table.put_item(
            Item={
                "id": str(uuid.uuid4()),
                "type": "tax",
                "summary": "Tax calculation",
                "created_at": datetime.utcnow().strftime("%d-%b-%Y %H:%M"),
                "input": convert_to_decimal(request.json),
                "output": convert_to_decimal(result)
            }
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route("/loan", methods=["POST"])
def loan():
    try:
        response = requests.post(
            f"{LOAN_API}/loan/calculate",
            json=request.json,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        data = response.json()
        data.pop("input", None)

        table.put_item(
            Item={
                "id": str(uuid.uuid4()),
                "type": "loan",
                "summary": "Loan EMI calculation",
                "created_at": datetime.utcnow().strftime("%d-%b-%Y %H:%M"),
                "input": convert_to_decimal(request.json),
                "output": convert_to_decimal(data)
            }
        )

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route("/insurance", methods=["POST"])
def insurance():
    try:
        d = request.json

        payload = {
            "age": int(d["age"]),
            "termYears": int(d["term_years"]),
            "sumAssured": float(d["sum_assured"]),
            "smoker": d["smoker"] == "Yes",
            "gender": d["gender"].lower(),
            "paymentFrequency": d["payment_frequency"].lower(),
            "currency": "EUR"
        }

        response = requests.post(
            INSURANCE_API,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        r = response.json()

        result = {
            "premium": r.get("premium"),
            "currency": r.get("currency", "EUR"),
            "frequency": r.get("frequency")
        }

        table.put_item(
            Item={
                "id": str(uuid.uuid4()),
                "type": "insurance",
                "summary": "Insurance premium estimation",
                "created_at": datetime.utcnow().strftime("%d-%b-%Y %H:%M"),
                "input": convert_to_decimal(d),
                "output": convert_to_decimal(result)
            }
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route("/tax/convert", methods=["POST"])
def convert():
    try:
        d = request.json

        if not d or "net_income" not in d or "currency" not in d:
            return jsonify({"error": "Missing net_income or currency"}), 400

        amount = float(d["net_income"])
        currency = d["currency"].strip().upper()

        res = requests.get(
            "https://api.exchangerate-api.com/v4/latest/EUR",
            timeout=10
        )

        if res.status_code != 200:
            return jsonify({"error": "Exchange rate service unavailable"}), 500

        data = res.json()
        rates = data.get("rates", {})

        if currency not in rates:
            return jsonify({"error": f"{currency} not supported"}), 400

        converted = amount * rates[currency]

        return jsonify({
            "converted": round(converted, 2),
            "currency": currency
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@application.route("/history")
def history():
    try:
        response = table.scan()
        items = response.get("Items", [])

        items = convert_decimal_to_float(items)
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return jsonify(items)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8080)