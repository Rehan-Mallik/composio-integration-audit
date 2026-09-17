import json
from pathlib import Path


INPUT_PATH = Path("outputs/research_results.json")
TOOLKIT_PATH = Path("data/verified_toolkits.csv")

OUTPUT_PATH = Path("outputs/verified_results.json")


def verify_result(result: dict) -> dict:

    verification = {
        "verification_status": "verified",
        "issues": [],
        "checks": {},
    }

    # ---------------------------------------------------------
    # Basic identity
    # ---------------------------------------------------------

    required_fields = [
        "app_name",
        "category",
        "website",
    ]

    for field in required_fields:

        if not result.get(field):

            verification["issues"].append(
                f"Missing field: {field}"
            )

    verification["checks"]["identity"] = (
        len(verification["issues"]) == 0
    )

    # ---------------------------------------------------------
    # API research
    # ---------------------------------------------------------

    api = result.get(
        "api_research",
        {},
    )

    if api.get("success"):

        verification["checks"][
            "api_source_accessible"
        ] = True

    else:

        verification["checks"][
            "api_source_accessible"
        ] = False

        verification["issues"].append(
            "Official documentation could not be accessed."
        )

    # ---------------------------------------------------------
    # Composio research
    # ---------------------------------------------------------

    composio = result.get(
        "composio_research",
        {},
    )

    composio_status = composio.get(
        "status"
    )

    if composio_status == "available":

        tool_count = composio.get(
            "tool_count",
            0,
        )

        if tool_count > 0:

            verification["checks"][
                "composio_tools_found"
            ] = True

        else:

            verification["checks"][
                "composio_tools_found"
            ] = False

            verification["issues"].append(
                "Composio toolkit reported available "
                "but no tools were returned."
            )

    elif composio_status == "not_found":

        verification["checks"][
            "composio_tools_found"
        ] = False

        verification["issues"].append(
            "No Composio toolkit was found for "
            "the supplied toolkit identifier."
        )

    elif composio_status == "lookup_error":

        verification["checks"][
            "composio_tools_found"
        ] = False

        verification["issues"].append(
            "Composio toolkit lookup failed."
        )

    else:

        verification["checks"][
            "composio_tools_found"
        ] = False

        verification["issues"].append(
            "Composio toolkit was not checked."
        )

    # ---------------------------------------------------------
    # Confidence validation
    # ---------------------------------------------------------

    confidence = result.get(
        "confidence"
    )

    if confidence == "low":

        verification["issues"].append(
            "Research confidence is low."
        )

    # ---------------------------------------------------------
    # Final verification status
    # ---------------------------------------------------------

    if not verification["issues"]:

        verification["verification_status"] = (
            "verified"
        )

    elif (
        composio_status == "available"
        and confidence == "high"
    ):

        verification["verification_status"] = (
            "verified_with_source_limitation"
        )

    else:

        verification["verification_status"] = (
            "needs_review"
        )

    result["verification"] = verification

    return result


def main():

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"Research results not found: "
            f"{INPUT_PATH}"
        )

    with INPUT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        results = json.load(file)

    verified_results = []

    for result in results:

        verified = verify_result(
            result
        )

        verified_results.append(
            verified
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            verified_results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    from collections import Counter

    statuses = Counter(
        x["verification"][
            "verification_status"
        ]
        for x in verified_results
    )

    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)

    print(
        f"Total applications: "
        f"{len(verified_results)}"
    )

    for status, count in statuses.items():

        print(
            f"{status}: {count}"
        )

    print()
    print(
        f"Saved: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()