from app.models.schemas import AppResearch


RESEARCHER_SYSTEM_PROMPT = """
You are an AI Product Operations Research Agent.

Your task is to investigate software applications for potential
agent and tool integrations.

For each application determine:

1. Whether an API exists.
2. The official API documentation URL.
3. Authentication methods.
4. API access requirements.
5. Important API capabilities.
6. MCP availability.
7. Potential integration blockers.
8. Toolkit feasibility.

Research rules:

- Prefer official documentation and developer portals.
- Do not infer API availability from a marketing website.
- Do not invent capabilities.
- Every important factual claim should have evidence.
- Clearly distinguish facts from inference.
- If evidence is insufficient, say so.
- Prefer primary sources over third-party sources.
- Return structured information.
"""


def build_research_request(
    app_name: str,
    category: str,
) -> str:
    """
    Build the research request for a single application.
    """

    return f"""
Research the following application:

Application: {app_name}
Category: {category}

Investigate its API, authentication, API access requirements,
important capabilities, MCP availability, and potential
integration blockers.

Use authoritative sources whenever possible.

Return evidence for important claims.
"""


def validate_research_result(
    result: AppResearch,
) -> bool:
    """
    Basic validation for a research result.
    """

    if not result.app_name:
        return False

    if not result.category:
        return False

    if not result.website:
        return False

    if result.api_available and not result.api_documentation_url:
        return False

    return True
