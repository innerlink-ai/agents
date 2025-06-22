#!/usr/bin/env python3
"""
Example usage of the refactored InnerLink AI Agent modules.

This script demonstrates how to use the individual components
of the modular agent system.
"""

def example_basic_usage():
    """Example of basic usage using the high-level interface."""
    print("=== Basic Usage Example ===")
    
    from . import iterative_prompt_loop, install_dependencies
    
    # Install system dependencies
    print("Installing dependencies...")
    install_dependencies()
    
    # Run a simple task
    print("Running a simple task...")
    iterative_prompt_loop("List all files in the current directory")

def example_component_usage():
    """Example of using individual components."""
    print("\n=== Component Usage Example ===")
    
    from .config import client, system_prompt_body
    from .models import TerminalParams, PythonParams
    from .safety import is_command_safe, is_python_safe
    from .agent import call_openai, call_mcp
    
    # Test safety functions
    print("Testing safety functions:")
    print(f"  'ls -la' is safe: {is_command_safe('ls -la')}")
    print(f"  'rm -rf /' is safe: {is_command_safe('rm -rf /')}")
    print(f"  'print(\"hello\")' is safe: {is_python_safe('print(\"hello\")')}")
    print(f"  'os.system(\"rm -rf /\")' is safe: {is_python_safe('os.system(\"rm -rf /\")')}")
    
    # Create model instances
    print("\nCreating model instances:")
    terminal_params = TerminalParams(
        command="echo 'Hello from terminal'",
        description="Print a greeting from terminal"
    )
    print(f"  Terminal params: {terminal_params}")
    
    python_params = PythonParams(
        code="print('Hello from Python')",
        description="Print a greeting from Python"
    )
    print(f"  Python params: {python_params}")

def example_custom_integration():
    """Example of custom integration with the agent system."""
    print("\n=== Custom Integration Example ===")
    
    from .config import client
    from .models import ToolCall, TerminalParams
    from .agent import call_mcp
    
    # Example of how you might integrate with your own system
    print("Example custom integration:")
    print("  - OpenAI client available for custom API calls")
    print("  - MCP servers can be called directly")
    print("  - Safety functions available for validation")
    print("  - Models available for type-safe data handling")

if __name__ == "__main__":
    print("🚀 InnerLink AI Agent - Example Usage\n")
    
    # Run examples
    example_component_usage()
    example_custom_integration()
    
    print("\n" + "="*50)
    print("To run the full agent with the new modular structure:")
    print("  python -m agents.main_new")
    print("="*50) 