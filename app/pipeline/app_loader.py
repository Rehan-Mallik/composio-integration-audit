import csv
from pathlib import Path


DATASET_PATH = Path("data/apps.csv")


def load_apps() -> list[dict]:
    """
    Load all applications from the assignment CSV.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        apps = []

        for row in reader:
            apps.append(
                {
                    "app_name": row["app_name"].strip(),
                    "category": row["category"].strip(),
                }
            )

    return apps


if __name__ == "__main__":

    apps = load_apps()

    print(f"Loaded {len(apps)} applications.")
    print()

    for index, app in enumerate(apps[:10], start=1):
        print(
            f"{index}. "
            f"{app['app_name']} "
            f"({app['category']})"
        )

    if len(apps) > 10:
        print("...")
        print()
        print(
            f"Last application: "
            f"{apps[-1]['app_name']}"
        )
