import csv
import json
from pathlib import Path

INPUT_PATH = Path("outputs/verified_results.json")
CSV_PATH = Path("outputs/final_audit.csv")
JSON_PATH = Path("outputs/final_audit.json")


def build_row(item):
    api = item.get("api_research", {})
    composio = item.get("composio_research", {})
    verification = item.get("verification", {})

    return {
        "app_name": item.get("app_name", ""),
        "category": item.get("category", ""),
        "website": item.get("website", ""),
        "research_status": item.get("status", ""),
        "api_source_accessible": api.get("success", False),
        "documentation_url": api.get("documentation_url", ""),
        "api_findings": ", ".join(api.get("findings", [])),
        "composio_toolkit": composio.get("toolkit", ""),
        "toolkit_mapping_status": item.get(
            "toolkit_mapping_status", ""
        ),
        "composio_status": composio.get("status", ""),
        "composio_tool_count": composio.get("tool_count", 0),
        "confidence": item.get("confidence", ""),
        "verification_status": verification.get(
            "verification_status", ""
        ),
        "verification_issues": " | ".join(
            verification.get("issues", [])
        ),
    }


def main():
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    rows = [build_row(item) for item in data]

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

    with CSV_PATH.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)

    with JSON_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("=" * 70)
    print("FINAL AUDIT GENERATED")
    print("=" * 70)
    print(f"Applications: {len(rows)}")
    print(f"CSV:  {CSV_PATH}")
    print(f"JSON: {JSON_PATH}")


if __name__ == "__main__":
    main()