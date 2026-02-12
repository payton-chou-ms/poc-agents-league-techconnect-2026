"""Shared fixtures and test configuration for Zava test suite."""

import sys
from pathlib import Path

import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def skills_dir():
    """Path to the .github/skills directory."""
    return PROJECT_ROOT / ".github" / "skills"


@pytest.fixture
def data_dir():
    """Path to the data/ directory."""
    return PROJECT_ROOT / "data"


@pytest.fixture
def all_skills(skills_dir):
    """Load all skills from the skills directory."""
    from src.skills import load_skills
    return load_skills(skills_dir)


@pytest.fixture
def all_tools(all_skills):
    """Build all tools from loaded skills."""
    from src.tools import build_tools
    return build_tools(all_skills)
