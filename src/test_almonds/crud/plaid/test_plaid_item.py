from uuid import uuid4

from almonds.crud.plaid.plaid_item import (
    create_item,
    delete_item,
    get_item,
    get_items_for_user,
    update_cursor,
)
from almonds.schemas.plaid.plaid_item import PlaidItemBase


def test_create_and_get_item(sessionmaker_test):
    user_id = uuid4()
    access_token = "access-sandbox-123"
    item_id = "item_123"
    item_base = PlaidItemBase(
        user_id=user_id,
        access_token=access_token,
        item_id=item_id,
    )

    # Create
    created = create_item(item_base, sessionmaker=sessionmaker_test)
    assert created.user_id == user_id
    assert created.access_token == access_token
    assert created.item_id == item_id
    assert created.id is not None
    assert created.expired is False
    assert created.cursor is None

    # Get by id
    fetched = get_item(created.id, sessionmaker=sessionmaker_test)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.user_id == user_id
    assert fetched.access_token == access_token
    assert fetched.item_id == item_id
    assert fetched.expired is False


def test_get_items_for_user(sessionmaker_test):
    user_id = uuid4()
    other_user_id = uuid4()
    item1 = PlaidItemBase(
        user_id=user_id,
        access_token="token1",
        item_id="item_1",
    )
    item2 = PlaidItemBase(
        user_id=user_id,
        access_token="token2",
        item_id="item_2",
    )
    item3 = PlaidItemBase(
        user_id=other_user_id,
        access_token="token3",
        item_id="item_3",
    )
    create_item(item1, sessionmaker=sessionmaker_test)
    create_item(item2, sessionmaker=sessionmaker_test)
    create_item(item3, sessionmaker=sessionmaker_test)

    items = get_items_for_user(user_id, sessionmaker=sessionmaker_test)
    assert len(items) == 2
    assert all(item.user_id == user_id for item in items)
    tokens = {item.access_token for item in items}
    assert tokens == {"token1", "token2"}


def test_delete_item(sessionmaker_test):
    user_id = uuid4()
    item_base = PlaidItemBase(
        user_id=user_id,
        access_token="token_del",
        item_id="item_del",
    )
    created = create_item(item_base, sessionmaker=sessionmaker_test)
    assert get_item(created.id, sessionmaker=sessionmaker_test).expired is False

    # Delete (expire)
    delete_item(created.id, sessionmaker=sessionmaker_test)
    fetched = get_item(created.id, sessionmaker=sessionmaker_test)
    assert fetched is not None
    assert fetched.expired is True


def test_update_cursor(sessionmaker_test):
    user_id = uuid4()
    item_base = PlaidItemBase(
        user_id=user_id,
        access_token="token_cursor",
        item_id="item_cursor",
    )
    created = create_item(item_base, sessionmaker=sessionmaker_test)
    assert created.cursor is None

    # Update cursor
    new_cursor = "cursor_123"
    update_cursor(created.id, new_cursor, sessionmaker=sessionmaker_test)
    fetched = get_item(created.id, sessionmaker=sessionmaker_test)
    assert fetched is not None
    assert fetched.cursor == new_cursor
    assert fetched.synced_at is not None


def test_get_item_not_found(sessionmaker_test):
    random_id = uuid4()
    assert get_item(random_id, sessionmaker=sessionmaker_test) is None
