import os

import pandas as pd

# Path to the CSV file relative to this file
CSV_PATH = os.path.join(
    os.path.dirname(__file__), "../static/almonds_plaid_transaction_map.csv"
)


def load_detailed_to_almonds_category_map():
    """
    Loads a mapping from Plaid DETAILED category to ALMONDS_CATEGORY (as int or None) using pandas.
    Returns:
        dict[str, int|None]: {DETAILED: ALMONDS_CATEGORY}
    """
    df = pd.read_csv(
        CSV_PATH, dtype={"ALMONDS_CATEGORY": pd.Int64Dtype()}, on_bad_lines="skip"
    )
    df.dropna(inplace=True)
    # zip up detailed: almonds_category into a dict
    detailed_to_almonds_category = dict(
        zip(df["DETAILED"].astype(str), df["ALMONDS_CATEGORY"].astype(int))
    )

    return detailed_to_almonds_category


# Singleton pattern: load once and reuse
PLAID_TO_ALMONDS_CATEGORY = load_detailed_to_almonds_category_map()
