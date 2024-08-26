def budget_color(percentage: float) -> str:
    """Return the color status of a budget based on the percentage spent."""
    if percentage > 100:
        return "danger"
    if percentage > 80:
        return "warning"
    return "success"
