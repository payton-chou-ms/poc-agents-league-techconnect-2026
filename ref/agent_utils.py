"""
Agent Utilities - 共用模組
提供 Agent 建立與對話的共用函數，減少程式碼重複。
"""

import logging
import os
from typing import Callable

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


def setup_logging(name: str = __name__) -> logging.Logger:
    """設定並取得 logger

    Args:
        name: Logger 名稱

    Returns:
        設定好的 Logger 實例
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    
    # 降低 Azure SDK 的日誌級別,避免過多 INFO 訊息
    logging.getLogger('azure').setLevel(logging.WARNING)
    
    return logging.getLogger(name)


def get_project_client() -> AIProjectClient:
    """取得 AI Project Client

    Returns:
        已初始化的 AIProjectClient 實例

    Raises:
        ValueError: 當 AZURE_EXISTING_AIPROJECT_ENDPOINT 未設定時
    """
    endpoint = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")
    if not endpoint:
        raise ValueError("請設定 AZURE_EXISTING_AIPROJECT_ENDPOINT 環境變數")

    credential = DefaultAzureCredential()
    return AIProjectClient(endpoint=endpoint, credential=credential)


def interactive_chat(
    agent_name: str,
    chat_func: Callable[[str, str], str],
    welcome_message: str | None = None,
    example_prompts: list[str] | None = None
) -> None:
    """通用互動式對話函數

    Args:
        agent_name: Agent 名稱
        chat_func: 對話函數，接受 (question, agent_name) 並回傳回應字串
        welcome_message: 歡迎訊息（選填）
        example_prompts: 範例提示列表（選填）
    """
    logger = setup_logging("interactive_chat")

    print("\n" + "=" * 50)
    if welcome_message:
        print(welcome_message)
    else:
        print(f"💬 Agent 互動式對話 ({agent_name})")
    print("=" * 50)
    print("輸入問題開始對話，輸入 'exit' 或 'quit' 結束")
    print("=" * 50 + "\n")

    if example_prompts:
        print("💡 範例問題:")
        for prompt in example_prompts:
            print(f"  - {prompt}")
        print()

    while True:
        try:
            question = input("❓ 您的問題: ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                print("👋 再見!")
                break
            if not question:
                continue

            print("🔄 處理中...")
            response = chat_func(question, agent_name)
            print(f"\n💬 回答:\n{response}\n")
            print("-" * 50 + "\n")

        except KeyboardInterrupt:
            print("\n👋 再見!")
            break
        except Exception as e:
            logger.error("對話錯誤: %s", e)
            print(f"❌ 錯誤: {e}\n")


def get_required_env(key: str, description: str | None = None) -> str:
    """取得必要的環境變數

    Args:
        key: 環境變數名稱
        description: 環境變數描述（用於錯誤訊息）

    Returns:
        環境變數值

    Raises:
        ValueError: 當環境變數未設定時
    """
    value = os.getenv(key)
    if not value:
        desc = description or key
        raise ValueError(f"請設定 {key} 環境變數 ({desc})")
    return value
