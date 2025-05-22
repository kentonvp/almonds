from threading import Thread
from uuid import UUID

from flask import Blueprint, request, session

import almonds.crud.user as crud_user
import almonds.services.plaid.core as plaid_core
from almonds.crud.plaid import plaid_item as crud_plaid_item
from almonds.crypto.cryptograph import Cryptograph
from almonds.schemas.plaid.plaid_item import PlaidItemBase
from almonds.services import plaid_sync

plaid_bp = Blueprint("plaid", __name__)


@plaid_bp.route("/createLinkToken")
def create_link_token():
    user_id = session.get("user_id", None)
    if user_id is None:
        return {"error": "user_id not set"}

    link_token = plaid_core.create_link_token(user_id)
    return {"link_token": link_token}


@plaid_bp.route("/exchangePublicToken", methods=["GET", "POST"])
def exchange_public_token():
    if request.method != "POST":
        return {"public_token_exchange": "ERROR"}

    body = request.get_json()
    resp = plaid_core.exchange_public_token(session["user_id"], body["public_token"])

    # Encrypt the data.
    crypto = Cryptograph()

    item = PlaidItemBase(
        user_id=session["user_id"],
        access_token=crypto.encrypt(resp["access_token"]),
        item_id=crypto.encrypt(resp["item_id"]),
    )
    crud_plaid_item.create_item(item)

    # start a sync in the background
    Thread(
        target=plaid_sync.sync_user,
        args=(crud_user.get_user_by_id(session["user_id"]),),
        kwargs={"cryptograph": crypto},
        daemon=True,
    ).start()

    return {"public_token_exchange": "complete"}


@plaid_bp.route("/isConnected")
def is_account_connected():
    return {"status": "access_token" in session}


@plaid_bp.route("/unlinkAccount", methods=["DELETE"])
def delete_access_token():
    body = request.get_json()
    item_id = UUID(body["id"])
    item = crud_plaid_item.get_item(item_id)

    # validate
    if item is None:
        return {"status": "not found"}, 404

    crud_plaid_item.delete_item(item_id)

    crypto = Cryptograph()

    plaid_core.remove_item(item.user_id, crypto.decrypt(item.access_token))

    return {"status": "deleted"}
