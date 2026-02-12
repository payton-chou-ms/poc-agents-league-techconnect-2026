"""Custom exception classes for the Zava Smart Assistant.

Provides structured error handling across the application.
"""


class ZavaError(Exception):
    """Base exception for all Zava errors."""


class SkillLoadError(ZavaError):
    """Raised when a SKILL.md file cannot be parsed or loaded."""

    def __init__(self, skill_path: str, reason: str):
        self.skill_path = skill_path
        self.reason = reason
        super().__init__(f"Failed to load skill '{skill_path}': {reason}")


class RoutingError(ZavaError):
    """Raised when intent routing encounters an unexpected state."""

    def __init__(self, user_input: str, detail: str = ""):
        self.user_input = user_input
        self.detail = detail
        super().__init__(
            f"Routing error for input '{user_input[:50]}...': {detail}"
        )


class PermissionError(ZavaError):
    """Raised when an agent lacks required permissions."""

    def __init__(self, agent_name: str, required_level: str):
        self.agent_name = agent_name
        self.required_level = required_level
        super().__init__(
            f"Agent '{agent_name}' lacks required permission level '{required_level}'"
        )


class MCPConnectionError(ZavaError):
    """Raised when an MCP server is unreachable or returns an error."""

    def __init__(self, server_name: str, url: str = "", reason: str = ""):
        self.server_name = server_name
        self.url = url
        self.reason = reason
        super().__init__(
            f"MCP server '{server_name}' connection failed: {reason}"
        )


class AgentNotFoundError(ZavaError):
    """Raised when an agent name cannot be resolved in the registry."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(f"Agent '{agent_name}' not found in registry")
