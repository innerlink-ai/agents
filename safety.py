def is_command_safe(command: str) -> bool:
    """Returns True if the command passes the sandbox check."""
    dangerous_keywords = [
        "rm ", "shutdown", "reboot", "mkfs", ":(){", "kill", "dd if=", ">:",
        "> /dev/sd", "> /etc", "mv /", "wget ", "curl ", "nc ", "netcat", "forkbomb"
    ]
    return not any(keyword in command.lower() for keyword in dangerous_keywords)

def is_python_safe(code: str) -> bool:
    """Returns True if the Python code passes basic safety checks."""
    dangerous_patterns = [
        "os.system", "subprocess.call", "eval(", "exec(", "__import__",
        "open('/etc", "open('/dev", "rmtree", "unlink", "remove",
        "socket.", "urllib.request", "requests.post", "requests.put"
    ]
    # Allow some safe subprocess usage
    if "subprocess.run(['pip'" in code or "subprocess.run([sys.executable" in code:
        return True
    
    return not any(pattern in code for pattern in dangerous_patterns) 