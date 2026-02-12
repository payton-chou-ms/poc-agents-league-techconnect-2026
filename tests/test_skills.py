"""Tests for src/skills.py — SKILL.md loader and parser."""

import pytest
from pathlib import Path

from src.skills import (
    Skill,
    _parse_frontmatter,
    _extract_triggers,
    _extract_response,
    load_skills,
)


class TestParseFrontmatter:
    def test_basic_frontmatter(self):
        content = "---\nname: test-skill\ndescription: A test\n---\nBody"
        fm = _parse_frontmatter(content)
        assert fm["name"] == "test-skill"
        assert fm["description"] == "A test"

    def test_no_frontmatter(self):
        content = "Just some text without frontmatter"
        fm = _parse_frontmatter(content)
        assert fm == {}

    def test_empty_frontmatter(self):
        content = "---\n---\nBody"
        fm = _parse_frontmatter(content)
        assert fm == {}

    def test_frontmatter_with_quotes(self):
        content = "---\nname: fabric-inventory-query\ndescription: 'Query data from Fabric'\n---\n"
        fm = _parse_frontmatter(content)
        assert fm["name"] == "fabric-inventory-query"
        assert "Fabric" in fm["description"]


class TestExtractTriggers:
    def test_english_triggers(self):
        content = "## Triggers\n\n- Check inventory\n- Product stock\n- Supplier data\n\n## Next Section"
        triggers = _extract_triggers(content)
        assert len(triggers) == 3
        assert "Check inventory" in triggers

    def test_alternate_header_triggers(self):
        """Test that the parser handles the Chinese '觸發條件' header."""
        content = "## \u89f8\u767c\u689d\u4ef6\n\n- check stock\n- out of stock\n- supplier\n"
        triggers = _extract_triggers(content)
        assert len(triggers) == 3
        assert "check stock" in triggers

    def test_no_triggers_section(self):
        content = "## Other Section\n\nSome content"
        triggers = _extract_triggers(content)
        assert triggers == []

    def test_empty_triggers(self):
        content = "## Triggers\n\n## Next Section"
        triggers = _extract_triggers(content)
        assert triggers == []

    def test_triggers_with_extra_whitespace(self):
        content = "## Triggers\n\n-   Spaced trigger  \n- Normal trigger\n"
        triggers = _extract_triggers(content)
        assert len(triggers) == 2
        assert "Spaced trigger" in triggers


class TestExtractResponse:
    def test_basic_response(self):
        content = "## Default Response\n\nSome intro\n\n---\n\nResponse body here\n\n## Tools Used\n\nSome tools"
        response = _extract_response(content)
        assert "Response body here" in response

    def test_alternate_header_response(self):
        """Test that the parser handles the Chinese response/tools headers."""
        content = "## \u9810\u8a2d\u56de\u61c9\n\nIntro\n\n---\n\nAlternate response\n\n## \u4f7f\u7528\u7684\u5de5\u5177\n\nTools"
        response = _extract_response(content)
        assert "Alternate response" in response

    def test_no_response_section(self):
        content = "## Other Section\n\nContent"
        response = _extract_response(content)
        assert response == ""


class TestLoadSkills:
    def test_load_all_8_skills(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        assert len(skills) == 8, f"Expected 8 skills, got {len(skills)}"

    def test_skills_sorted_by_demo_id(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        demo_ids = [s.demo_id for s in skills if s.demo_id is not None]
        assert demo_ids == sorted(demo_ids)

    def test_demo_ids_1_to_8(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        demo_ids = {s.demo_id for s in skills}
        assert demo_ids == {1, 2, 3, 4, 5, 6, 7, 8}

    def test_every_skill_has_name(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        for skill in skills:
            assert skill.name, f"Skill with demo_id={skill.demo_id} has no name"

    def test_every_skill_has_description(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        for skill in skills:
            assert skill.description, f"Skill '{skill.name}' has no description"

    def test_every_skill_has_triggers(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        for skill in skills:
            assert len(skill.triggers) >= 1, (
                f"Skill '{skill.name}' has no triggers"
            )

    def test_every_skill_has_response(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        for skill in skills:
            assert len(skill.response_content) > 0, (
                f"Skill '{skill.name}' has empty response_content"
            )

    def test_skill_names_unique(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        names = [s.name for s in skills]
        assert len(names) == len(set(names)), f"Duplicate skill names: {names}"

    def test_load_missing_directory(self):
        skills = load_skills("/tmp/nonexistent-skills-dir-xyz")
        assert skills == []

    def test_known_skill_names(self, skills_dir):
        if not skills_dir.exists():
            pytest.skip("Skills directory not found")
        skills = load_skills(skills_dir)
        names = {s.name for s in skills}
        expected_names = {
            "fabric-inventory-query",
            "sharepoint-km-query",
            "github-bugfix-agent",
            "bing-weather-search",
            "logistics-tracking-query",
            "azure-system-health",
            "incident-report-generator",
            "workiq-meeting-booking",
        }
        assert names == expected_names, f"Unexpected skill names: {names - expected_names}"
