import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')

    TAX_API_URL = os.getenv(
        'TAX_API_URL',
        'https://ouagt7mepszmrfw47uhb3fdcly0mbgqi.lambda-url.us-east-1.on.aws/calculate'
    )
    TAX_HEALTH_URL = os.getenv(
        'TAX_HEALTH_URL',
        'https://ouagt7mepszmrfw47uhb3fdcly0mbgqi.lambda-url.us-east-1.on.aws/health'
    )

    INSURANCE_API_URL = os.getenv(
        'INSURANCE_API_URL',
        'https://dx9lk0qa66.execute-api.us-east-1.amazonaws.com/prod/premium/estimate'
    )
    LOAN_API_URL = os.getenv(
        'LOAN_API_URL',
        'https://72xiv7vsp6.execute-api.us-east-1.amazonaws.com/prod/loan/calculate'
    )
    LOAN_HEALTH_URL = os.getenv(
        'LOAN_HEALTH_URL',
        'https://72xiv7vsp6.execute-api.us-east-1.amazonaws.com/prod/loan/health'
    )

    CURRENCY_API_URL = os.getenv(
        'CURRENCY_API_URL',
        'https://api.frankfurter.app/latest?from=EUR&to=USD,INR,AUD,GBP'
    )

    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '15'))
