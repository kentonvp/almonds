import datetime

import yaml

if __name__ == "__main__":
    with open("default_categories.yaml") as f:
        categories = yaml.safe_load(f)

    print("Generating default categories SQL script...")

    # TODO: export to datetime with filename
    dt = datetime.datetime.now()
    with open(
        f"src/almonds/sql/default_categories_{dt.strftime('%Y%m%d_%H%M')}.sql", "w"
    ) as f:
        for category in categories:
            f.write(f"INSERT INTO categories (name) VALUES ('{category}');\n")
