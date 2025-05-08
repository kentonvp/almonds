from datetime import datetime

from almonds.templates.filters import format_currency, format_date, format_dollars


def test_format_date():
    # Test with a specific datetime
    dt = datetime(2023, 5, 15, 14, 30, 0)
    assert format_date(dt) == "2023-05-15 02:30 PM"

    # Test with midnight
    dt_midnight = datetime(2023, 5, 15, 0, 0, 0)
    assert format_date(dt_midnight) == "2023-05-15 12:00 AM"

    # Test with noon
    dt_noon = datetime(2023, 5, 15, 12, 0, 0)
    assert format_date(dt_noon) == "2023-05-15 12:00 PM"


def test_format_currency():
    # Test positive numbers
    assert format_currency(10.5) == "$10.50"
    assert format_currency(0.01) == "$0.01"
    assert format_currency(1000000.00) == "$1,000,000.00"
    assert format_currency(-1000000.00) == "-$1,000,000.00"

    # Test negative numbers
    assert format_currency(-10.5) == "-$10.50"
    assert format_currency(-0.01) == "-$0.01"

    # Test zero
    assert format_currency(0) == "$0.00"

    # Test rounding
    assert format_currency(10.506) == "$10.51"
    assert format_currency(10.504) == "$10.50"

    # Test large numbers
    assert format_currency(1234567.89) == "$1,234,567.89"
    assert format_currency(-1234567.89) == "-$1,234,567.89"


def test_format_dollars():
    # Test positive numbers
    assert format_dollars(10.5) == "$10"
    assert format_dollars(0.01) == "$0"
    assert format_dollars(1000000.00) == "$1,000,000"
    assert format_dollars(-1000000.00) == "-$1,000,000"

    # Test negative numbers
    assert format_dollars(-10.5) == "-$10"
    assert format_dollars(-0.01) == "-$0"

    # Test zero
    assert format_dollars(0) == "$0"

    # Test rounding
    assert format_dollars(10.506) == "$11"
    assert format_dollars(10.504) == "$11"

    # Test large numbers
    assert format_dollars(1234567.89) == "$1,234,568"
    assert format_dollars(-1234567.89) == "-$1,234,568"
