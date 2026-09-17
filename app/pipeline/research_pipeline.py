from app.tools.web_search import fetch_page
from app.tools.composio_tools import summarize_tools


def research_app(
    app_name: str,
    category: str,
    website: str,
    documentation_url: str,
    composio_toolkit: str | None = None,
) -> dict:

    print("=" * 70)
    print(f"Researching: {app_name}")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Official documentation research
    # ---------------------------------------------------------

    print()
    print("1. Fetching official documentation...")

    docs = fetch_page(documentation_url)

    if docs["success"]:
        text = docs["text"]
        lower_text = text.lower()

        keywords = [
            "authentication",
            "oauth",
            "api",
            "rest",
            "graphql",
            "token",
            "authorization",
            "webhook",
        ]

        findings = [
            keyword
            for keyword in keywords
            if keyword.lower() in lower_text
        ]

        api_research = {
            "success": True,
            "documentation_url": documentation_url,
            "page_title": docs["title"],
            "findings": findings,
            "characters": len(text),
            "evidence_preview": text[:1000],
        }

    else:
        print()
        print("Official documentation could not be fetched.")
        print("Continuing with Composio research...")

        text = ""
        findings = []

    api_research = {
    "success": False,
    "documentation_url": documentation_url,
    "status_code": docs.get("status_code"),
    "error": docs.get("error"),
    "findings": [],
}

    # ---------------------------------------------------------
    # 2. Composio toolkit research
    # ---------------------------------------------------------

    composio_research = {
        "status": "not_checked",
        "toolkit": composio_toolkit,
        "tool_count": 0,
        "tools": [],
    }

    if composio_toolkit:

        print()
        print(f"2. Searching Composio toolkit: {composio_toolkit}")

        try:
            tools = summarize_tools(
                toolkit=composio_toolkit,
                limit=20,
            )

            if tools:
                composio_research = {
                    "status": "available",
                    "toolkit": composio_toolkit,
                    "tool_count": len(tools),
                    "tools": tools,
                }

            else:
                composio_research = {
                    "status": "not_found",
                    "toolkit": composio_toolkit,
                    "tool_count": 0,
                    "tools": [],
                }

        except Exception as exc:

            print()
            print(f"Composio lookup failed: {exc}")
            print("Retrying Composio lookup...")

            try:
                tools = summarize_tools(
                    toolkit=composio_toolkit,
                    limit=20,
                )

                if tools:
                    composio_research = {
                        "status": "available",
                        "toolkit": composio_toolkit,
                        "tool_count": len(tools),
                        "tools": tools,
                        "retry_used": True,
                    }

                else:
                    composio_research = {
                        "status": "not_found",
                        "toolkit": composio_toolkit,
                        "tool_count": 0,
                        "tools": [],
                        "retry_used": True,
                    }

            except Exception as retry_exc:

                composio_research = {
                    "status": "lookup_error",
                    "toolkit": composio_toolkit,
                    "tool_count": 0,
                    "tools": [],
                    "error": str(retry_exc),
                    "retry_error": str(retry_exc),
                }

    # ---------------------------------------------------------
    # 3. Confidence
    # ---------------------------------------------------------

    if composio_research["status"] == "available":
        confidence = "high"

    elif (
        api_research["success"]
        and composio_research["status"] == "not_found"
    ):
        confidence = "medium"

    else:
        confidence = "low"

    # ---------------------------------------------------------
    # 4. Final result
    # ---------------------------------------------------------

    return {
        "app_name": app_name,
        "category": category,
        "website": website,
        "api_research": api_research,
        "composio_research": composio_research,
        "confidence": confidence,
    }


if __name__ == "__main__":

    result = research_app(
        app_name="Salesforce",
        category="CRM",
        website="https://www.salesforce.com/",
        documentation_url="https://developer.salesforce.com/docs",
        composio_toolkit="SALESFORCE",
    )

    print()
    print()
    print("FINAL RESEARCH RESULT")
    print("=" * 70)

    print(f"Application: {result['app_name']}")
    print(f"Category: {result['category']}")
    print(f"Website: {result['website']}")
    print(f"Confidence: {result['confidence']}")

    print()
    print("API RESEARCH")
    print("-" * 70)

    api = result["api_research"]

    print(
        f"Documentation: "
        f"{api.get('documentation_url', 'Unavailable')}"
    )

    print(
        f"Page title: "
        f"{api.get('page_title', 'Unavailable')}"
    )

    print(
        f"Findings: "
        f"{api.get('findings', [])}"
    )

    print()
    print("COMPOSIO RESEARCH")
    print("-" * 70)

    composio = result["composio_research"]

    print(f"Toolkit: {composio['toolkit']}")
    print(f"Status: {composio['status']}")
    print(f"Tool count: {composio['tool_count']}")

    for tool in composio["tools"][:5]:
        print()
        print(f"Tool: {tool['slug']}")
        print(f"Description: {tool['description']}")