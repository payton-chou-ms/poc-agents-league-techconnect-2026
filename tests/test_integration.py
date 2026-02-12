"""Integration tests — end-to-end validation across multiple modules.

Tests the full pipeline: router → agent → skill → tool, and verifies
consistency between the system prompt, agents, skills, and routing rules.
"""

import pytest
from pathlib import Path

from src.agents import AGENT_REGISTRY, get_agent, AgentCategory, PermissionLevel
from src.router import (
    FoundryRouter,
    IntentCategory,
    ROUTING_RULES,
    route_intent,
)
from src.skills import load_skills
from src.prompts import SYSTEM_MESSAGE


# ---------------------------------------------------------------------------
# Router → Agent Pipeline
# ---------------------------------------------------------------------------

class TestRouterToAgent:
    """Verify every routing rule maps to a valid registered agent."""

    def test_all_routing_rules_map_to_registered_agent(self):
        agent_names = {a.name for a in AGENT_REGISTRY}
        for rule in ROUTING_RULES:
            assert rule.agent_name in agent_names, (
                f"Routing rule for {rule.intent.value} references "
                f"unknown agent '{rule.agent_name}'"
            )

    def test_every_intent_has_routing_rule(self):
        mapped_intents = {r.intent for r in ROUTING_RULES}
        for intent in IntentCategory:
            if intent == IntentCategory.UNKNOWN:
                continue
            assert intent in mapped_intents, (
                f"IntentCategory.{intent.name} has no routing rule"
            )

    def test_route_returns_correct_agent_for_each_rule(self):
        router = FoundryRouter()
        for rule in ROUTING_RULES:
            # Use the first English keyword to trigger routing
            english_kws = [kw for kw in rule.keywords if kw.isascii()]
            if not english_kws:
                continue
            test_input = english_kws[0]
            agent, intent, conf = router.route(test_input)
            assert agent is not None, (
                f"Route returned None for keyword '{test_input}' "
                f"(expected agent '{rule.agent_name}')"
            )
            assert agent.name == rule.agent_name, (
                f"Route for '{test_input}' returned agent '{agent.name}', "
                f"expected '{rule.agent_name}'"
            )


# ---------------------------------------------------------------------------
# Skill → Agent Mapping
# ---------------------------------------------------------------------------

class TestSkillAgentMapping:
    """Verify demo_ids in skills correspond to agents correctly."""

    def test_every_skill_demo_id_maps_to_agent(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        all_demo_ids = set()
        for agent in AGENT_REGISTRY:
            all_demo_ids.update(agent.demo_ids)

        for skill in skills:
            if skill.demo_id is not None:
                assert skill.demo_id in all_demo_ids, (
                    f"Skill '{skill.name}' has demo_id={skill.demo_id} "
                    f"which is not claimed by any agent"
                )

    def test_expected_skill_count(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        assert len(skills) == 8, f"Expected 8 skills, got {len(skills)}"

    def test_demo_ids_cover_1_to_8(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        demo_ids = {s.demo_id for s in skills}
        expected = set(range(1, 9))
        assert demo_ids == expected, (
            f"Missing demo_ids: {expected - demo_ids}"
        )


# ---------------------------------------------------------------------------
# System Prompt Consistency
# ---------------------------------------------------------------------------

class TestSystemPromptConsistency:
    """Verify the system prompt references match actual project definitions."""

    def test_system_prompt_references_all_skill_names(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        for skill in skills:
            assert skill.name in SYSTEM_MESSAGE, (
                f"Skill '{skill.name}' is not mentioned in SYSTEM_MESSAGE"
            )

    def test_system_prompt_mentions_permission_system(self):
        assert "Permission" in SYSTEM_MESSAGE or "permission" in SYSTEM_MESSAGE

    def test_system_prompt_mentions_mcp(self):
        assert "MCP" in SYSTEM_MESSAGE

    def test_system_prompt_mentions_workiq(self):
        assert "WorkIQ" in SYSTEM_MESSAGE or "workiq" in SYSTEM_MESSAGE

    def test_system_prompt_language_is_english(self):
        assert "respond in English" in SYSTEM_MESSAGE or "English" in SYSTEM_MESSAGE


# ---------------------------------------------------------------------------
# Agent Registry Completeness
# ---------------------------------------------------------------------------

class TestAgentRegistryCompleteness:
    """Verify the agent registry covers all expected categories."""

    def test_all_categories_have_agents(self):
        categories_with_agents = {a.category for a in AGENT_REGISTRY}
        for cat in AgentCategory:
            assert cat in categories_with_agents, (
                f"AgentCategory.{cat.name} has no registered agents"
            )

    def test_minimum_7_agents(self):
        assert len(AGENT_REGISTRY) >= 7

    def test_data_category_has_2_agents(self):
        data_agents = [a for a in AGENT_REGISTRY if a.category == AgentCategory.DATA]
        assert len(data_agents) == 2, (
            f"Expected 2 DATA agents (inventory + logistics), got {len(data_agents)}"
        )

    def test_all_demo_ids_unique_across_agents(self):
        seen = set()
        for agent in AGENT_REGISTRY:
            for d in agent.demo_ids:
                assert d not in seen, (
                    f"demo_id {d} is used by multiple agents"
                )
                seen.add(d)

    def test_high_permission_agents(self):
        high = [a for a in AGENT_REGISTRY if a.permission == PermissionLevel.HIGH]
        assert len(high) >= 3, "Expected at least 3 HIGH-permission agents"


# ---------------------------------------------------------------------------
# Data Files Existence
# ---------------------------------------------------------------------------

class TestDataFilesExistence:
    """Verify expected data files exist."""

    REGIONS = ["us", "tw", "jp"]

    def test_inventory_csv_exists(self, data_dir):
        for region in self.REGIONS:
            path = data_dir / "inventory" / f"{region}_supplier_inventory.csv"
            assert path.exists(), f"Missing inventory file: {path.name}"

    def test_complaint_json_exists(self, data_dir):
        for region in self.REGIONS:
            path = data_dir / "customer-complaints" / f"{region}_complaints_jan25.json"
            assert path.exists(), f"Missing complaint file: {path.name}"

    def test_knowledge_docs_exist(self, data_dir):
        km_dir = data_dir / "sharepoint-km"
        expected = ["common-issues-faq.md", "inventory-troubleshoot.md", "supplier-sync-guide.md"]
        for filename in expected:
            assert (km_dir / filename).exists(), f"Missing knowledge doc: {filename}"
