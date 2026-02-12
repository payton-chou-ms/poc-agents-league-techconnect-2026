"""Tests for ref/02_inventory_agent.py — Foundry Agent structure validation.

These tests validate the agent's configuration, instructions, and data
WITHOUT requiring Azure credentials. They parse the module's globals
to verify correctness of the embedded data, instructions, and scope.
"""

import re
import sys
from pathlib import Path

import pytest

# ------------------------------------------------------------------
# Import strategy: We can't import the module normally because it calls
# get_project_client() at module level (requires Azure credentials).
# Instead, we parse the source file directly for structural validation.
# ------------------------------------------------------------------

REF_DIR = Path(__file__).parent.parent / "ref"
AGENT_SCRIPT = REF_DIR / "02_inventory_agent.py"
AGENT_UTILS_SCRIPT = REF_DIR / "agent_utils.py"


@pytest.fixture(scope="module")
def agent_source():
    """Read the raw source of 02_inventory_agent.py."""
    if not AGENT_SCRIPT.exists():
        pytest.skip("ref/02_inventory_agent.py not found")
    return AGENT_SCRIPT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def agent_utils_source():
    """Read the raw source of agent_utils.py."""
    if not AGENT_UTILS_SCRIPT.exists():
        pytest.skip("ref/agent_utils.py not found")
    return AGENT_UTILS_SCRIPT.read_text(encoding="utf-8")


# ===========================================================================
# A7: Foundry Agent Structure Tests
# ===========================================================================


class TestFoundryAgentFileExists:
    """Verify all ref/ scripts are present."""

    def test_02_inventory_agent_exists(self):
        assert AGENT_SCRIPT.exists(), "ref/02_inventory_agent.py should exist"

    def test_agent_utils_exists(self):
        assert AGENT_UTILS_SCRIPT.exists(), "ref/agent_utils.py should exist"

    def test_01_iq_agent_exists(self):
        iq = REF_DIR / "01_iq_agent.py"
        assert iq.exists(), "ref/01_iq_agent.py should exist"

    def test_00_env_check_exists(self):
        ec = REF_DIR / "00_env_check.py"
        assert ec.exists(), "ref/00_env_check.py should exist"


class TestFoundryInstructionsContent:
    """Validate the instructions string embedded in the agent script."""

    def test_instructions_contain_inventory_data(self, agent_source):
        assert "INVENTORY_DATA" in agent_source, (
            "Agent script should define INVENTORY_DATA"
        )

    def test_instructions_contain_taiwan_data(self, agent_source):
        assert "Taiwan" in agent_source or "TW" in agent_source

    def test_instructions_contain_japan_data(self, agent_source):
        assert "Japan" in agent_source or "JP" in agent_source

    def test_instructions_contain_usa_data(self, agent_source):
        assert "USA" in agent_source or "US" in agent_source

    def test_instructions_contain_three_regions_with_totals(self, agent_source):
        assert "3,270" in agent_source, "Should contain TW total 3,270"
        assert "700" in agent_source, "Should contain JP total 700"
        assert "3 boxes" in agent_source, "Should contain US total 3"

    def test_instructions_contain_response_guidelines(self, agent_source):
        assert "Response Guidelines" in agent_source, (
            "Instructions should include 'Response Guidelines' section"
        )

    def test_instructions_contain_scope(self, agent_source):
        assert "## Scope" in agent_source, (
            "Instructions should define a '## Scope' section"
        )
        assert "✅" in agent_source, "Scope should have ✅ (in-scope items)"
        assert "❌" in agent_source, "Scope should have ❌ (out-of-scope items)"

    def test_instructions_contain_anomaly_section(self, agent_source):
        assert "Anomal" in agent_source, (
            "Instructions should describe known anomalies"
        )

    def test_instructions_contain_capabilities(self, agent_source):
        assert "Capabilities" in agent_source, (
            "Instructions should define agent capabilities"
        )

    def test_instructions_mention_101_pineapple_cake(self, agent_source):
        assert "101" in agent_source and "Pineapple" in agent_source


class TestFoundryAgentFunctions:
    """Validate that key functions are defined in the agent script."""

    def test_create_agent_defined(self, agent_source):
        assert "def create_agent(" in agent_source

    def test_chat_defined(self, agent_source):
        assert "def chat(" in agent_source

    def test_chat_responses_defined(self, agent_source):
        assert "def chat_responses(" in agent_source

    def test_demo_defined(self, agent_source):
        assert "def demo(" in agent_source

    def test_create_agent_uses_model(self, agent_source):
        assert "AGENT_MODEL" in agent_source

    def test_chat_responses_uses_responses_api(self, agent_source):
        assert "responses.create" in agent_source, (
            "chat_responses should use OpenAI Responses API"
        )

    def test_create_agent_uses_sdk(self, agent_source):
        assert "agents.create_agent" in agent_source, (
            "create_agent should use project_client.agents.create_agent"
        )


class TestFoundryAgentDemoQueries:
    """Validate demo queries cover the required scenarios."""

    def test_demo_has_full_inventory_query(self, agent_source):
        assert "inventory" in agent_source.lower()

    def test_demo_has_anomaly_query(self, agent_source):
        assert "anomal" in agent_source.lower()

    def test_demo_has_restock_query(self, agent_source):
        assert "restock" in agent_source.lower()


class TestAgentUtilsFunctions:
    """Validate shared agent_utils.py has no import issues structurally."""

    def test_get_project_client_defined(self, agent_utils_source):
        assert "def get_project_client(" in agent_utils_source

    def test_interactive_chat_defined(self, agent_utils_source):
        assert "def interactive_chat(" in agent_utils_source

    def test_setup_logging_defined(self, agent_utils_source):
        assert "def setup_logging(" in agent_utils_source

    def test_uses_dotenv(self, agent_utils_source):
        assert "load_dotenv" in agent_utils_source

    def test_uses_default_credential(self, agent_utils_source):
        assert "DefaultAzureCredential" in agent_utils_source

    def test_checks_endpoint_env_var(self, agent_utils_source):
        assert "AZURE_EXISTING_AIPROJECT_ENDPOINT" in agent_utils_source
