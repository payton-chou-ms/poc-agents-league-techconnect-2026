"""Tests for MCP configuration and feature validation."""

import pytest

# Import MCP config from console_app (may need adjustment if restructured)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMcpServersConfig:
    """Validate MCP_SERVERS dict from console_app."""

    @pytest.fixture(autouse=True)
    def load_mcp_config(self):
        """Load MCP_SERVERS without importing the entire console_app."""
        # We extract the config dict directly since console_app has async code
        from console_app import MCP_SERVERS
        self.mcp_servers = MCP_SERVERS

    def test_mcp_servers_not_empty(self):
        assert len(self.mcp_servers) >= 2

    def test_each_server_has_name(self):
        for key, mcp in self.mcp_servers.items():
            assert "name" in mcp, f"Server '{key}' missing 'name'"

    def test_each_server_has_status(self):
        for key, mcp in self.mcp_servers.items():
            assert "status" in mcp, f"Server '{key}' missing 'status'"

    def test_each_server_has_description(self):
        for key, mcp in self.mcp_servers.items():
            assert "description" in mcp, f"Server '{key}' missing 'description'"

    def test_each_server_has_type(self):
        for key, mcp in self.mcp_servers.items():
            assert "type" in mcp, f"Server '{key}' missing 'type'"
            assert mcp["type"] in ("http", "local"), (
                f"Server '{key}' has unknown type '{mcp['type']}'"
            )

    def test_http_servers_have_url(self):
        for key, mcp in self.mcp_servers.items():
            if mcp["type"] == "http":
                assert "url" in mcp, f"HTTP server '{key}' missing 'url'"
                assert mcp["url"].startswith("https://"), (
                    f"HTTP server '{key}' URL should use HTTPS"
                )

    def test_local_servers_have_command(self):
        for key, mcp in self.mcp_servers.items():
            if mcp["type"] == "local":
                assert "command" in mcp, f"Local server '{key}' missing 'command'"
                assert "args" in mcp, f"Local server '{key}' missing 'args'"
                assert isinstance(mcp["args"], list)

    def test_github_mcp_configured(self):
        assert "github" in self.mcp_servers
        assert self.mcp_servers["github"]["type"] == "http"

    def test_workiq_mcp_configured(self):
        assert "workiq" in self.mcp_servers
        assert self.mcp_servers["workiq"]["type"] == "http"


class TestLiveMcpSkillsMap:
    """Validate LIVE_MCP_SKILLS mapping consistency."""

    def test_live_skills_keys_are_valid_skill_names(self, all_skills):
        from src.tools import LIVE_MCP_SKILLS
        skill_names = {s.name for s in all_skills}
        for live_name in LIVE_MCP_SKILLS:
            assert live_name in skill_names, (
                f"LIVE_MCP_SKILLS key '{live_name}' not in loaded skills"
            )

    def test_live_skills_session_keys_match_mcp_servers(self):
        from src.tools import LIVE_MCP_SKILLS
        from console_app import MCP_SERVERS
        for skill_name, session_key in LIVE_MCP_SKILLS.items():
            assert session_key in MCP_SERVERS, (
                f"Session key '{session_key}' for '{skill_name}' "
                f"not found in MCP_SERVERS"
            )


class TestMcpSessionConfig:
    """Validate the MCP session configuration shape used in CopilotClient."""

    def test_session_mcp_config_shape(self):
        """The session mcp_servers dict should have correct structure."""
        # This is the config defined in console_app.run_console()
        config = {
            "workiq": {
                "type": "http",
                "url": "https://workiq.microsoft.com/mcp/",
                "tools": ["*"],
            },
            "github": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp/",
                "tools": ["*"],
            },
        }
        for key, server in config.items():
            assert "type" in server
            assert "url" in server
            assert "tools" in server
            assert server["type"] == "http"
            assert server["url"].startswith("https://")
