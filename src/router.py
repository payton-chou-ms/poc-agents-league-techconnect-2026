"""Foundry Agent Intent Router for Zava multi-agent architecture.

Routes user intents to the appropriate specialized agent based on
keyword matching and intent classification.
"""

from dataclasses import dataclass
from enum import Enum

from src.agents import AgentDefinition, AGENT_REGISTRY, get_agent


class IntentCategory(Enum):
    """Classified user intent categories."""
    INVENTORY_QUERY = "inventory_query"        # Query inventory
    KNOWLEDGE_SEARCH = "knowledge_search"      # Search knowledge base docs
    BUG_FIX = "bug_fix"                        # Fix code bugs
    EXTERNAL_SEARCH = "external_search"        # Search weather/news
    LOGISTICS_TRACK = "logistics_track"        # Track logistics
    SYSTEM_HEALTH = "system_health"            # System health check
    INCIDENT_REPORT = "incident_report"        # Generate incident report
    MEETING_BOOKING = "meeting_booking"        # Schedule meetings
    UNKNOWN = "unknown"                        # Unclassified


@dataclass
class RoutingRule:
    """Maps intent keywords to target agent."""
    intent: IntentCategory
    agent_name: str
    keywords: list[str]
    description: str


# ---------------------------------------------------------------------------
# Routing Rules — keyword-based intent → agent mapping
# ---------------------------------------------------------------------------
ROUTING_RULES: list[RoutingRule] = [
    RoutingRule(
        intent=IntentCategory.INVENTORY_QUERY,
        agent_name="inventory-agent",
        keywords=[
            "庫存", "存貨", "缺貨", "補貨", "stock", "inventory",
            "鳳梨酥", "pineapple", "供應商", "supplier",
            "幾盒", "數量", "台灣", "日本", "美國",
        ],
        description="Query inventory status across regions",
    ),
    RoutingRule(
        intent=IntentCategory.KNOWLEDGE_SEARCH,
        agent_name="knowledge-agent",
        keywords=[
            "知識庫", "文件", "FAQ", "排解", "troubleshoot",
            "SOP", "流程", "怎麼辦", "解法", "同步",
            "knowledge", "search doc", "guide",
        ],
        description="Search internal knowledge management docs",
    ),
    RoutingRule(
        intent=IntentCategory.BUG_FIX,
        agent_name="coding-agent",
        keywords=[
            "bug", "程式碼", "修復", "fix", "error", "timeout",
            "API", "code", "issue", "PR", "pull request",
            "GitHub", "deploy", "版本",
        ],
        description="Analyze and fix code issues",
    ),
    RoutingRule(
        intent=IntentCategory.EXTERNAL_SEARCH,
        agent_name="search-agent",
        keywords=[
            "天氣", "weather", "新聞", "news", "搜尋",
            "颱風", "暴風雪", "航班", "機場",
            "Bing", "search", "查一下",
        ],
        description="Search public info (weather, news)",
    ),
    RoutingRule(
        intent=IntentCategory.LOGISTICS_TRACK,
        agent_name="logistics-agent",
        keywords=[
            "物流", "logistics", "貨運", "出貨", "運送",
            "追蹤", "tracking", "ETA", "到貨",
            "快遞", "空運", "海運",
        ],
        description="Track shipment and logistics status",
    ),
    RoutingRule(
        intent=IntentCategory.SYSTEM_HEALTH,
        agent_name="sre-agent",
        keywords=[
            "系統", "健康", "health", "監控", "monitor",
            "Azure", "日誌", "log", "metrics", "CPU",
            "記憶體", "異常", "告警", "alert",
        ],
        description="Check system health metrics",
    ),
    RoutingRule(
        intent=IntentCategory.INCIDENT_REPORT,
        agent_name="copilot-agent",
        keywords=[
            "報告", "report", "事件", "incident", "摘要",
            "summary", "整理", "紀錄",
        ],
        description="Generate incident report draft",
    ),
    RoutingRule(
        intent=IntentCategory.MEETING_BOOKING,
        agent_name="copilot-agent",
        keywords=[
            "會議", "meeting", "約", "行事曆", "calendar",
            "排程", "schedule", "開會", "Teams",
        ],
        description="Schedule follow-up meetings",
    ),
]


class FoundryRouter:
    """Foundry Agent — routes user input to specialized agents.

    Implements keyword-based intent recognition and agent dispatching.
    In production, this would use an LLM for intent classification.
    """

    def __init__(self):
        self.rules = ROUTING_RULES
        self.agents = {a.name: a for a in AGENT_REGISTRY}

    def classify_intent(self, user_input: str) -> tuple[IntentCategory, float]:
        """Classify user intent based on keyword matching.

        Returns:
            Tuple of (intent category, confidence score 0-1)
        """
        user_lower = user_input.lower()
        scores: dict[IntentCategory, int] = {}

        for rule in self.rules:
            match_count = sum(
                1 for kw in rule.keywords if kw.lower() in user_lower
            )
            if match_count > 0:
                scores[rule.intent] = match_count

        if not scores:
            return IntentCategory.UNKNOWN, 0.0

        best_intent = max(scores, key=lambda k: scores[k])
        max_keywords = max(len(r.keywords) for r in self.rules)
        confidence = min(scores[best_intent] / max_keywords * 2, 1.0)

        return best_intent, confidence

    def route(self, user_input: str) -> tuple[AgentDefinition | None, IntentCategory, float]:
        """Route user input to the appropriate agent.

        Returns:
            Tuple of (agent definition, intent, confidence)
        """
        intent, confidence = self.classify_intent(user_input)

        if intent == IntentCategory.UNKNOWN:
            return None, intent, confidence

        # Find the matching rule's agent
        for rule in self.rules:
            if rule.intent == intent:
                agent = self.agents.get(rule.agent_name)
                return agent, intent, confidence

        return None, intent, confidence

    def route_with_explanation(self, user_input: str) -> str:
        """Route and return a human-readable explanation."""
        agent, intent, confidence = self.route(user_input)

        if agent is None:
            return (
                f"⚠️ Unable to classify intent\n"
                f"  Input: {user_input}\n"
                f"  Suggestion: Please try a more specific description"
            )

        return (
            f"🔀 Routing Result\n"
            f"  Intent: {intent.value}\n"
            f"  Confidence: {confidence:.0%}\n"
            f"  Target Agent: {agent.category_icon} {agent.display_name}\n"
            f"  Permission: {agent.permission_icon} {agent.permission.value}\n"
            f"  MCP: {agent.mcp_connector or '(direct access)'}"
        )


# Module-level singleton
_router = FoundryRouter()


def route_intent(user_input: str) -> tuple[AgentDefinition | None, IntentCategory, float]:
    """Convenience function to route user input."""
    return _router.route(user_input)


def explain_routing(user_input: str) -> str:
    """Convenience function to get routing explanation."""
    return _router.route_with_explanation(user_input)
