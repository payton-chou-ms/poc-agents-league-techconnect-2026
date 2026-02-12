"""Convert loaded Skills into Copilot SDK Tool objects."""

from copilot import Tool

from src.skills import Skill
from src.agents import AGENT_REGISTRY
from src.inventory_data import generate_inventory_report


def _find_agent_for_skill(skill: Skill):
    """Find the agent and MCP connector associated with a skill's demo_id."""
    if skill.demo_id is None:
        return None, None
    for agent in AGENT_REGISTRY:
        if skill.demo_id in agent.demo_ids:
            return agent.display_name, agent.mcp_connector
    return None, None


# Skills that should be skipped because they are handled by a live MCP server.
# Maps skill name → session MCP server key.
# These skills won't be registered as tools; the model calls the MCP directly.
LIVE_MCP_SKILLS: dict[str, str] = {
    "workiq-meeting-booking": "workiq",  # demo8 → real WorkIQ MCP
    # Add more as you wire up real MCP servers, e.g.:
    # "github-bugfix-agent": "github",
}


def _make_handler(skill: Skill):
    """Create a tool handler that returns the skill's response content.

    If the skill is backed by a live MCP server, the handler instructs the
    model to call the real MCP tools instead of returning static text.
    """

    agent_name, mcp_connector = _find_agent_for_skill(skill)
    use_live_mcp = skill.name in LIVE_MCP_SKILLS
    use_live_csv = skill.name == "fabric-inventory-query"

    async def handler(invocation):
        # === Logging: Skill / Agent / MCP ===
        print(f"\n{'─' * 50}")
        print(f"📋 [SKILL] {skill.name}")
        print(f"   Description: {skill.description[:80]}")
        if agent_name:
            print(f"🤖 [AGENT] {agent_name}")
        else:
            print(f"🤖 [AGENT] (no agent mapped)")
        if mcp_connector:
            live_tag = " (LIVE ✅)" if use_live_mcp else " (static)"
            print(f"🔌 [MCP]   {mcp_connector}{live_tag}")
        else:
            print(f"🔌 [MCP]   (none / direct)")
        if use_live_csv:
            print(f"📂 [DATA]  Live CSV from data/inventory/")
        print(f"{'─' * 50}")

        if use_live_mcp:
            session_key = LIVE_MCP_SKILLS[skill.name]
            query = invocation.get("query", "") if isinstance(invocation, dict) else ""
            return {
                "textResultForLlm": (
                    f"User's query: {query}\n\n"
                    f"You MUST use the '{session_key}' MCP server tools to fulfill this request with real live data. "
                    f"Do NOT use any cached, sample, or static data. "
                    f"Call the MCP tools directly and return the actual results to the user."
                ),
                "resultType": "success",
                "sessionLog": f"Skill '{skill.name}' → live MCP '{session_key}'",
            }

        # Live CSV data for inventory skill
        if use_live_csv:
            try:
                report = generate_inventory_report()
                return {
                    "textResultForLlm": report,
                    "resultType": "success",
                    "sessionLog": f"Skill '{skill.name}' → live CSV data from data/inventory/",
                }
            except Exception as e:
                print(f"   ⚠️ [CSV ERROR] {e} — falling back to static response")
                # Fall through to static response below

        return {
            "textResultForLlm": skill.response_content,
            "resultType": "success",
            "sessionLog": f"Executed skill: {skill.name}",
        }

    return handler


def build_tools(skills: list[Skill]) -> list[Tool]:
    """Build a list of Copilot SDK Tool objects from loaded skills.

    Skills backed by a live MCP connector are SKIPPED — the model will
    call the real MCP server tools directly instead of going through a
    static skill handler.

    Each remaining skill becomes a tool with:
    - name: the skill's name from YAML frontmatter
    - description: skill description + trigger keywords
    - parameters: a single 'query' string (user's question context)
    - handler: returns the skill's static response as textResultForLlm
    """
    tools: list[Tool] = []

    for skill in skills:
        # Skip skills that are wired to a live MCP — let the model
        # route those queries to the real MCP tools directly.
        if skill.name in LIVE_MCP_SKILLS:
            print(f"  ⏭️  Skipped skill '{skill.name}' → routed to live MCP '{LIVE_MCP_SKILLS[skill.name]}'")
            continue

        trigger_text = ", ".join(skill.triggers) if skill.triggers else ""
        description = skill.description
        if trigger_text:
            description += f"\nTrigger keywords: {trigger_text}"

        tool = Tool(
            name=skill.name,
            description=description,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's query text",
                    },
                },
                "required": ["query"],
            },
            handler=_make_handler(skill),
        )
        tools.append(tool)

    return tools
