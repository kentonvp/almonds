import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from almonds.crud.category import create_category, delete_category, get_category_by_name
from almonds.models.category import Category as CategoryModel
from almonds.schemas.category import Category, CategoryBase


@pytest.fixture
def sample_category_base():
    return CategoryBase(name="Test Category")


def test_create_category(sessionmaker_test, sample_category_base):
    created_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )

    assert isinstance(created_category, Category)
    assert isinstance(created_category.id, int)
    assert created_category.name == sample_category_base.name


def test_get_category_by_name(sessionmaker_test, sample_category_base):
    created_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )

    retrieved_category = get_category_by_name(
        created_category.name, sessionmaker=sessionmaker_test
    )

    assert retrieved_category is not None
    assert retrieved_category.id == created_category.id
    assert retrieved_category.name == created_category.name


def test_get_nonexistent_category(sessionmaker_test):
    non_existent_name = "Nonexistent Category"
    retrieved_category = get_category_by_name(
        non_existent_name, sessionmaker=sessionmaker_test
    )
    assert retrieved_category is None


def test_delete_category(sessionmaker_test, sample_category_base):
    created_category = create_category(
        sample_category_base, sessionmaker=sessionmaker_test
    )

    delete_category(created_category.id, sessionmaker=sessionmaker_test)

    retrieved_category = get_category_by_name(
        created_category.name, sessionmaker=sessionmaker_test
    )
    assert retrieved_category is None


def test_delete_nonexistent_category(sessionmaker_test):
    non_existent_id = 9999  # Assuming this ID doesn't exist

    # This should not raise an exception
    delete_category(non_existent_id, sessionmaker=sessionmaker_test)
