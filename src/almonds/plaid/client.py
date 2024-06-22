import os

import plaid
from plaid.api import plaid_api

configuration = plaid.Configuration(
    host=(
        plaid.Environment.Sandbox
        if os.getenv("PLAID_ENV", "sandbox") != "production"
        else plaid.Environment.Production
    ),
    api_key={
        "clientId": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
