import threading
import time

from mcp_servers import start_terminal_mcp_server, start_python_mcp_server, start_ai_server
from agent import iterative_prompt_loop
from config import MCP_HOST, TERMINAL_MCP_PORT, PYTHON_MCP_PORT, AI_MCP_PORT

def main():
    """Main entry point for the InnerLink AI Agent."""
    
    # Start all MCP servers
    terminal_thread = threading.Thread(
        target=start_terminal_mcp_server, 
        args=(MCP_HOST, TERMINAL_MCP_PORT), 
        daemon=True
    )
    python_thread = threading.Thread(
        target=start_python_mcp_server, 
        args=(MCP_HOST, PYTHON_MCP_PORT), 
        daemon=True
    )
    ai_thread = threading.Thread(
        target=start_ai_server,
        args=(MCP_HOST, AI_MCP_PORT),
        daemon=True
    )
    
    terminal_thread.start()
    python_thread.start()
    ai_thread.start()
    
    time.sleep(2)  # Give servers time to start


    full_conversation = ""

    while True:
        print("\n\n[AGENT] Tell me what to do. I can execute terminal commands, Python code, and AI operations")
        print("[AGENT] Commands: 'e' to exit, 'n' to start fresh conversation")

        user_input = input(">")
        if user_input.lower() in {"exit", "quit", "e"}:
            print("Goodbye!")
            break
        if user_input.lower() in {""}:
            continue
        if user_input.lower() =='n':
            full_conversation=""
            continue
        full_conversation += f"\nUser: {user_input}"
        iterative_prompt_loop(user_input, full_conversation)
        full_conversation += f"\n[Task attempted: {user_input}]"

if __name__ == "__main__":
    main() 