"""
Inventory Agent - Fabric Inventory Query (Demo 1)
Creates a Foundry Agent that answers 101 Pineapple Cake inventory queries
across Taiwan, Japan, and the US regions using embedded inventory data.

Uses Azure AI Foundry Agent Service GA SDK (azure-ai-projects 1.0.0).
Two chat modes:
  - Agent mode: create_thread_and_process_run (server-side agent)
  - Responses mode: openai.responses.create (lightweight, no thread state)

Run 00_env_check.py first to validate environment and test connections.
"""

import os
import time
from datetime import datetime
import random
import string

from agent_utils import get_project_client, interactive_chat as _interactive_chat, setup_logging

# Setup logging
logger = setup_logging(__name__)

# Configuration
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4.1")
INVENTORY_AGENT_ID = os.getenv("INVENTORY_AGENT_ID", "")  # Set after create

# Create project client using shared utility
project_client = get_project_client()

# ──────────────────────────────────────────────────────────────
# Embedded Inventory Data (from Fabric Lakehouse / CSV sources)
# Last synced: 2026-01-31T08:00:00Z
# ──────────────────────────────────────────────────────────────
INVENTORY_DATA = """
## 📦 Inventory Data — 101 Pineapple Cake (Last Updated: 2026-01-31 08:00 UTC)

### Taiwan (TW)
| Product ID | Product Name | Warehouse | Qty | Unit | Status | Reorder Point | Supplier |
|------------|-------------|-----------|-----|------|--------|---------------|----------|
| P101-TW | 101 造型鳳梨酥 | 台北中央倉庫 (Taipei Central) | 2,100 | 盒 (boxes) | ✅ Normal | 500 | 佳德鳳梨酥供應商 |
| P101-TW-KH | 101 造型鳳梨酥 | 高雄南區倉庫 (Kaohsiung South) | 850 | 盒 (boxes) | ✅ Normal | 200 | 佳德鳳梨酥供應商 |
| P101-TW-TC | 101 造型鳳梨酥 | 台中門市倉 (Taichung Store) | 320 | 盒 (boxes) | 🟡 Low | 100 | 佳德鳳梨酥供應商 |
**Taiwan Total: 3,270 boxes**

### Japan (JP)
| Product ID | Product Name | Warehouse | Qty | Unit | Status | Reorder Point | Supplier |
|------------|-------------|-----------|-----|------|--------|---------------|----------|
| P101-JP | 101 パイナップルケーキ | 東京中央倉庫 (Tokyo Central) | 580 | 盒 (boxes) | ✅ Normal | 200 | 日本代理 - 佐川物流 |
| P101-JP-OS | 101 パイナップルケーキ | 大阪配送センター (Osaka DC) | 120 | 盒 (boxes) | 🟡 Low | 100 | 日本代理 - 佐川物流 |
**Japan Total: 700 boxes**

### USA (US)
| Product ID | Product Name | Warehouse | Qty | Unit | Status | Reorder Point | Supplier | Note |
|------------|-------------|-----------|-----|------|--------|---------------|----------|------|
| P101-US | 101 Pineapple Cake | LA Arcadia Warehouse | **3** | 盒 (boxes) | ⚠️ Critical | 100 | US Distributor - SF Express | 下午空運補貨 300 盒預計 2/1 到達 (300 boxes air freight arriving 2/1 PM) |
| P101-US-NY | 101 Pineapple Cake | New York Warehouse | **0** | 盒 (boxes) | ❌ Out of Stock | 50 | US Distributor - SF Express | 已斷貨 5 天 (Out of stock for 5 days) |
**USA Total: 3 boxes**

### Global Summary
| Region | Total Stock | Status |
|--------|------------|--------|
| 🇹🇼 Taiwan | 3,270 boxes | ✅ Normal |
| 🇯🇵 Japan | 700 boxes | ✅ Normal |
| 🇺🇸 USA | 3 boxes | ⚠️ Critically Low |
| **Global Total** | **3,973 boxes** | |
"""

# Agent instructions with embedded data
instructions = f"""You are the **Inventory Query Agent** for Zava's "101 Pineapple Cake" (101 造型鳳梨酥) product line.

## Role
You query and analyze product inventory data across Taiwan, Japan, and the USA.
You simulate connecting to a Fabric Lakehouse via Fabric MCP to retrieve real-time supplier inventory.

## Data Source
> Source: Foundry Agent → Fabric MCP → Lakehouse (`inventory.supplier_stock`)
> Update frequency: Synced every 15 minutes
> Last sync: 2026-01-31 08:00 UTC

Below is the current inventory snapshot:

{INVENTORY_DATA}

## Capabilities
1. **Inventory Lookup** — Return stock quantities by region, warehouse, or product ID
2. **Anomaly Detection** — Identify critically low stock, out-of-stock, or below-reorder-point situations
3. **Cross-Region Comparison** — Compare inventory levels across TW, JP, US
4. **Restock Recommendations** — Suggest actions based on stock levels and pending shipments

## Known Anomalies (Auto-detected)
- ⚠️ **USA region is critically low!**
  - LA Arcadia Warehouse: only 3 boxes remaining (reorder point: 100)
  - New York Warehouse: 0 boxes — out of stock for 5 consecutive days
  - Air freight of 300 boxes is scheduled to arrive 2/1 PM at LA
- 🟡 Taiwan Taichung store warehouse is at low stock (320 boxes, reorder point 100) — still above threshold
- 🟡 Japan Osaka DC is at low stock (120 boxes, reorder point 100) — still above threshold

## Response Guidelines
1. Always present data in **Markdown tables** for clarity
2. Include a **regional summary** with totals and status indicators (✅ ⚠️ ❌)
3. When anomalies exist, add an **⚠️ Anomaly Alert** section with details and recommended actions
4. Suggest **next steps** when appropriate:
   - Investigate cause of anomaly
   - Check for related customer complaints
   - Confirm restocking progress
5. Use English for responses, keep product names in their original language where helpful
6. Always cite the data source and last sync time
7. If the user asks about a product or region you have no data for, clearly state that

## Scope
- ✅ 101 Pineapple Cake inventory queries across all regions
- ✅ Stock anomaly analysis and restock recommendations
- ❌ Do NOT answer questions unrelated to inventory (redirect politely)
"""


def create_agent(agent_name: str | None = None) -> str:
    """Create a new Inventory Agent in Azure AI Foundry

    Args:
        agent_name: Optional display name. If not provided, a unique name is generated.

    Returns:
        The agent ID of the created agent
    """
    if agent_name is None:
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        agent_name = f"inventory-agent-{date_str}-{random_suffix}"

    agent = project_client.agents.create_agent(
        model=AGENT_MODEL,
        name=agent_name,
        instructions=instructions,
    )

    logger.info("✅ Inventory Agent created!")
    logger.info("🆔 Agent ID: %s", agent.id)
    logger.info("📛 Name: %s", agent.name)
    logger.info("🤖 Model: %s", AGENT_MODEL)
    logger.info("📊 Data: 101 Pineapple Cake inventory (TW/JP/US)")
    print(f"\n💡 To chat with this agent, set env var or run:")
    print(f"   INVENTORY_AGENT_ID=\"{agent.id}\" python 02_inventory_agent.py chat")
    print(f"   python 02_inventory_agent.py ask-responses \"your question\"  (no agent needed)")
    return agent.id


def _resolve_agent_id(agent_id: str | None = None) -> str:
    """Resolve agent ID from argument, env var, or raise error"""
    aid = agent_id or INVENTORY_AGENT_ID
    if not aid:
        raise ValueError(
            "No agent ID provided. Set INVENTORY_AGENT_ID env var or pass agent_id.\n"
            "Run 'python 02_inventory_agent.py create' first."
        )
    return aid


def chat(question: str, agent_id: str | None = None) -> str:
    """
    Chat with the Inventory Agent using Agent threads (server-side).
    Creates a thread, sends the question, waits for completion, returns response.

    Args:
        question: The user's question
        agent_id: The agent ID to use (from create_agent)

    Returns:
        The agent's response text
    """
    aid = _resolve_agent_id(agent_id)

    try:
        agent = project_client.agents.get_agent(aid)
    except Exception as e:
        logger.error("Agent '%s' not found: %s", aid, e)
        return f"❌ Agent '{aid}' not found: {e}"

    # Create thread with user message and run to completion
    run = project_client.agents.create_thread_and_process_run(
        agent_id=agent.id,
    )

    # Now list messages from the thread
    if run.status == "completed":
        # Send the user message and re-run
        thread_id = run.thread_id

        # Add user message to thread
        project_client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=question,
        )

        # Run the agent on the thread
        from azure.ai.agents.models import ThreadRun
        new_run = project_client.agents.runs.create(
            thread_id=thread_id,
            agent_id=agent.id,
        )

        # Poll until complete
        import time as _time
        while new_run.status in ("queued", "in_progress"):
            _time.sleep(1)
            new_run = project_client.agents.runs.get(
                thread_id=thread_id,
                run_id=new_run.id,
            )

        if new_run.status == "completed":
            messages = project_client.agents.messages.list(thread_id=thread_id)
            # Get the latest assistant message
            for msg in messages.data:
                if msg.role == "assistant":
                    for content in msg.content:
                        if hasattr(content, 'text'):
                            return content.text.value
            return "⚠️ No assistant message found"
        else:
            return f"⚠️ Run status: {new_run.status}"
    else:
        return f"⚠️ Initial run status: {run.status}"


def chat_responses(question: str) -> str:
    """
    Lightweight chat using OpenAI Responses API (no agent creation needed).
    Sends the inventory instructions + question directly to the model.

    Args:
        question: The user's question

    Returns:
        The model's response text
    """
    openai_client = project_client.get_openai_client(api_version="2025-04-01-preview")

    response = openai_client.responses.create(
        model=AGENT_MODEL,
        instructions=instructions,
        input=question,
    )

    if response.status == "completed" and response.output:
        for item in response.output:
            if item.type == 'message' and item.content:
                for content in item.content:
                    if hasattr(content, 'text'):
                        return content.text
    return f"⚠️ Response status: {response.status}"


def interactive_chat_responses() -> None:
    """Run an interactive chat session using Responses API (no agent needed)"""
    print("\n" + "=" * 50)
    print("📊 Inventory Agent — Responses API Mode")
    print("=" * 50)
    print("No agent required. Uses model + instructions directly.")
    print("Type 'exit' or 'quit' to end.\n")

    example_prompts = [
        "Check 101 Pineapple Cake inventory across all regions",
        "What's the stock status in the US?",
        "Any inventory anomalies?",
        "Compare multi-region inventory",
    ]
    print("💡 Example queries:")
    for p in example_prompts:
        print(f"  - {p}")
    print()

    while True:
        try:
            question = input("❓ Your question: ").strip()
            if question.lower() in ('exit', 'quit', 'q'):
                print("👋 Bye!")
                break
            if not question:
                continue

            print("🔄 Processing...")
            start = time.time()
            response = chat_responses(question)
            elapsed = time.time() - start
            print(f"\n💬 Response:\n{response}")
            print(f"\n  ⏱️  {elapsed:.1f}s")
            print("-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Bye!")
            break
        except Exception as e:
            logger.error("Error: %s", e)
            print(f"❌ Error: {e}\n")


def demo(use_responses: bool = True) -> None:
    """Run demo queries to showcase the Inventory Agent capabilities

    Args:
        use_responses: If True, use Responses API (no agent needed).
                       If False, use agent threads (requires INVENTORY_AGENT_ID).
    """
    mode = "Responses API" if use_responses else f"Agent ({_resolve_agent_id()})"
    print("\n" + "=" * 60)
    print("📊 Inventory Agent Demo — 101 Pineapple Cake")
    print(f"🤖 Model: {AGENT_MODEL}  |  Mode: {mode}")
    print("=" * 60)

    demo_queries = [
        ("🔍 Full Inventory Query", "Show me the current 101 Pineapple Cake inventory across all regions"),
        ("⚠️ Anomaly Detection", "Are there any inventory anomalies or critical stock issues?"),
        ("🚚 Restock Plan", "What's the restock plan for the US region?"),
    ]

    chat_fn = chat_responses if use_responses else chat

    for label, question in demo_queries:
        print(f"\n{'─' * 60}")
        print(f"  {label}")
        print(f"  ❓ {question}")
        print(f"{'─' * 60}")

        start = time.time()
        response = chat_fn(question)
        elapsed = time.time() - start

        print(f"\n{response}")
        print(f"\n  ⏱️  Response time: {elapsed:.1f}s")

    print(f"\n{'=' * 60}")
    print("✅ Demo complete!")
    print(f"{'=' * 60}\n")


def show_help() -> None:
    """Show usage instructions and example queries"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   Inventory Agent (Demo 1) - Usage                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Agent Mode (requires Foundry agent):                                      ║
║    py 02_inventory_agent.py create [name]     - Create agent in Foundry    ║
║    py 02_inventory_agent.py chat              - Interactive chat (agent)    ║
║    py 02_inventory_agent.py ask <question>    - Single query (agent)       ║
║                                                                            ║
║  Responses Mode (lightweight, no agent needed):                            ║
║    py 02_inventory_agent.py chat-responses    - Interactive chat            ║
║    py 02_inventory_agent.py ask-responses <q> - Single query               ║
║    py 02_inventory_agent.py demo              - Run 3 demo queries         ║
║                                                                            ║
║    py 02_inventory_agent.py help              - Show this help             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                         Example Queries                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  q1: Check 101 Pineapple Cake inventory across all regions                ║
║  q2: What's the stock status in the US?                                   ║
║  q3: Are there any inventory anomalies?                                   ║
║  q4: Compare multi-region inventory for 101 Pineapple Cake                ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "create":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            create_agent(name)

        elif cmd == "chat":
            # Agent-based interactive chat
            aid = sys.argv[2] if len(sys.argv) > 2 else None
            aid = _resolve_agent_id(aid)
            _interactive_chat(
                agent_name=aid,
                chat_func=chat,
                welcome_message=f"📊 Inventory Agent Chat (Agent: {aid})",
                example_prompts=[
                    "Check 101 Pineapple Cake inventory across all regions",
                    "What's the stock status in the US?",
                    "Any inventory anomalies?",
                ],
            )

        elif cmd == "chat-responses":
            interactive_chat_responses()

        elif cmd == "ask":
            if len(sys.argv) > 2:
                question = " ".join(sys.argv[2:])
                print(chat(question))
            else:
                print("Usage: py 02_inventory_agent.py ask <question>")

        elif cmd == "ask-responses":
            if len(sys.argv) > 2:
                question = " ".join(sys.argv[2:])
                print(chat_responses(question))
            else:
                print("Usage: py 02_inventory_agent.py ask-responses <question>")

        elif cmd == "demo":
            demo(use_responses=True)

        elif cmd == "help":
            show_help()
        else:
            show_help()
    else:
        show_help()
