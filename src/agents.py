"""Agent definitions and permission model for Zava multi-agent architecture.

Defines the 6 specialized agents with their permission levels,
accessible resources, and corresponding MCP connectors.
"""

from dataclasses import dataclass, field
from enum import Enum


class PermissionLevel(Enum):
    """Agent permission classification."""
    LOW = "low"          # 🟢 Public data only
    MEDIUM = "medium"    # 🟡 Internal docs, calendar
    HIGH = "high"        # 🔴 Databases, repos, infra


class AgentCategory(Enum):
    """Agent category classification."""
    DATA = "data"            # 📊 Data Agents
    KNOWLEDGE = "knowledge"  # 📚 Knowledge Agent
    EXTERNAL = "external"    # 🌐 External Agent
    OPS = "ops"              # ⚙️ Ops Agent
    GITHUB = "github"        # 🛠️ GitHub Agent


@dataclass
class AgentDefinition:
    """Definition of a specialized agent within the Zava ecosystem."""
    name: str
    display_name: str
    category: AgentCategory
    permission: PermissionLevel
    description: str
    accessible_resources: list[str] = field(default_factory=list)
    mcp_connector: str | None = None
    demo_ids: list[int] = field(default_factory=list)

    @property
    def permission_icon(self) -> str:
        icons = {
            PermissionLevel.LOW: "🟢",
            PermissionLevel.MEDIUM: "🟡",
            PermissionLevel.HIGH: "🔴",
        }
        return icons[self.permission]

    @property
    def category_icon(self) -> str:
        icons = {
            AgentCategory.DATA: "📊",
            AgentCategory.KNOWLEDGE: "📚",
            AgentCategory.EXTERNAL: "🌐",
            AgentCategory.OPS: "⚙️",
            AgentCategory.GITHUB: "🛠️",
        }
        return icons[self.category]


# ---------------------------------------------------------------------------
# Agent Registry — all 7 agents in the system
# ---------------------------------------------------------------------------
AGENT_REGISTRY: list[AgentDefinition] = [
    AgentDefinition(
        name="inventory-agent",
        display_name="Inventory Agent",
        category=AgentCategory.DATA,
        permission=PermissionLevel.HIGH,
        description="Query cross-region inventory data from Fabric Lakehouse",
        accessible_resources=["Fabric Lakehouse (inventory)"],
        mcp_connector="fabric-mcp",
        demo_ids=[1],
    ),
    AgentDefinition(
        name="logistics-agent",
        display_name="Logistics Agent",
        category=AgentCategory.DATA,
        permission=PermissionLevel.HIGH,
        description="Track shipment status and estimated arrival time",
        accessible_resources=["Logistics DB"],
        mcp_connector="logistics-mcp",
        demo_ids=[5],
    ),
    AgentDefinition(
        name="knowledge-agent",
        display_name="Knowledge Agent",
        category=AgentCategory.KNOWLEDGE,
        permission=PermissionLevel.MEDIUM,
        description="Search SharePoint internal knowledge management docs",
        accessible_resources=["SharePoint internal docs"],
        mcp_connector="sharepoint-mcp",
        demo_ids=[2],
    ),
    AgentDefinition(
        name="search-agent",
        display_name="Search Agent",
        category=AgentCategory.EXTERNAL,
        permission=PermissionLevel.LOW,
        description="Query public information via Bing Search (weather, news)",
        accessible_resources=["Bing public search"],
        mcp_connector="bing-search-mcp",
        demo_ids=[4],
    ),
    AgentDefinition(
        name="sre-agent",
        display_name="SRE Agent",
        category=AgentCategory.OPS,
        permission=PermissionLevel.HIGH,
        description="Check Azure Monitor system health and logs",
        accessible_resources=["Azure Monitor Logs/Metrics"],
        mcp_connector="azure-monitor-mcp",
        demo_ids=[6],
    ),
    AgentDefinition(
        name="coding-agent",
        display_name="GitHub Coding Agent",
        category=AgentCategory.GITHUB,
        permission=PermissionLevel.HIGH,
        description="Analyze and fix bugs in GitHub repositories",
        accessible_resources=["GitHub Repo (write)"],
        mcp_connector=None,  # Direct GitHub access, no MCP
        demo_ids=[3],
    ),
    AgentDefinition(
        name="copilot-agent",
        display_name="GitHub Copilot",
        category=AgentCategory.GITHUB,
        permission=PermissionLevel.MEDIUM,
        description="Generate incident reports and schedule M365 meetings",
        accessible_resources=["M365 Calendar", "Incident context"],
        mcp_connector="workiq-mcp",
        demo_ids=[7, 8],
    ),
]


def get_agent(name: str) -> AgentDefinition | None:
    """Look up an agent by name."""
    for agent in AGENT_REGISTRY:
        if agent.name == name:
            return agent
    return None


def get_agents_by_category(category: AgentCategory) -> list[AgentDefinition]:
    """Get all agents in a category."""
    return [a for a in AGENT_REGISTRY if a.category == category]


def get_agents_by_permission(permission: PermissionLevel) -> list[AgentDefinition]:
    """Get all agents with a specific permission level."""
    return [a for a in AGENT_REGISTRY if a.permission == permission]


def check_permission(agent_name: str, required_level: PermissionLevel) -> bool:
    """Check if an agent has sufficient permission.

    Returns True if the agent's permission level is >= required level.
    Permission hierarchy: HIGH > MEDIUM > LOW
    """
    agent = get_agent(agent_name)
    if not agent:
        return False

    hierarchy = {
        PermissionLevel.LOW: 0,
        PermissionLevel.MEDIUM: 1,
        PermissionLevel.HIGH: 2,
    }
    return hierarchy[agent.permission] >= hierarchy[required_level]


def print_agent_registry():
    """Print a formatted table of all registered agents."""
    print("\n" + "=" * 80)
    print("🔐 Agent Permission Registry")
    print("=" * 80)
    print(f"  {'Category':<15} {'Agent':<25} {'Permission':<12} {'MCP':<20}")
    print("  " + "-" * 72)
    for agent in AGENT_REGISTRY:
        mcp = agent.mcp_connector or "(direct)"
        demos = ", ".join(f"Demo {d}" for d in agent.demo_ids)
        print(
            f"  {agent.category_icon} {agent.category.value:<12} "
            f"{agent.display_name:<25} "
            f"{agent.permission_icon} {agent.permission.value:<8} "
            f"{mcp:<20}"
        )
        print(f"  {'':>15} └─ {demos}")
    print("=" * 80)
