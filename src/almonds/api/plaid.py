import os

from flask import Blueprint, request, session, url_for

from almonds.services.plaid import core

plaid_bp = Blueprint("plaid", __name__)


@plaid_bp.route("/createLinkToken")
def create_link_token():
    link_token = core.create_link_token()
    return {"link_token": link_token}


@plaid_bp.route("/exchangePublicToken", methods=["GET", "POST"])
def exchange_public_token():
    if request.method != "POST":
        return {"public_token_exchange": "ERROR"}

    body = request.get_json()
    resp = core.exchange_public_token(body["public_token"])

    # Store to session cookie
    session["access_token"] = resp["access_token"]
    session["item_id"] = resp["item_id"]

    return {"public_token_exchange": "complete"}


@plaid_bp.route("/isConnected")
def is_account_connected():
    return {"status": "access_token" in session}
