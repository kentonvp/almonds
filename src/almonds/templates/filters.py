from datetime import datetime, date


def format_date(s: datetime) -> str:
    return s.strftime("%Y-%m-%d %I:%M %p")


def format_currency(s: float) -> str:
    print(s)
    return f"${s:.2f}".replace("$-", "-$")
