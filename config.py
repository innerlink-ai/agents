import platform
from openai import OpenAI

# ====================
# CONFIG
# ====================
MCP_HOST = "localhost"
TERMINAL_MCP_PORT = 8000
PYTHON_MCP_PORT = 8001
AI_MCP_PORT = 8002
WEB_MCP_PORT = 8003

TERMINAL_MCP_URL = f"http://{MCP_HOST}:{TERMINAL_MCP_PORT}"
PYTHON_MCP_URL = f"http://{MCP_HOST}:{PYTHON_MCP_PORT}"
AI_MCP_URL = f"http://{MCP_HOST}:{AI_MCP_PORT}"
WEB_MCP_URL = f"http://{MCP_HOST}:{WEB_MCP_PORT}"


MODEL = "gpt-4o"
MAX_RETRIES = 50






# === OpenAI client setup ===
client = OpenAI(api_key=OPENAI_API_KEY)

detected_os = platform.system()

system_prompt_body = """You are an AI agent that can execute terminal commands, Python code, web operations, and AI operations.""" 