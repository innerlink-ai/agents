import requests
from config import client, system_prompt_body, MAX_RETRIES, TERMINAL_MCP_URL, PYTHON_MCP_URL, AI_MCP_URL, WEB_MCP_URL
from models import ToolCall
from safety import is_command_safe, is_python_safe

def call_openai(prompt: str) -> dict:
    """Call OpenAI API to get the next tool call."""
    response_text = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": system_prompt_body},
            {"role": "user", "content": prompt}
        ],
        text_format=ToolCall,
        temperature=0
    )

    tool_call = response_text.output_parsed
    try:
        if tool_call.method == "python.execute":
            return {
                "method": tool_call.method,
                "params": {
                    "code": tool_call.params.code,
                    "description": tool_call.params.description,
                }
            }
        else:  # terminal.execute
            return {
                "method": tool_call.method,
                "params": {
                    "command": tool_call.params.command,
                    "description": tool_call.params.description,
                }
            }
    except Exception as e:
        raise ValueError(f"Failed to parse model output: {e}\nOutput:\n{response_text}")

def call_mcp(method: str, params: dict) -> dict:
    """Call the appropriate MCP server with the given method and parameters."""
    # Route to appropriate MCP server
    if method == "python.execute":
        url = PYTHON_MCP_URL
    elif method.startswith("ai."):
        url = AI_MCP_URL
    else:
        url = TERMINAL_MCP_URL
        
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    res = requests.post(url, json=payload)
    response_json = res.json()
    
    # Handle both success and error responses
    if "result" in response_json:
        return response_json["result"]
    elif "error" in response_json:
        return {"error": response_json["error"]["message"], "returncode": 1}
    else:
        return {"error": "Invalid response format", "returncode": 1}

def execute_single_step(prompt: str):
    """Execute a single step with retry logic for both Python and Terminal."""
    context = []
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Add structured memory to the prompt if retrying
            if context:
                retry_prompt = (
                    f"The previous command failed. Here is the history:\n\n"
                    + "\n\n".join([
                        f"Attempt {i+1}:\n"
                        f"Method: {step['method']}\n"
                        f"Command/Code: {step['command']}\n"
                        f"Return Code: {step['returncode']}\n"
                        f"STDOUT:\n{step['stdout']}\n"
                        f"STDERR:\n{step['stderr']}"
                        for i, step in enumerate(context)
                    ])
                    + f"\n\nPlease suggest a corrected approach for:\n\"{prompt}\""
                )
            else:
                retry_prompt = prompt

            tool_call = call_openai(retry_prompt)
            method = tool_call["method"]
            params = tool_call["params"]

            print(f"\n[STEP] Attempt {attempt}")
            if method == "python.execute":
                print(f"[STEP] 🐍 Python Code:")
                print(f"[STEP] Description: {params.get('description', 'No description')}")
                # Show first few lines of code
                code_lines = params['code'].strip().split('\n')
                for i, line in enumerate(code_lines[:5]):
                    print(f"      {i+1}: {line}")
                if len(code_lines) > 5:
                    print(f"      ... ({len(code_lines)-5} more lines)")
                
                if not is_python_safe(params["code"]):
                    print("[BLOCKED] Python code contains dangerous operations")
                    return False, {"method": method, "command": params["code"], "output": "Code blocked for safety"}
            elif method.startswith("ai."):
                print(f"[STEP] 🤖 AI {method.split('.')[1].title()}:")
                print(f"[STEP] Description: {params.get('description', 'No description')}")
            else:
                print(f"[STEP] 🖥️ Terminal Command: {params['command']}")
                print(f"[STEP] Description: {params.get('description', 'No description')}")
                
                if not is_command_safe(params["command"]):
                    print("[BLOCKED] Command contains dangerous keywords")
                    return False, {"method": method, "command": params["command"], "output": "Command blocked for safety"}

            # Check if this is a TASK_COMPLETE command and auto-execute
            if method == "terminal.execute" and "TASK_COMPLETE" in params.get("command", ""):
                proceed = "y"
                print("Auto-executing TASK_COMPLETE command...")
            else:
                proceed = input("Execute this? (y/n): ").strip().lower()
                if proceed != "y":
                    print("Execution skipped by user")
                    return False, {"method": method, "command": params.get("command", params.get("code", "")), "output": "Skipped by user"}

            result = call_mcp(method, params)

            context.append({
                "method": method,
                "command": _get_command_display(method, params),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", "") or result.get("error", ""),
                "returncode": result.get("returncode", 1),
            })

            if result.get("returncode", 1) == 0:
                print("[✅ STEP SUCCESS]")
                output = result.get("stdout", "").strip() or result.get("content", "").strip() or result.get("summary", "").strip()
                print("[OUTPUT]")
                for line in output.splitlines()[:10]:  # Show first 10 lines
                    print(f"  {line}")
                if len(output.splitlines()) > 10:
                    print("  ...")
                
                return True, {
                    "method": method,
                    "command": _get_command_display(method, params),
                    "output": output,
                    "description": params.get("description", "")
                }
            else:
                print("[❌ STEP FAILURE]")
                print(result.get("stderr", "").strip())

        except Exception as e:
            print(f"[ERROR] {e}")
            return False, {"method": "", "command": "", "output": f"Error: {e}"}
    
    print("⚠️ Step failed after all retry attempts")
    return False, {"method": "", "command": "", "output": "Failed after all retries"}

def _get_command_display(method, params):
    """Get a display string for the command based on method type"""
    if method == "python.execute":
        return params.get("code", "")[:100]
    elif method == "terminal.execute":
        return params.get("command", "")
    elif method.startswith("ai."):
        return f"{method}({params.get('text', params.get('prompt', ''))[:50]})"
    else:
        return str(params)[:100]

def discover_available_tools():
    """Discover tools from all MCP servers"""
    tools = {}
    endpoints = {
        "terminal": TERMINAL_MCP_URL,
        "python": PYTHON_MCP_URL, 
        "ai": AI_MCP_URL
    }
    
    for server, url in endpoints.items():
        try:
            payload = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
            response = requests.post(url, json=payload, timeout=5)
            server_tools = response.json()["result"]["tools"]
            for tool in server_tools:
                tools[tool["name"]] = {
                    "url": url,
                    "description": tool["description"],
                    "schema": tool["inputSchema"]
                }
            #print(f"✅ {server} server: {len(server_tools)} tools available")
        except Exception as e:
            print(f"❌ {server} server not available: {e}")
    
    #print(f"Total tools discovered: {len(tools)}")
    return tools

def iterative_prompt_loop(user_prompt: str, full_conversation_context=""):
    """Enhanced version with Python and Terminal execution capabilities."""
    print(f"\n[AGENT] Starting work on: {user_prompt}")
    
    conversation_history = []
    step_count = 0
    max_steps = 10
    consecutive_skips = 0
    
    while step_count < max_steps:
        step_count += 1
        print(f"\n{'='*50}")
        print(f"[AGENT] Step {step_count}")
        print(f"{'='*50}")
        
        # Build comprehensive context
        context_parts = []
        
        # Discover available tools and add to context
        available_tools = discover_available_tools()
        tool_list = "\n".join([f"- {name}: {info['description']}" for name, info in available_tools.items()])
        context_parts.append(f"AVAILABLE TOOLS:\n{tool_list}")
        
        if full_conversation_context:
            context_parts.append(f"FULL CONVERSATION HISTORY:\n{full_conversation_context}")
        
        if conversation_history:
            recent_steps = "\n".join([
                f"Step {i+1}: {step['method']} -> {step['command'][:50]}... -> {'SUCCESS' if step['success'] else 'SKIPPED/FAILED'}\n"
                f"Result: {step['output'][:200]}{'...' if len(step['output']) > 200 else ''}"
                for i, step in enumerate(conversation_history[-3:])
            ])
            context_parts.append(f"RECENT STEPS:\n{recent_steps}")
        
        # Build the prompt with full context
        if context_parts:
            next_prompt = f"""
{chr(10).join(context_parts)}

CURRENT TASK: "{user_prompt}"

Based on ALL the context above, what should be the next action?

IMPORTANT GUIDELINES:
🔍 Use web.search for:
- Searching the web for information
- Finding facts, news, or general information
- Research tasks

🐍 Use python.execute for:
- Data analysis, text processing, summarization
- File parsing (PDF, CSV, JSON, etc.)
- Complex calculations or algorithms
- AI/ML tasks, web scraping, API calls
- When you need libraries like pandas, requests, PyPDF2, etc.

🖥️ Use terminal.execute for:
- File system operations (ls, find, mkdir, etc.)
- System information (ps, df, etc.)
- Installing packages or tools
- Basic text operations with standard Unix tools
- Web content retrieval using curl, wget, etc.

🤖 Use ai.summarize for:
- Summarizing text content
- Analyzing job postings, articles, documents

- If the user has been skipping commands repeatedly, try a completely different approach
- If the task seems complete, respond with: echo "TASK_COMPLETE: [summary]" (using terminal.execute)

Provide the next appropriate action:
"""
        else:
            next_prompt = user_prompt
        

        # Get the next command
        success, command_info = execute_single_step(next_prompt)
        
        # Track consecutive skips
        if not success and "Skipped by user" in command_info.get("output", ""):
            consecutive_skips += 1
        else:
            consecutive_skips = 0
        
        # Store the step in history
        conversation_history.append({
            "method": command_info.get("method", ""),
            "command": command_info.get("command", "")[:100],  # Truncate long code
            "success": success,
            "output": command_info.get("output", ""),
            "skipped": "Skipped by user" in command_info.get("output", "")
        })
        
        # Check for exit conditions
        if "TASK_COMPLETE" in command_info.get("output", ""):
            print(f"\n[AGENT] ✅ Task completed after {step_count} steps!")
            print(f"[AGENT] {command_info.get('output', '')}")
            break
        
        # Check if the task was successful and should be considered complete
        if success and command_info.get("output", ""):
            output = command_info.get("output", "").lower()
            # Check for common success indicators
            if any(indicator in output for indicator in [
                "opened", "found", "located", "successfully", "completed", "done"
            ]):
                # If this looks like a successful completion, ask user
                print(f"\n[AGENT] 🤔 This step was successful. Does this complete your task?")
                user_response = input("[AGENT] Task complete? (y/n): ").strip().lower()
                if user_response == 'y':
                    print(f"\n[AGENT] ✅ Task completed after {step_count} steps!")
                    break
        
        # Exit if too many consecutive skips
        if consecutive_skips >= 1:
            print(f"\n[AGENT] ⚠️ User has skipped command.")
            user_choice = input("[AGENT] Continue trying (c), give up (g), or provide guidance (h)? ").strip().lower()
            if user_choice == 'g':
                print("[AGENT] Giving up on this task.")
                break
            elif user_choice == 'h':
                guidance = input("[AGENT] What would you like me to try instead? ")
                if guidance:
                    full_conversation_context += f"\nUSER GUIDANCE: {guidance}"
                consecutive_skips = 0
            elif user_choice == 'c':
                consecutive_skips = 0
                print("[AGENT] Continuing with a different approach...")
        
        print(f"[AGENT] Continuing to next step...")
    
    if step_count >= max_steps:
        print(f"\n[AGENT] ⚠️ Reached maximum steps ({max_steps}). Task may not be complete.")
    
    print(f"\n[AGENT] Final summary:")
    for i, step in enumerate(conversation_history):
        if step["skipped"]:
            status = "⏭️"
        elif step["success"]:
            status = "✅"
        else:
            status = "❌"
        method_icon = "🐍" if step["method"] == "python.execute" else "🖥️"
        print(f"  Step {i+1}: {status} {method_icon} {step['command']}") 