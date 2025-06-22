import json
import subprocess
import os
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from safety import is_command_safe, is_python_safe
import json
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import quote_plus
import re

from openai import OpenAI
import os


# ====================
# TERMINAL MCP SERVER
# ====================
class TerminalMCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress access logs
        pass
        
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        response = self.handle_json_rpc(body)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def handle_json_rpc(self, body):
        try:
            request = json.loads(body)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "tools/list":
                # Return list of available terminal tools
                tools = [
                    {
                        "name": "terminal.execute",
                        "description": "Execute terminal commands",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string", "description": "Terminal command to execute"},
                                "description": {"type": "string", "description": "Description of what the command does"}
                            },
                            "required": ["command"]
                        }
                    }
                ]
                return json.dumps({"jsonrpc": "2.0", "result": {"tools": tools}, "id": request_id})

            elif method == "terminal.execute":
                command = params.get("command")
                result = self.execute_command(command)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                })

        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": None
            })

    def execute_command(self, command):
        if not is_command_safe(command):
            return {
                "stdout": "",
                "stderr": "Blocked for safety: command contains potentially dangerous keywords.",
                "returncode": 1
            }

        try:
            command = command.replace("~", os.path.expanduser("~"))
            completed = subprocess.run(command, shell=True, text=True, capture_output=True)

            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            returncode = completed.returncode

            response = {
                "stdout": stdout if stdout else "<EMPTY STDOUT>",
                "stderr": stderr if stderr else "<EMPTY STDERR>",
                "returncode": returncode,
            }
            if not stdout and not stderr:
                response["stderr"] = (
                    "The command produced no output or error message, revise the command."
                )
            return response
        except Exception as e:
            return {"error": str(e)}

# ====================
# PYTHON MCP SERVER
# ====================
class PythonMCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress access logs
        pass
        
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        response = self.handle_json_rpc(body)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def handle_json_rpc(self, body):
        try:
            request = json.loads(body)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "tools/list":
                # Return list of available Python tools
                tools = [
                    {
                        "name": "python.execute",
                        "description": "Execute Python code",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string", "description": "Python code to execute"},
                                "description": {"type": "string", "description": "Description of what the code does"}
                            },
                            "required": ["code"]
                        }
                    }
                ]
                return json.dumps({"jsonrpc": "2.0", "result": {"tools": tools}, "id": request_id})

            elif method == "python.execute":
                code = params.get("code")
                result = self.execute_python(code)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                })

        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": None
            })

    def execute_python(self, code):
        if not is_python_safe(code):
            return {
                "stdout": "",
                "stderr": "Blocked for safety: code contains potentially dangerous operations.",
                "returncode": 1
            }

        try:
            # Create a temporary file for the Python code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # Execute the Python code
            completed = subprocess.run([sys.executable, temp_file], 
                                     text=True, capture_output=True, cwd=os.getcwd())

            # Clean up
            os.unlink(temp_file)

            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            returncode = completed.returncode

            response = {
                "stdout": stdout if stdout else "<EMPTY STDOUT>",
                "stderr": stderr if stderr else "<EMPTY STDERR>", 
                "returncode": returncode,
            }
            
            return response
            
        except Exception as e:
            return {"error": str(e), "returncode": 1}




class WebMCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress access logs
        pass
        
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        response = self.handle_json_rpc(body)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def handle_json_rpc(self, body):
        try:
            request = json.loads(body)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "tools/list":
                # Return list of available web tools
                tools = [
                    {
                        "name": "web.fetch",
                        "description": "Fetch content from any URL",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "URL to fetch content from"}
                            },
                            "required": ["url"]
                        }
                    },
                    {
                        "name": "web.search",
                        "description": "Search the web for information",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "web.post",
                        "description": "Send POST request to a URL",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "URL to post to"},
                                "data": {"type": "object", "description": "Data to send"},
                                "headers": {"type": "object", "description": "HTTP headers"}
                            },
                            "required": ["url"]
                        }
                    }
                ]
                return json.dumps({"jsonrpc": "2.0", "result": {"tools": tools}, "id": request_id})

            elif method == "web.fetch":
                url = params.get("url")
                result = self.web_fetch(url)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            
            elif method == "web.search":
                query = params.get("query")
                result = self.web_search(query)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            
            elif method == "web.post":
                url = params.get("url")
                data = params.get("data", {})
                headers = params.get("headers", {})
                result = self.web_post(url, data, headers)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                })

        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": request_id
            })

    def web_fetch(self, url):
        """Generic web content fetcher"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            content = response.text
            
            # Extract useful information based on content type
            if "job" in url.lower() or "career" in url.lower():
                content = self.extract_job_info(content)
            elif "news" in url.lower() or "article" in url.lower():
                content = self.extract_article_info(content)
            elif "weather" in url.lower():
                content = self.extract_weather_info(content)
            else:
                # Generic content extraction
                content = self.extract_generic_info(content)
            
            return {
                "url": url,
                "status_code": response.status_code,
                "content": content[:8000],  # Limit content size
                "content_length": len(content),
                "returncode": 0
            }
            
        except Exception as e:
            return {"url": url, "error": str(e), "returncode": 1}

    def web_search(self, query):
        """Generic web search using DuckDuckGo"""
        try:
            # Use DuckDuckGo instant answer API
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            # Extract relevant info
            results = []
            
            # Main answer
            if data.get("Abstract"):
                results.append({
                    "title": data.get("AbstractSource", ""),
                    "snippet": data.get("Abstract", ""),
                    "url": data.get("AbstractURL", "")
                })
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append({
                        "title": topic.get("FirstURL", "").split("/")[-1] if topic.get("FirstURL") else "",
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", "")
                    })
            
            return {
                "query": query,
                "results": results,
                "returncode": 0
            }
            
        except Exception as e:
            return {"query": query, "error": str(e), "returncode": 1}

    def web_post(self, url, data, headers):
        """Generic POST request handler"""
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            return {
                "url": url,
                "status_code": response.status_code,
                "content": response.text[:2000],
                "returncode": 0
            }
            
        except Exception as e:
            return {"url": url, "error": str(e), "returncode": 1}


    def extract_generic_info(self, html):
        """Generic content extraction for any webpage"""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract text from common content areas
        patterns = [
            r'<h[1-6][^>]*>([^<]*)</h[1-6]>',
            r'<p[^>]*>(.*?)</p>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*main[^"]*"[^>]*>(.*?)</div>',
            r'<article[^>]*>(.*?)</article>',
            r'<section[^>]*>(.*?)</section>'
        ]
        
        extracted = []
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for match in matches[:2]:  # Limit matches per pattern
                # Clean up the extracted text
                clean_text = re.sub(r'<[^>]+>', '', match)  # Remove HTML tags
                clean_text = re.sub(r'\s+', ' ', clean_text)  # Normalize whitespace
                clean_text = clean_text.strip()
                if len(clean_text) > 20:  # Only keep substantial content
                    extracted.append(clean_text)
        
        if extracted:
            return "\n\n".join(extracted[:10])  # Limit to 10 extracts
        else:
            # Last resort: extract any text content
            text_content = re.sub(r'<[^>]+>', '', html)
            text_content = re.sub(r'\s+', ' ', text_content)
            return text_content[:2000]  # Limit to 2000 characters



class AIMCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress access logs
        pass
        
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        response = self.handle_json_rpc(body)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def handle_json_rpc(self, body):
        try:
            request = json.loads(body)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "tools/list":
                # Return list of available AI tools
                tools = [
                    {
                        "name": "ai.summarize",
                        "description": "Summarize text using AI",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Text to summarize"},
                                "style": {"type": "string", "enum": ["professional", "bullet_points", "brief"], "default": "professional"}
                            },
                            "required": ["text"]
                        }
                    },
                    {
                        "name": "ai.analyze",
                        "description": "Analyze text for specific information",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Text to analyze"},
                                "type": {"type": "string", "enum": ["skills", "sentiment", "keywords", "structure", "general"], "default": "general"}
                            },
                            "required": ["text"]
                        }
                    },
                    {
                        "name": "ai.generate",
                        "description": "Generate text based on prompt",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "Prompt for text generation"}
                            },
                            "required": ["prompt"]
                        }
                    }
                ]
                return json.dumps({"jsonrpc": "2.0", "result": {"tools": tools}, "id": request_id})

            elif method == "ai.summarize":
                text = params.get("text")
                style = params.get("style", "professional")
                result = self.summarize_text(text, style)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            
            elif method == "ai.analyze":
                text = params.get("text")
                analysis_type = params.get("type", "general")
                result = self.analyze_text(text, analysis_type)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            
            elif method == "ai.generate":
                prompt = params.get("prompt")
                result = self.generate_text(prompt)
                return json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            
            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                })

        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": request_id
            })

    def summarize_text(self, text, style="professional"):
        """Summarize text using OpenAI API"""
        if style == "professional":
            prompt = f"Provide a professional 2-3 sentence summary:\n\n{text}"
        elif style == "bullet_points":
            prompt = f"Create bullet-point summary:\n\n{text}"
        elif style == "brief":
            prompt = f"Summarize in 1 sentence:\n\n{text}"
        else:
            prompt = f"Summarize this text:\n\n{text}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "summary": summary,
                "style": style,
                "returncode": 0
            }
            
        except Exception as e:
            return {"error": str(e), "returncode": 1}

    def analyze_text(self, text, analysis_type="general"):
        """Analyze text for specific information"""
        prompts = {
            "skills": f"Extract all technical skills and categorize them:\n\n{text}",
            "sentiment": f"Analyze the sentiment and tone of this text:\n\n{text}",
            "keywords": f"Extract the most important keywords and topics:\n\n{text}",
            "structure": f"Analyze the structure and organization of this content:\n\n{text}",
            "general": f"Provide a detailed analysis of this text:\n\n{text}"
        }
        
        prompt = prompts.get(analysis_type, prompts["general"])
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                "analysis": analysis,
                "type": analysis_type,
                "returncode": 0
            }
            
        except Exception as e:
            return {"error": str(e), "returncode": 1}

    def generate_text(self, prompt):
        """Generate text based on prompt"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            return {
                "text": generated_text,
                "returncode": 0
            }
            
        except Exception as e:
            return {"error": str(e), "returncode": 1}


def start_ai_server(host="localhost", port=8002):
    server = HTTPServer((host, port), AIMCPHandler)
    print(f"[AI MCP] Running at http://{host}:{port}")
    server.serve_forever()



def start_web_server(host="localhost", port=8003):
    server = HTTPServer((host, port), WebMCPHandler)
    print(f"[Web MCP] Running at http://{host}:{port}")
    server.serve_forever()


def start_terminal_mcp_server(host="localhost", port=8000):
    server = HTTPServer((host, port), TerminalMCPHandler)
    print(f"[TERMINAL MCP] Running at http://{host}:{port}")
    server.serve_forever()

def start_python_mcp_server(host="localhost", port=8001):
    server = HTTPServer((host, port), PythonMCPHandler)
    print(f"[PYTHON MCP] Running at http://{host}:{port}")
    server.serve_forever() 