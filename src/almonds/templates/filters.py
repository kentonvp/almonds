from datetime import datetime


def format_date(s: datetime) -> str:
    return s.strftime("%Y-%m-%d %I:%M %p")


def format_currency(s: float) -> str:
    return f"${s:,.2f}".replace("$-", "-$")


def format_dollars(s: float) -> str:
    return f"${s:,.0f}".replace("$-", "-$")
