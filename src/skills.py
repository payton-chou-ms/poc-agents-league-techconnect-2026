"""Loader for .github/skills/ SKILL.md files."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Skill:
    name: str
    description: str
    triggers: list[str] = field(default_factory=list)
    response_content: str = ""
    demo_id: int | None = None  # extracted from folder name (e.g. demo1 → 1)


def _parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from skill markdown content.

    Handles both ```skill fenced and standard --- fenced frontmatter.
    """
    # Pattern: ```skill\n---\n...\n---\n
    match = re.search(r"---\n(.+?)\n---", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            pass
    return {}


def _extract_triggers(content: str) -> list[str]:
    """Extract trigger keywords from the Triggers section."""
    pattern = r"## (?:觸發條件|Triggers)\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []

    triggers = []
    for line in match.group(1).split("\n"):
        line = line.strip()
        if line.startswith("- "):
            keyword = line[2:].strip()
            if keyword:
                triggers.append(keyword)
    return triggers


def _extract_response(content: str) -> str:
    """Extract the main response content after ## Default Response.

    Gets everything between the first --- after Default Response and the
    ## Tools Used / ## Data Sources sections (or end of file).
    """
    # Find Default Response / 預設回應 section
    pattern = r"## (?:預設回應|Default Response)\s*\n.*?\n---\n(.*?)(?=\n## (?:使用的工具|Tools Used)|\n## (?:資料來源|Data Sources)|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: everything after the section header
    pattern = r"## (?:預設回應|Default Response)\s*\n(.*?)(?=\n## (?:使用的工具|Tools Used)|\n## (?:資料來源|Data Sources)|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()

    return ""


def load_skills(skills_dir: str | Path | None = None) -> list[Skill]:
    """Load all SKILL.md files from .github/skills/ directory.

    Args:
        skills_dir: Path to the skills directory. If None, auto-detects
                    relative to this file's project root.

    Returns:
        List of Skill objects sorted by folder name (demo1, demo2, ...).
    """
    if skills_dir is None:
        project_root = Path(__file__).parent.parent
        skills_dir = project_root / ".github" / "skills"
    else:
        skills_dir = Path(skills_dir)

    skills: list[Skill] = []

    if not skills_dir.exists():
        print(f"Warning: skills directory not found at {skills_dir}")
        return skills

    for skill_folder in sorted(skills_dir.iterdir()):
        if not skill_folder.is_dir():
            continue
        skill_file = skill_folder / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text(encoding="utf-8")

        # Strip the opening/closing ```skill fences for cleaner parsing
        clean = re.sub(r"^```+\w*\s*\n", "", content)
        clean = re.sub(r"\n```+\s*$", "", clean)

        fm = _parse_frontmatter(content)
        triggers = _extract_triggers(clean)
        response = _extract_response(clean)

        # Extract demo_id from folder name (e.g. "demo1-fabric-inventory" → 1)
        demo_id = None
        match_demo = re.match(r"demo(\d+)", skill_folder.name)
        if match_demo:
            demo_id = int(match_demo.group(1))

        skill = Skill(
            name=fm.get("name", skill_folder.name),
            description=fm.get("description", ""),
            triggers=triggers,
            response_content=response,
            demo_id=demo_id,
        )
        skills.append(skill)
        print(f"  Loaded skill: {skill.name} ({len(skill.triggers)} triggers)")

    return skills
