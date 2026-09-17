from composio import Composio

from app.config import COMPOSIO_API_KEY


def get_toolkit_tools(
    toolkit: str,
    limit: int = 20,
) -> list:
    """
    Retrieve available Composio tools for a toolkit.
    """

    composio = Composio(
        api_key=COMPOSIO_API_KEY
    )

    tools = composio.tools.get_raw_composio_tools(
        toolkits=[toolkit],
        limit=limit,
    )

    return tools


def summarize_tools(
    toolkit: str,
    limit: int = 20,
) -> list[dict]:
    """
    Convert Composio tool objects into simple dictionaries.
    """

    tools = get_toolkit_tools(
        toolkit=toolkit,
        limit=limit,
    )

    results = []

    for tool in tools:
        results.append(
            {
                "slug": tool.slug,
                "description": tool.description,
            }
        )

    return results


if __name__ == "__main__":

    tools = summarize_tools(
        toolkit="GITHUB",
        limit=10,
    )

    print(f"Found {len(tools)} Composio tools.")
    print()

    for tool in tools:
        print(f"Tool: {tool['slug']}")
        print(f"Description: {tool['description']}")
        print("-" * 60)
