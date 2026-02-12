"""Tests for src/tools.py — Copilot SDK Tool builder."""

import asyncio
import pytest

from src.skills import Skill, load_skills
from src.tools import (
    LIVE_MCP_SKILLS,
    _find_agent_for_skill,
    _make_handler,
    build_tools,
)


class TestLiveMcpSkills:
    def test_live_mcp_skills_defined(self):
        assert "workiq-meeting-booking" in LIVE_MCP_SKILLS

    def test_live_mcp_session_key(self):
        assert LIVE_MCP_SKILLS["workiq-meeting-booking"] == "workiq"


class TestFindAgentForSkill:
    def test_skill_with_demo_id(self):
        skill = Skill(name="test", description="test", demo_id=1)
        agent_name, mcp = _find_agent_for_skill(skill)
        assert agent_name == "Inventory Agent"
        assert mcp == "fabric-mcp"

    def test_skill_without_demo_id(self):
        skill = Skill(name="test", description="test", demo_id=None)
        agent_name, mcp = _find_agent_for_skill(skill)
        assert agent_name is None
        assert mcp is None

    def test_skill_with_invalid_demo_id(self):
        skill = Skill(name="test", description="test", demo_id=999)
        agent_name, mcp = _find_agent_for_skill(skill)
        assert agent_name is None
        assert mcp is None

    def test_demo_id_to_agent_mapping(self):
        """Verify all 8 demo IDs map to their expected agents."""
        expected = {
            1: ("Inventory Agent", "fabric-mcp"),
            2: ("Knowledge Agent", "sharepoint-mcp"),
            3: ("GitHub Coding Agent", None),
            4: ("Search Agent", "bing-search-mcp"),
            5: ("Logistics Agent", "logistics-mcp"),
            6: ("SRE Agent", "azure-monitor-mcp"),
            7: ("GitHub Copilot", "workiq-mcp"),
            8: ("GitHub Copilot", "workiq-mcp"),
        }
        for demo_id, (exp_agent, exp_mcp) in expected.items():
            skill = Skill(name=f"test-{demo_id}", description="", demo_id=demo_id)
            agent_name, mcp = _find_agent_for_skill(skill)
            assert agent_name == exp_agent, f"Demo {demo_id}: expected {exp_agent}, got {agent_name}"
            assert mcp == exp_mcp, f"Demo {demo_id}: expected {exp_mcp}, got {mcp}"


class TestBuildTools:
    def test_build_tools_count(self, all_skills, all_tools):
        """Should build 7 tools (8 skills minus 1 live MCP skip)."""
        assert len(all_tools) == len(all_skills) - len(LIVE_MCP_SKILLS)

    def test_live_mcp_skill_skipped(self, all_tools):
        tool_names = {t.name for t in all_tools}
        for live_name in LIVE_MCP_SKILLS:
            assert live_name not in tool_names, (
                f"Live MCP skill '{live_name}' should be skipped"
            )

    def test_tool_has_name(self, all_tools):
        for tool in all_tools:
            assert tool.name and len(tool.name) > 0

    def test_tool_has_description(self, all_tools):
        for tool in all_tools:
            assert tool.description and len(tool.description) > 0

    def test_tool_has_query_parameter(self, all_tools):
        for tool in all_tools:
            props = tool.parameters.get("properties", {})
            assert "query" in props, f"Tool '{tool.name}' missing 'query' parameter"
            assert props["query"]["type"] == "string"

    def test_tool_parameters_required(self, all_tools):
        for tool in all_tools:
            required = tool.parameters.get("required", [])
            assert "query" in required, f"Tool '{tool.name}': 'query' not required"


class TestMakeHandler:
    @pytest.mark.asyncio
    async def test_static_handler_returns_dict(self):
        skill = Skill(
            name="test-skill",
            description="Test",
            response_content="Sample response",
            demo_id=1,
        )
        handler = _make_handler(skill)
        result = await handler({"query": "test query"})
        assert isinstance(result, dict)
        assert "textResultForLlm" in result
        assert result["resultType"] == "success"
        assert result["textResultForLlm"] == "Sample response"

    @pytest.mark.asyncio
    async def test_live_mcp_handler_returns_redirect(self):
        skill = Skill(
            name="workiq-meeting-booking",
            description="Test live MCP",
            response_content="Static fallback",
            demo_id=8,
        )
        handler = _make_handler(skill)
        result = await handler({"query": "book a meeting"})
        assert isinstance(result, dict)
        assert "MUST use" in result["textResultForLlm"]
        assert "workiq" in result["textResultForLlm"]
        assert "live" in result.get("sessionLog", "").lower() or "MCP" in result.get("sessionLog", "")
