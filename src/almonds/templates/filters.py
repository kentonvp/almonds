from datetime import date, datetime


def format_date(s: datetime) -> str:
    return s.strftime("%Y-%m-%d %I:%M %p")


def format_currency(s: float) -> str:
    return f"${s:.2f}".replace("$-", "-$")
