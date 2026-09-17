import csv
import difflib

from composio import Composio
from app.config import COMPOSIO_API_KEY


APPS_PATH = "data/app_hints.csv"
OUTPUT_PATH = "data/verified_toolkits.csv"


composio = Composio(api_key=COMPOSIO_API_KEY)


def value(obj, *names):
    for name in names:
        if isinstance(obj, dict):
            if name in obj:
                return obj[name]
        elif hasattr(obj, name):
            return getattr(obj, name)

    return ""


def get_all_toolkits():
    """Retrieve the full Composio toolkit catalog using cursors."""

    results = []
    cursor = None

    while True:

        kwargs = {
            "limit": 100,
            "sort_by": "alphabetically",
        }

        if cursor:
            kwargs["cursor"] = cursor

        response = composio.toolkits.list(**kwargs)

        items = response.items or []

        results.extend(items)

        print(
            f"Retrieved {len(items)} toolkits "
            f"(total: {len(results)})"
        )

        cursor = response.next_cursor

        if not cursor:
            break

    return results


def normalise(text):
    return (
        text.lower()
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
        .replace(".", "")
        .replace("/", "")
    )


def find_match(app_name, hinted_toolkit, catalog):

    # ---------------------------------------------------------
    # Exact toolkit slug
    # ---------------------------------------------------------

    if hinted_toolkit:

        for item in catalog:

            slug = value(
                item,
                "slug",
                "key",
                "id",
            )

            if (
                str(slug).lower()
                == hinted_toolkit.lower()
            ):
                return str(slug), "verified", "exact_slug"

    # ---------------------------------------------------------
    # Exact application name
    # ---------------------------------------------------------

    normalized_app = normalise(app_name)

    for item in catalog:

        slug = str(
            value(item, "slug", "key", "id")
            or ""
        )

        name = str(
            value(
                item,
                "name",
                "display_name",
                "label",
            )
            or ""
        )

        if (
            normalise(name) == normalized_app
            or normalise(slug) == normalized_app
        ):
            return slug, "verified", "exact_name"

    # ---------------------------------------------------------
    # Strong fuzzy match
    # ---------------------------------------------------------

    candidates = []

    for item in catalog:

        slug = str(
            value(item, "slug", "key", "id")
            or ""
        )

        name = str(
            value(
                item,
                "name",
                "display_name",
                "label",
            )
            or ""
        )

        if not slug:
            continue

        score_slug = difflib.SequenceMatcher(
            None,
            normalized_app,
            normalise(slug),
        ).ratio()

        score_name = difflib.SequenceMatcher(
            None,
            normalized_app,
            normalise(name),
        ).ratio()

        score = max(
            score_slug,
            score_name,
        )

        candidates.append(
            (score, slug)
        )

    candidates.sort(
        reverse=True
    )

    if candidates:

        score, slug = candidates[0]

        if score >= 0.85:
            return slug, "candidate", "fuzzy"

    return "", "not_found", ""


def main():

    print("=" * 70)
    print("COMPOSIO TOOLKIT DISCOVERY")
    print("=" * 70)

    print()
    print("Downloading toolkit catalog...")

    catalog_raw = get_all_toolkits()

    catalog = []

    for item in catalog_raw:

        catalog.append(
            {
                "slug": str(
                    value(
                        item,
                        "slug",
                        "key",
                        "id",
                    )
                    or ""
                ),
                "name": str(
                    value(
                        item,
                        "name",
                        "display_name",
                        "label",
                    )
                    or ""
                ),
            }
        )

    print()
    print(
        f"Total toolkit catalog entries: "
        f"{len(catalog)}"
    )

    with open(
        APPS_PATH,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        apps = list(
            csv.DictReader(file)
        )

    rows = []

    for index, app in enumerate(
        apps,
        start=1,
    ):

        app_name = app["app_name"].strip()

        hinted = app.get(
            "composio_toolkit",
            "",
        ).strip()

        toolkit, status, match_type = find_match(
            app_name,
            hinted,
            catalog,
        )

        rows.append(
            {
                "app_name": app_name,
                "category": app["category"],
                "hinted_toolkit": hinted,
                "verified_toolkit": toolkit,
                "status": status,
                "match_type": match_type,
            }
        )

        print(
            f"[{index}/100] "
            f"{app_name} -> "
            f"{status}"
            + (
                f" ({toolkit})"
                if toolkit
                else ""
            )
        )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "app_name",
                "category",
                "hinted_toolkit",
                "verified_toolkit",
                "status",
                "match_type",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 70)
    print("DISCOVERY COMPLETE")
    print("=" * 70)

    print(
        "Verified:",
        sum(
            x["status"] == "verified"
            for x in rows
        ),
    )

    print(
        "Candidates:",
        sum(
            x["status"] == "candidate"
            for x in rows
        ),
    )

    print(
        "Not found:",
        sum(
            x["status"] == "not_found"
            for x in rows
        ),
    )

    print(
        "Saved:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()