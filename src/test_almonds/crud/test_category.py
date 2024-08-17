from uuid import uuid4

import pytest

from almonds.crud.category import (
    create_category,
    delete_category,
    get_categories_by_user,
    get_category_by_id,
    update_category,
)
from almonds.schemas.category import Category, CategoryBase


@pytest.fixture
def sample_category_base():
    return CategoryBase(name="User Category", user_id=uuid4())


def test_create_category(sessionmaker_test, sample_category_base):
    created_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )

    assert isinstance(created_category, Category)
    assert isinstance(created_category.id, int)
    assert created_category.name == sample_category_base.name


def test_get_category_by_id(sessionmaker_test, sample_category_base):
    created_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )

    retrieved_category = get_category_by_id(
        created_category.id, sessionmaker=sessionmaker_test
    )

    assert retrieved_category
    assert retrieved_category.id == created_category.id
    assert retrieved_category.user_id == created_category.user_id
    assert retrieved_category.name == created_category.name


def test_get_categories_by_user(sessionmaker_test, sample_category_base):
    # Create a user categoriy
    user_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )

    # Create a category that is not associated with any user
    create_category(
        CategoryBase(name="Other", user_id=None), sessionmaker=sessionmaker_test
    )

    # Create a category that is associated with a DIFFERENT user
    # (should not be picked up in get)
    create_category(
        CategoryBase(name="Second User Category", user_id=uuid4()),
        sessionmaker=sessionmaker_test,
    )

    retrieved_categories = get_categories_by_user(
        user_category.user_id, sessionmaker=sessionmaker_test
    )

    assert len(retrieved_categories) == 2
    assert "Other" in (category.name for category in retrieved_categories)
    assert "User Category" in (category.name for category in retrieved_categories)


def test_update_category(sessionmaker_test, sample_category_base):
    created_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )
    print(f"{created_category}")

    new_name = "New Name"
    created_category.name = new_name

    update_category(created_category, sessionmaker=sessionmaker_test)
    print(f"{created_category}")

    categories = get_categories_by_user(
        created_category.user_id, sessionmaker=sessionmaker_test
    )

    assert new_name in (c.name for c in categories), f"{categories=}"


def test_delete_category(sessionmaker_test, sample_category_base):
    created_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )

    delete_category(created_category.id, sessionmaker=sessionmaker_test)

    retrieved_category = get_categories_by_user(
        created_category.user_id, sessionmaker=sessionmaker_test
    )
    assert not retrieved_category


def test_delete_nonexistent_category(sessionmaker_test):
    non_existent_id = 9999  # Assuming this ID doesn't exist

    # This should not raise an exception
    delete_category(non_existent_id, sessionmaker=sessionmaker_test)
