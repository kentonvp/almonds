from datetime import datetime

from almonds.templates.filters import format_currency, format_date


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
    assert format_currency(1000000.00) == "$1000000.00"

    # Test negative numbers
    assert format_currency(-10.5) == "-$10.50"
    assert format_currency(-0.01) == "-$0.01"

    # Test zero
    assert format_currency(0) == "$0.00"

    # Test rounding
    assert format_currency(10.506) == "$10.51"
    assert format_currency(10.504) == "$10.50"

    # Test large numbers
    assert format_currency(1234567.89) == "$1234567.89"
