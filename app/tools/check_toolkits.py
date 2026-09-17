import csv

from app.tools.composio_tools import summarize_tools


INPUT_PATH = "data/app_hints.csv"


def load_hints():
    with open(INPUT_PATH, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main():
    apps = load_hints()

    print("=" * 70)
    print("COMPOSIO TOOLKIT DISCOVERY TEST")
    print("=" * 70)

    available = 0
    not_found = 0
    errors = 0

    for index, app in enumerate(apps, start=1):
        name = app["app_name"]
        toolkit = app["composio_toolkit"].strip()

        print()
        print(f"[{index}/100] {name}")

        if not toolkit:
            print("  Toolkit: not specified")
            continue

        print(f"  Toolkit: {toolkit}")

        try:
            tools = summarize_tools(
                toolkit=toolkit,
                limit=1,
            )

            if tools:
                print("  Status: AVAILABLE")
                print(f"  Example tool: {tools[0]['slug']}")
                available += 1
            else:
                print("  Status: NOT FOUND")
                not_found += 1

        except Exception as exc:
            print("  Status: ERROR")
            print(f"  Error: {exc}")
            errors += 1

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Available: {available}")
    print(f"Not found: {not_found}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    main()