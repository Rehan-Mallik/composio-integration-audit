import csv
import json
from pathlib import Path

from app.pipeline.app_loader import load_apps
from app.pipeline.research_pipeline import research_app


TOOLKIT_PATH = Path("data/verified_toolkits.csv")
HINTS_PATH = Path("data/app_hints.csv")
OUTPUT_PATH = Path("outputs/research_results.json")


def load_research_config() -> dict:

    config = {}

    with HINTS_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            app_name = row["app_name"].strip()

            config[app_name] = {
                "website": row.get("website_hint", "").strip(),
                "documentation_url": row.get(
                    "documentation_hint",
                    "",
                ).strip(),
            }

    toolkit_map = {}

    with TOOLKIT_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            toolkit_map[
                row["app_name"].strip()
            ] = {
                "toolkit": row.get(
                    "verified_toolkit",
                    "",
                ).strip(),
                "status": row.get(
                    "status",
                    "",
                ).strip(),
            }

    for app_name in config:

        mapping = toolkit_map.get(
            app_name,
            {},
        )

        config[app_name]["composio_toolkit"] = (
            mapping.get("toolkit", "")
        )

        config[app_name]["toolkit_status"] = (
            mapping.get("status", "not_found")
        )

    return config


def run_research():

    apps = load_apps()
    config = load_research_config()

    results = []

    total = len(apps)

    for index, app in enumerate(
        apps,
        start=1,
    ):

        app_name = app["app_name"]

        print()
        print("=" * 70)
        print(f"[{index}/{total}] {app_name}")
        print("=" * 70)

        app_config = config.get(
            app_name,
            {},
        )

        website = app_config.get(
            "website",
            "",
        )

        documentation_url = app_config.get(
            "documentation_url",
            "",
        )

        toolkit = app_config.get(
            "composio_toolkit",
            "",
        )

        toolkit_status = app_config.get(
            "toolkit_status",
            "not_found",
        )

        # -----------------------------------------------------
        # Missing research sources
        # -----------------------------------------------------

        if not website and not documentation_url and not toolkit:

            print(
                "No research configuration available."
            )

            results.append(
                {
                    "app_name": app_name,
                    "category": app["category"],
                    "status": "needs_discovery",
                    "toolkit_status": toolkit_status,
                }
            )

            continue

        try:

            # If no documentation URL exists, use the
            # application website when available.
            if not documentation_url:
                documentation_url = website

            result = research_app(
                app_name=app_name,
                category=app["category"],
                website=website,
                documentation_url=documentation_url,
                composio_toolkit=toolkit or None,
            )

            result["status"] = "completed"
            result["toolkit_mapping_status"] = toolkit_status

            results.append(result)

        except Exception as exc:

            print(
                f"Research error for {app_name}: {exc}"
            )

            results.append(
                {
                    "app_name": app_name,
                    "category": app["category"],
                    "status": "error",
                    "error": str(exc),
                    "toolkit_mapping_status": toolkit_status,
                }
            )

    return results


def save_results(results):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"Saved results to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":

    results = run_research()

    save_results(results)

    print()
    print("=" * 70)
    print("RESEARCH COMPLETE")
    print("=" * 70)
    print(
        f"Total results: {len(results)}"
    )