"""
Environment Check and Connection Test Script
This script validates environment variables, tests Azure connections,
and performs a simple conversation test.
"""

import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# ========== Load Configuration ==========
credential = DefaultAzureCredential()
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
KNOWLEDGE_BASE_NAME = os.getenv("KNOWLEDGE_BASE_NAME")
PROJECT_ENDPOINT = os.getenv("AZURE_EXISTING_AIPROJECT_ENDPOINT")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4.1")

mcp_endpoint = f"{SEARCH_SERVICE_ENDPOINT}/knowledgebases/{KNOWLEDGE_BASE_NAME}/mcp?api-version=2025-11-01-preview"


def check_environment():
    """Check all required environment variables"""
    print("=" * 50)
    print("🔍 Environment Variables Check")
    print("=" * 50)

    env_vars = {
        "SEARCH_SERVICE_ENDPOINT": SEARCH_SERVICE_ENDPOINT,
        "KNOWLEDGE_BASE_NAME": KNOWLEDGE_BASE_NAME,
        "PROJECT_ENDPOINT": PROJECT_ENDPOINT,
        "AGENT_MODEL": AGENT_MODEL
    }

    all_valid = True
    for var_name, var_value in env_vars.items():
        if var_value:
            print(f"✅ {var_name}: {var_value}")
        else:
            print(f"❌ {var_name}: NOT SET")
            all_valid = False

    print(f"\n📎 MCP Endpoint: {mcp_endpoint}")
    
    return all_valid


def test_azure_credential():
    """Test Azure credential authentication"""
    print("\n" + "=" * 50)
    print("🔗 Connection Test")
    print("=" * 50)

    try:
        print("Testing Azure credential...")
        token = credential.get_token("https://management.azure.com/.default")
        print("✅ Azure credential: OK")
        return True
    except Exception as e:
        print(f"❌ Azure credential failed: {e}")
        return False


def test_project_client():
    """Test AI Project Client connection"""
    try:
        print("Testing AI Project Client connection...")
        project_client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
        print("✅ AI Project Client: OK")
        return project_client
    except Exception as e:
        print(f"❌ AI Project Client connection failed: {e}")
        return None


def run_simple_chat_test(project_client):
    """Run a simple chat test using Responses API (without MCP tools)"""
    print("\n" + "=" * 50)
    print("💬 Simple Chat Test")
    print("=" * 50)

    test_question = "請用繁體中文簡單介紹你自己,限 50 字以內"

    try:
        # Get OpenAI client with Responses API
        openai_client = project_client.get_openai_client()
        
        print(f"❓ Question: {test_question}")
        print("🔄 Processing...")

        # Use Responses API with simple chat (no tools)
        response = openai_client.responses.create(
            model=AGENT_MODEL,
            input=test_question
        )

        # Extract response text
        if response.status == "completed" and response.output:
            for item in response.output:
                if item.type == 'message' and item.content:
                    for content in item.content:
                        if hasattr(content, 'text'):
                            response_text = content.text
                            print(f"💬 Response: {response_text}")
                            print("✅ Simple chat test passed")
                            return True
        
        print(f"⚠️ Response status: {response.status}")
        return False

    except Exception as e:
        print(f"❌ Simple chat test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run all checks and tests"""
    print("\n" + "=" * 50)
    print("🧪 Environment Check & Simple Chat Test")
    print("=" * 50 + "\n")

    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Missing required environment variables. Please check your .env file.")
        return False

    # Step 2: Test Azure credential
    if not test_azure_credential():
        return False

    # Step 3: Test project client
    project_client = test_project_client()
    if not project_client:
        return False

    # Step 4: Run simple chat test
    success = run_simple_chat_test(project_client)

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    if success:
        print("✅ All tests passed!")
        print(f"🤖 Model: {AGENT_MODEL}")
        print(f"🔗 Project Endpoint: {PROJECT_ENDPOINT}")
    else:
        print("❌ Some tests failed. Please check the errors above.")

    return success


if __name__ == "__main__":
    main()
