"""
InnerLink AI Agent Package

A modular AI agent system that can execute both terminal commands and Python code
through MCP (Model Context Protocol) servers.
"""

from .agent import iterative_prompt_loop, execute_single_step
from .config import client, system_prompt_body
from .models import ToolCall, TerminalParams, PythonParams
from .mcp_servers import start_terminal_mcp_server, start_python_mcp_server
from .safety import is_command_safe, is_python_safe


__version__ = "1.0.0"
__author__ = "InnerLink AI"

__all__ = [
    "iterative_prompt_loop",
    "execute_single_step", 
    "client",
    "system_prompt_body",
    "ToolCall",
    "TerminalParams",
    "PythonParams",
    "start_terminal_mcp_server",
    "start_python_mcp_server",
    "is_command_safe",
    "is_python_safe",
    "install_dependencies"
] 