"""Tests for src/agents.py — Agent registry & permission model."""

from src.agents import (
    AGENT_REGISTRY,
    AgentCategory,
    AgentDefinition,
    PermissionLevel,
    check_permission,
    get_agent,
    get_agents_by_category,
    get_agents_by_permission,
)


class TestAgentRegistry:
    """Agent registry structure and completeness."""

    def test_registry_has_7_agents(self):
        assert len(AGENT_REGISTRY) == 7

    def test_no_duplicate_names(self):
        names = [a.name for a in AGENT_REGISTRY]
        assert len(names) == len(set(names))

    def test_all_agents_have_required_fields(self):
        for agent in AGENT_REGISTRY:
            assert agent.name, f"Agent missing name"
            assert agent.display_name, f"{agent.name} missing display_name"
            assert isinstance(agent.category, AgentCategory)
            assert isinstance(agent.permission, PermissionLevel)
            assert agent.description, f"{agent.name} missing description"

    def test_demo_ids_cover_all_8_demos(self):
        all_demos = set()
        for agent in AGENT_REGISTRY:
            all_demos.update(agent.demo_ids)
        assert all_demos == {1, 2, 3, 4, 5, 6, 7, 8}

    def test_every_agent_has_at_least_one_demo(self):
        for agent in AGENT_REGISTRY:
            assert len(agent.demo_ids) >= 1, f"{agent.name} has no demo_ids"

    def test_mcp_connectors(self):
        """Agents with MCP should have non-empty connector; GitHub agents may have None."""
        for agent in AGENT_REGISTRY:
            if agent.category != AgentCategory.GITHUB or agent.name == "copilot-agent":
                if agent.mcp_connector is not None:
                    assert len(agent.mcp_connector) > 0
            # coding-agent has no MCP (direct GitHub access)

    def test_accessible_resources_non_empty(self):
        for agent in AGENT_REGISTRY:
            assert len(agent.accessible_resources) >= 1, (
                f"{agent.name} has no accessible_resources"
            )


class TestGetAgent:
    def test_get_existing_agent(self):
        agent = get_agent("inventory-agent")
        assert agent is not None
        assert agent.name == "inventory-agent"
        assert agent.category == AgentCategory.DATA

    def test_get_nonexistent_agent(self):
        assert get_agent("nonexistent-agent") is None

    def test_get_all_agents_by_name(self):
        for expected in AGENT_REGISTRY:
            found = get_agent(expected.name)
            assert found is not None
            assert found.name == expected.name


class TestGetAgentsByCategory:
    def test_data_agents(self):
        agents = get_agents_by_category(AgentCategory.DATA)
        names = {a.name for a in agents}
        assert "inventory-agent" in names
        assert "logistics-agent" in names
        assert len(agents) == 2

    def test_knowledge_agents(self):
        agents = get_agents_by_category(AgentCategory.KNOWLEDGE)
        assert len(agents) == 1
        assert agents[0].name == "knowledge-agent"

    def test_external_agents(self):
        agents = get_agents_by_category(AgentCategory.EXTERNAL)
        assert len(agents) == 1
        assert agents[0].name == "search-agent"

    def test_ops_agents(self):
        agents = get_agents_by_category(AgentCategory.OPS)
        assert len(agents) == 1
        assert agents[0].name == "sre-agent"

    def test_github_agents(self):
        agents = get_agents_by_category(AgentCategory.GITHUB)
        assert len(agents) == 2


class TestGetAgentsByPermission:
    def test_high_permission_agents(self):
        agents = get_agents_by_permission(PermissionLevel.HIGH)
        assert len(agents) == 4  # inventory, logistics, sre, coding
        for a in agents:
            assert a.permission == PermissionLevel.HIGH

    def test_medium_permission_agents(self):
        agents = get_agents_by_permission(PermissionLevel.MEDIUM)
        assert len(agents) == 2  # knowledge, copilot
        for a in agents:
            assert a.permission == PermissionLevel.MEDIUM

    def test_low_permission_agents(self):
        agents = get_agents_by_permission(PermissionLevel.LOW)
        assert len(agents) == 1  # search
        assert agents[0].name == "search-agent"


class TestCheckPermission:
    def test_high_can_access_high(self):
        assert check_permission("inventory-agent", PermissionLevel.HIGH) is True

    def test_high_can_access_medium(self):
        assert check_permission("inventory-agent", PermissionLevel.MEDIUM) is True

    def test_high_can_access_low(self):
        assert check_permission("inventory-agent", PermissionLevel.LOW) is True

    def test_medium_can_access_medium(self):
        assert check_permission("knowledge-agent", PermissionLevel.MEDIUM) is True

    def test_medium_can_access_low(self):
        assert check_permission("knowledge-agent", PermissionLevel.LOW) is True

    def test_medium_cannot_access_high(self):
        assert check_permission("knowledge-agent", PermissionLevel.HIGH) is False

    def test_low_cannot_access_medium(self):
        assert check_permission("search-agent", PermissionLevel.MEDIUM) is False

    def test_low_cannot_access_high(self):
        assert check_permission("search-agent", PermissionLevel.HIGH) is False

    def test_nonexistent_agent_returns_false(self):
        assert check_permission("nonexistent", PermissionLevel.LOW) is False


class TestAgentProperties:
    def test_permission_icons(self):
        agent_high = get_agent("inventory-agent")
        assert agent_high.permission_icon == "🔴"

        agent_med = get_agent("knowledge-agent")
        assert agent_med.permission_icon == "🟡"

        agent_low = get_agent("search-agent")
        assert agent_low.permission_icon == "🟢"

    def test_category_icons(self):
        agent = get_agent("inventory-agent")
        assert agent.category_icon == "📊"

        agent = get_agent("knowledge-agent")
        assert agent.category_icon == "📚"

        agent = get_agent("search-agent")
        assert agent.category_icon == "🌐"

        agent = get_agent("sre-agent")
        assert agent.category_icon == "⚙️"

        agent = get_agent("coding-agent")
        assert agent.category_icon == "🛠️"
