#!/usr/bin/env python3
"""Console test app for Zava Smart Assistant powered by GitHub Copilot SDK.

Features:
- Shows numbered menu of available skills
- User can type a number to select a skill or enter free-form text
- Slash commands: /skills, /mcp, /help, /agent, /exit
- Streaming output to console
"""

import asyncio
import json
import sys
from pathlib import Path

# ANSI color codes for terminal output
COLOR_USER = "\033[1;36m"      # Bold Cyan
COLOR_ASSISTANT = "\033[1;33m"  # Bold Yellow
COLOR_DIM = "\033[2m"           # Dim
COLOR_RESET = "\033[0m"         # Reset

from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

from src.skills import load_skills
from src.tools import build_tools
from src.prompts import SYSTEM_MESSAGE
from src.agents import AGENT_REGISTRY


# ============================================================================
# Config directory
# ============================================================================
CONFIG_DIR = Path(__file__).parent / "config"


def _load_json(filename: str):
    """Load a JSON config file from the config/ directory."""
    path = CONFIG_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# Sample Custom Agents (loaded from config/agent.json)
# ============================================================================
SAMPLE_AGENTS: list[dict] = _load_json("agent.json")

# ============================================================================
# MCP Servers Configuration (loaded from config/mcp_server.json)
# ============================================================================
MCP_SERVERS: dict[str, dict] = _load_json("mcp_server.json")


def print_skills_menu(skills):
    """Print the available skills as a numbered menu."""
    print("\n" + "=" * 60)
    print("🍍 Zava Smart Assistant - Available Skills")
    print("=" * 60)
    for i, skill in enumerate(skills, 1):
        triggers = ", ".join(skill.triggers[:3]) if skill.triggers else ""
        if len(skill.triggers) > 3:
            triggers += "..."
        print(f"  [{i}] {skill.name}")
        print(f"      {skill.description}")
        if triggers:
            print(f"      Triggers: {triggers}")
        print()
    print("=" * 60)


def print_mcp_servers():
    """Print available MCP servers."""
    print("\n" + "=" * 60)
    print("🔌 MCP Server List (Model Context Protocol)")
    print("=" * 60)
    for key, mcp in MCP_SERVERS.items():
        print(f"  {mcp['status']} {mcp['name']}")
        print(f"      {mcp['description']}")
        print(f"      Repo: {mcp['repo']}")
        print()
    print("=" * 60)


def print_agents_menu():
    """Print available custom agents."""
    print("\n" + "=" * 60)
    print("🤖 Custom Agents")
    print("=" * 60)
    for i, agent in enumerate(SAMPLE_AGENTS, 1):
        print(f"  [{i}] {agent['name']}")
        print(f"      {agent['description']}")
        print()
    print("=" * 60)
    print("Tip: Use '/agent N' to switch to a specific agent (e.g., /agent 1)")
    print("=" * 60)


def print_help():
    """Print help/command manual."""
    print("\n" + "=" * 60)
    print("📖 Command Manual")
    print("=" * 60)
    print("""
  Slash Commands:
  ─────────────────────────────────────────────────────────
    /skills    Show all available skills
    /mcp       Show MCP server list
    /agent     Browse custom agents
    /help      Show this help
    /exit      Exit the program

  Number Selection:
  ─────────────────────────────────────────────────────────
    1-8        Enter a number to select the corresponding skill

  Free Chat:
  ─────────────────────────────────────────────────────────
    Any text   Enter any question to chat with Zava

  Shortcuts:
  ─────────────────────────────────────────────────────────
    ?          Show skills menu
    0          Exit the program
    Ctrl+C     Force quit
""")
    print("=" * 60)


def get_skill_prompt_by_number(skills, num: int) -> str | None:
    """Get a sample prompt for the skill at the given index (1-based)."""
    if num < 1 or num > len(skills):
        return None
    skill = skills[num - 1]

    # === Logging: selected skill / agent / MCP ===
    print(f"\n{'═' * 50}")
    print(f"📋 [SKILL SELECTED] {skill.name}")
    if skill.demo_id is not None:
        for agent in AGENT_REGISTRY:
            if skill.demo_id in agent.demo_ids:
                print(f"🤖 [AGENT] {agent.display_name} ({agent.category.value})")
                print(f"🔐 [PERMISSION] {agent.permission_icon} {agent.permission.value}")
                mcp = agent.mcp_connector or "(direct access)"
                print(f"🔌 [MCP]   {mcp}")
                break
    print(f"{'═' * 50}")

    # Use first trigger as sample prompt, or a generic query
    if skill.triggers:
        return skill.triggers[0]
    return f"Please execute {skill.name}"


async def run_console():
    """Main console loop."""
    # Load skills
    print("\nLoading skills...")
    skills = load_skills()
    tools = build_tools(skills)
    print(f"✓ Loaded {len(tools)} skills\n")

    # Log agent registry
    print(f"📋 [LOG] Agent Registry: {len(AGENT_REGISTRY)} agents")
    for agent in AGENT_REGISTRY:
        mcp = agent.mcp_connector or "(direct)"
        demos = ", ".join(f"demo{d}" for d in agent.demo_ids)
        print(f"   {agent.category_icon} {agent.display_name:<25} MCP: {mcp:<20} Demos: {demos}")
    print()

    # Log MCP server config + health check HTTP endpoints
    print(f"🔌 [LOG] MCP Servers: {len(MCP_SERVERS)} configured")
    for key, mcp in MCP_SERVERS.items():
        status_icon = mcp['status']
        if mcp['type'] == 'http':
            url = mcp.get('url', '')
            try:
                import urllib.request
                req = urllib.request.Request(url, method='HEAD')
                req.add_header('User-Agent', 'ZavaHealthCheck/1.0')
                with urllib.request.urlopen(req, timeout=5) as resp:
                    status_icon = f"✅ Reachable ({resp.status})"
            except Exception as e:
                err_msg = str(e)[:40]
                status_icon = f"⚠️  Unreachable ({err_msg})"
        print(f"   {status_icon} {mcp['name']:<20} Type: {mcp['type']}")
    print()

    # Initialize Copilot client
    print("Connecting to Copilot SDK...")
    client = CopilotClient()
    await client.start()

    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "tools": tools,
        "system_message": {
            "content": SYSTEM_MESSAGE,
        },
        "mcp_servers": {
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
        },
    })
    print("✓ Copilot connected successfully\n")

    # Show initial menu
    print_skills_menu(skills)
    print("\n💬 Hello! I'm Zava Smart Assistant. How can I help you?")
    print("   Type /help to see all commands\n")

    while True:
        try:
            user_input = input(f"\n{COLOR_USER}🧑 You >{COLOR_RESET} ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n")
            break

        if not user_input:
            continue

        # Check for exit
        if user_input == "0" or user_input.lower() in ("exit", "quit", "bye", "/exit"):
            print("\n👋 Goodbye! Feel free to reach out anytime.\n")
            break

        # Check for menu request
        if user_input == "?" or user_input.lower() == "menu":
            print_skills_menu(skills)
            continue

        # ====== Slash Commands ======
        if user_input.startswith("/"):
            cmd = user_input.lower().split()[0]
            if cmd == "/skills":
                print_skills_menu(skills)
                continue
            elif cmd == "/mcp":
                print_mcp_servers()
                continue
            elif cmd == "/agent":
                parts = user_input.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    agent_num = int(parts[1])
                    if 1 <= agent_num <= len(SAMPLE_AGENTS):
                        selected = SAMPLE_AGENTS[agent_num - 1]
                        print(f"\n{'═' * 50}")
                        print(f"🤖 [AGENT SWITCH] → {selected['name']}")
                        print(f"   {selected['description']}")
                        print(f"{'═' * 50}")
                    else:
                        print(f"   ⚠️ Invalid agent number: {agent_num}")
                else:
                    print_agents_menu()
                continue
            elif cmd == "/help":
                print_help()
                continue
            else:
                print(f"   ⚠️ Unknown command: {cmd}")
                print("   Type /help to see available commands")
                continue

        # Check if input is a number (skill selection)
        prompt = user_input
        if user_input.isdigit():
            num = int(user_input)
            skill_prompt = get_skill_prompt_by_number(skills, num)
            if skill_prompt:
                prompt = skill_prompt
            else:
                print(f"   ⚠️ Invalid skill number: {num}")
                continue

        # Send to Copilot and stream response
        print(f"\n{COLOR_DIM}{'─' * 50}{COLOR_RESET}")
        print(f"{COLOR_ASSISTANT}🍍 Zava >{COLOR_RESET} ", end="", flush=True)

        done = asyncio.Event()
        collected: list[str] = []

        def handle_event(event):
            if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                delta = event.data.delta_content or ""
                if delta:
                    collected.append(delta)
                    print(delta, end="", flush=True)
            elif event.type == SessionEventType.TOOL_EXECUTION_START:
                tool_name = getattr(event.data, "tool_name", None) or ""
                mcp_server = getattr(event.data, "mcp_server_name", None)
                mcp_tool = getattr(event.data, "mcp_tool_name", None)
                if mcp_server:
                    print(f"\n   🔌 [MCP CALL] {mcp_server}::{mcp_tool or tool_name}", flush=True)
                elif tool_name:
                    print(f"\n   🛠️  [TOOL CALL] {tool_name}", flush=True)
            elif event.type == SessionEventType.TOOL_EXECUTION_COMPLETE:
                tool_name = getattr(event.data, "tool_name", None) or ""
                mcp_server = getattr(event.data, "mcp_server_name", None)
                if mcp_server:
                    print(f"   ✅ [MCP DONE] {mcp_server}::{tool_name}", flush=True)
            elif event.type == SessionEventType.SESSION_IDLE:
                done.set()

        unsubscribe = session.on(handle_event)

        try:
            await session.send_and_wait({"prompt": prompt}, timeout=300)
            try:
                await asyncio.wait_for(done.wait(), timeout=300)
            except asyncio.TimeoutError:
                print("\n[Timeout - 5min exceeded]", end="")
        finally:
            unsubscribe()

        print(f"\n{COLOR_DIM}{'─' * 50}{COLOR_RESET}\n")  # New line after response

    # Cleanup
    print("Closing connection...")
    try:
        await session.destroy()
    except Exception:
        pass
    try:
        await client.stop()
    except Exception:
        pass
    print("✓ Closed\n")


def main():
    """Entry point."""
    print("""
╔══════════════════════════════════════════════════════════╗
║       🍍 Zava Smart Assistant - Console Test App 🍍      ║
║         Agent League TechConnect 2026                    ║
╚══════════════════════════════════════════════════════════╝
""")
    asyncio.run(run_console())


if __name__ == "__main__":
    main()
