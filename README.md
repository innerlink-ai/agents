# InnerLink AI Agent - Modular Structure

This directory contains a refactored, modular version of the InnerLink AI Agent system. The original monolithic `main.py` file has been broken down into several focused modules for better maintainability and organization.

## File Structure

```
agents/
├── __init__.py          # Package initialization and exports
├── config.py            # Configuration constants and settings
├── models.py            # Pydantic models and data structures
├── safety.py            # Safety checks and validation
├── mcp_servers.py       # MCP server implementations
├── agent.py             # Main agent logic and execution
├── setup.py             # Dependency installation and system setup
├── main_new.py          # New modular entry point
├── main.py              # Original monolithic file (for reference)
└── README.md            # This documentation
```

## Module Descriptions

### `config.py`
Contains all configuration constants including:
- MCP server URLs and ports
- OpenAI API configuration
- System prompt template
- Maximum retry settings

### `models.py`
Defines Pydantic models for type safety:
- `TerminalParams` - Parameters for terminal commands
- `PythonParams` - Parameters for Python code execution
- `ToolCall` - Unified tool call structure

### `safety.py`
Implements safety checks for both terminal commands and Python code:
- `is_command_safe()` - Validates terminal commands
- `is_python_safe()` - Validates Python code

### `mcp_servers.py`
Contains the MCP (Model Context Protocol) server implementations:
- `TerminalMCPHandler` - Handles terminal command execution
- `PythonMCPHandler` - Handles Python code execution
- Server startup functions

### `agent.py`
Core agent logic including:
- `call_openai()` - OpenAI API integration
- `call_mcp()` - MCP server communication
- `execute_single_step()` - Single step execution with retry logic
- `iterative_prompt_loop()` - Main agent workflow

### `setup.py`
System setup and dependency management:
- `install_dependencies()` - OS-specific dependency installation

### `main_new.py`
New modular entry point that orchestrates all components.

## Usage

### Running the Agent

```bash
# From the parent directory
python -m innerlink-ai.agents.main_new
```

### Using as a Library

```python
from innerlink_ai.agents import iterative_prompt_loop, install_dependencies

# Install dependencies
install_dependencies()

# Run a task
iterative_prompt_loop("List all files in the current directory")
```

### Importing Specific Components

```python
from innerlink_ai.agents.config import client, system_prompt_body
from innerlink_ai.agents.models import ToolCall
from innerlink_ai.agents.safety import is_command_safe
from innerlink_ai.agents.mcp_servers import start_terminal_mcp_server
```

## Benefits of the Refactored Structure

1. **Modularity**: Each module has a single responsibility
2. **Maintainability**: Easier to locate and modify specific functionality
3. **Testability**: Individual components can be tested in isolation
4. **Reusability**: Components can be imported and used independently
5. **Readability**: Smaller, focused files are easier to understand
6. **Extensibility**: New features can be added without modifying existing modules

## Migration from Original

The original `main.py` file is preserved for reference. The new modular structure provides the exact same functionality but with better organization. All imports and function calls have been updated to use the new structure.

## Development

When adding new features:
1. Identify the appropriate module for the new functionality
2. Add the feature to that module
3. Update `__init__.py` if new exports are needed
4. Update this README if the structure changes 