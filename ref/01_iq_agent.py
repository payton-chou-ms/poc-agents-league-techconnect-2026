"""
SRS Agent - Create and Chat
Creates an SRS (Service Request System) support agent with MCP knowledge base tool,
and provides a chat function using the Responses API.

Run 00_env_check.py first to validate environment and test connections.
"""

import os
from datetime import datetime
import random
import string

from azure.ai.projects.models import PromptAgentDefinition, MCPTool

from agent_utils import get_project_client, interactive_chat as _interactive_chat, setup_logging

# Setup logging
logger = setup_logging(__name__)

# Configuration
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
KNOWLEDGE_BASE_NAME = os.getenv("KNOWLEDGE_BASE_NAME")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4.1")
AGENT_NAME = os.getenv("AGENT_NAME", "srs-agent")  # Use existing agent or create new

# MCP Knowledge Base connection
# The project_connection_id is used for authentication with the MCP server
MCP_CONNECTION_ID = os.getenv("MCP_CONNECTION_ID", "kb-knowledgebase403-7ssib")
mcp_endpoint = f"{SEARCH_SERVICE_ENDPOINT}/knowledgebases/{KNOWLEDGE_BASE_NAME}/mcp?api-version=2025-11-01-preview"

# Create project client using shared utility
project_client = get_project_client()

# Agent instructions
instructions = """你是 SRS (Service Request System) 系統的專業技術支援助理。你的職責是「僅回答 SRS 系統相關的技術問題」。

## 核心職責
回答 SRS 系統相關的疑難排解問題,包含:
- 帳號申請與建立錯誤(AD Account、APC Account、Service Account)
- 簽核流程與 Approval Flow 配置問題
- 系統設定與配置(Service Item Setup、Approval Rule)
- 分機申請與 PhoneBook 整合問題
- 批次作業與資料同步問題(Reposting、Employee interregional transfer)

## 回答範圍判斷
在回答前,先判斷問題是否與 SRS 系統相關:
- ✅ SRS 相關: 帳號申請、簽核流程、系統配置、錯誤訊息、批次作業
- ❌ 非 SRS 相關: 程式語言教學、框架比較、一般知識、烹飪食譜、天文地理、工作方法論

若問題與 SRS 系統無關,請簡短回覆:
「很抱歉,我是 SRS 系統技術支援助理,僅能協助解決 SRS 相關問題。關於您的問題,知識庫中沒有相關資訊。如有 SRS 系統相關問題,歡迎隨時詢問!」

## 回答原則
1. 僅回答知識庫中有明確記錄的內容
2. 提供結構化、步驟化的解決方案
3. 引用具體的系統欄位、功能名稱、SQL 查詢範例與操作路徑
4. 如知識庫中找不到相關資訊,明確回答「知識庫中沒有相關資訊」
5. 絕對不要編造、推測或提供通用建議

## 回答格式
- 使用繁體中文(zh-TW)
- 使用 Markdown 格式化(標題、列表、程式碼區塊)
- 條列式說明步驟,每個步驟包含明確的操作指示
- 標註需確認的系統位置、資料表、欄位名稱
- 提供相關的 SQL 查詢範例(如適用)
- 引用知識庫來源文件名稱
"""



def create_agent(agent_name: str | None = None) -> str:
    """Create a new SRS agent with MCP knowledge base tool
    
    Args:
        agent_name: Optional agent name. If not provided, a unique name will be generated.
        
    Returns:
        The name of the created agent
    """
    if agent_name is None:
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        agent_name = f"srs-agent-{date_str}-{random_suffix}"
    
    mcp_kb_tool = MCPTool(
        server_label="knowledge-base",
        server_url=mcp_endpoint,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=MCP_CONNECTION_ID  # Required for authentication
    )

    project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=AGENT_MODEL,
            instructions=instructions,
            tools=[mcp_kb_tool]
        )
    )

    logger.info("✅ Agent '%s' created successfully!", agent_name)
    logger.info("🤖 Model: %s", AGENT_MODEL)
    logger.info("📎 MCP Endpoint: %s", mcp_endpoint)
    return agent_name


def chat(question: str, agent_name: str = AGENT_NAME) -> str:
    """
    Chat with the SRS agent using Responses API.
    
    Args:
        question: The user's question
        agent_name: The name of the agent to use (default: srs-agent)
    
    Returns:
        The agent's response text
    """
    # Get OpenAI client
    openai_client = project_client.get_openai_client()
    
    # Get agent details with error handling
    try:
        agent = project_client.agents.get(agent_name)
    except Exception as e:
        logger.error("Agent '%s' 不存在或無法存取: %s", agent_name, e)
        return f"❌ Agent '{agent_name}' 不存在或無法存取: {e}"
    
    latest_version = agent.versions.get('latest')
    definition = latest_version.definition
    
    # Modify tools to set require_approval to never
    tools = definition.get('tools', [])
    for tool in tools:
        tool['require_approval'] = 'never'
    
    # Use Responses API with agent's config
    response = openai_client.responses.create(
        model=definition['model'],
        instructions=definition.get('instructions', ''),
        tools=tools,
        input=question
    )
    
    # Extract response text
    if response.status == "completed" and response.output:
        for item in response.output:
            if item.type == 'message' and item.content:
                for content in item.content:
                    if hasattr(content, 'text'):
                        return content.text
    
    return f"⚠️ Response status: {response.status}"


def interactive_chat(agent_name: str = AGENT_NAME) -> None:
    """Run an interactive chat session with the agent
    
    Args:
        agent_name: The name of the agent to chat with
    """
    _interactive_chat(
        agent_name=agent_name,
        chat_func=chat,
        welcome_message=f"💬 SRS Agent Interactive Chat ({agent_name})"
    )


def show_help() -> None:
    """顯示使用說明與範例查詢"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        SRS Agent - 使用說明                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  py 01_iq_agent.py create [agent_name]  - 建立新的 Agent                      ║
║  py 01_iq_agent.py chat [agent_name]    - 互動式對話                          ║
║  py 01_iq_agent.py ask <question>       - 單一問題查詢                        ║
║  py 01_iq_agent.py help                 - 顯示此說明                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                           範例查詢                                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  q1: APC account admin 於 SRS 已完成簽核,但帳號未自動化建立完成,應該如何確認? ║
║  q2: 在SRS提出帳號申請時,出現「No request data」錯誤訊息該如何處理?           ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            # Create a new agent
            name = sys.argv[2] if len(sys.argv) > 2 else None
            create_agent(name)
        elif sys.argv[1] == "chat":
            # Interactive chat mode
            agent = sys.argv[2] if len(sys.argv) > 2 else AGENT_NAME
            interactive_chat(agent)
        elif sys.argv[1] == "ask":
            # Single question mode
            if len(sys.argv) > 2:
                question = " ".join(sys.argv[2:])
                print(chat(question))
            else:
                print("Usage: py 01_iq_agent.py ask <question>")
        elif sys.argv[1] == "help":
            show_help()
        else:
            show_help()
    else:
        # Default: show help menu
        show_help()