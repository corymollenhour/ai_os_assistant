
import requests
import re
import json
from utils import log

SYSTEM_PROMPT = """You are a system automation assistant for a local Python-based OS agent.
You must respond ONLY with a JSON object. No explanations, no extra text, no code blocks. Examples:
{"action": "run_code", "code": "open('file.txt', 'w').close()"}
"""

def parse_prompt(prompt: str) -> dict:
    # data = {
    #     "model": "mistral",
    #     "messages": [
    #         {"role": "system", "content": SYSTEM_PROMPT},
    #         {"role": "user", "content": prompt}
    #     ]
    # }
    data = {
        "model": "deepseek-r1:32b",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        log(f"Sending request to Ollama with prompt: {prompt}")
        response = requests.post("http://localhost:11434/api/chat", json=data)
        response.raise_for_status()

        raw_response = response.text
        log("Raw Ollama response:\n" + raw_response)

        # Process each line of the streamed response and collect all content
        content_parts = []
        for line in raw_response.strip().splitlines():
            try:
                parsed_line = json.loads(line)
                if "message" in parsed_line and "content" in parsed_line["message"]:
                    content_parts.append(parsed_line["message"]["content"])
            except json.JSONDecodeError as e:
                log(f"Skipping invalid JSON line: {line} — {e}")

        content = "".join(content_parts)
        log(f"Reconstructed assistant content: {content}")

        # Try the simplest approach first - find the outermost JSON object
        try:
            # Look for complete JSON objects with proper start/end structure
            json_start = content.find('{')
            if json_start != -1:
                # Count braces to find the matching closing brace
                brace_count = 1
                pos = json_start + 1
                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:  # We found a complete, balanced JSON object
                    json_str = content[json_start:pos]
                    # Pre-process f-strings to protect them from JSON parser
                    # Replace f'...' or f"..." patterns temporarily
                    processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
                    return json.loads(processed_json)
        except json.JSONDecodeError as e:
            log(f"!! JSON parsing error with brace matching approach: {e}")
        
        # If that failed, try the regex approach that worked for some cases
        try:
            match = re.search(r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})', content, re.DOTALL)
            if match:
                json_str = match.group(0).strip()
                # Pre-process any f-strings
                processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
                return json.loads(processed_json)
        except json.JSONDecodeError as e:
            log(f"!! JSON parsing error with regex approach: {e} in string: {json_str}")
        
        # Final fallback - aggressively look for just the first JSON-like structure
        try:
            simple_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if simple_match:
                json_str = simple_match.group(0)
                # Pre-process any f-strings
                processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
                return json.loads(processed_json)
        except Exception as e:
            log(f"!! All JSON extraction methods failed: {e}")
            
        # If we got here, none of our approaches worked
        log("!! Could not extract valid JSON from: " + content)
        raise ValueError("No valid JSON object found in assistant's content")

    except requests.exceptions.ConnectionError:
        log("!! Ollama is not running on localhost:11434.")
        print("!! Ollama is not running on localhost:11434. Please start it by running:")
        print("ollama run deepseek-r1:32b")
    except Exception as e:
        log(f"!! LLM Error: {e}")
        print("!! LLM Error:", e)

    return {"action": "unknown"}


def generate_code_for_action(intent: dict, user_prompt: str = "") -> dict:
    # If intent looks like a preprocessed fallback from Mistral
    if intent.get("action") == "create_files" and isinstance(intent.get("filenames"), list):
        filenames = intent["filenames"]
        code_lines = [f"open('{f}', 'w').close()" for f in filenames]
        return {"action": "run_code", "code": "; ".join(code_lines)}

    # Otherwise, ask Ollama to interpret the original user request dynamically
    prompt = "You are an operating system assistant. Your job is to generate valid Python code to fulfill this user's request. Return your response as a JSON object in this format: { \"action\": \"run_code\", \"code\": \"<python code here>\" }. DO NOT include any markdown or comments. DO NOT explain your response. Just return the raw JSON." + f" User request: {user_prompt}"

    data = {
        "model": "deepseek-r1:32b",
        "messages": [
            {"role": "system", "content": "You are a code-only agent that writes cross-platform Python scripts for OS tasks."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        log(f"Asking Ollama to generate fallback code for unknown action: {intent}")
        response = requests.post("http://localhost:11434/api/chat", json=data)
        response.raise_for_status()

        content_parts = []
        for line in response.text.strip().splitlines():
            try:
                parsed_line = json.loads(line)
                if "message" in parsed_line and "content" in parsed_line["message"]:
                    content_parts.append(parsed_line["message"]["content"])
            except Exception as e:
                log(f"Skipping invalid JSON line: {e}")

        full_content = "".join(content_parts)
        log("LLM fallback code content (raw):\n" + full_content)

        # Try the simplest approach first - find the outermost JSON object
        try:
            # Look for complete JSON objects with proper start/end structure
            json_start = full_content.find('{')
            if json_start != -1:
                # Count braces to find the matching closing brace
                brace_count = 1
                pos = json_start + 1
                while pos < len(full_content) and brace_count > 0:
                    if full_content[pos] == '{':
                        brace_count += 1
                    elif full_content[pos] == '}':
                        brace_count -= 1
                    pos += 1
                
                if brace_count == 0:  # We found a complete, balanced JSON object
                    json_str = full_content[json_start:pos]
                    # Pre-process f-strings to protect them from JSON parser
                    # Replace f'...' or f"..." patterns temporarily
                    processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
                    parsed = json.loads(processed_json)
                    if parsed.get("action") == "run_code" and "code" in parsed:
                        return parsed
                    else:
                        log("! Parsed response was not valid 'run_code' format.")
        except json.JSONDecodeError as e:
            log(f"!! JSON parsing error with brace matching approach in generate_code_for_action: {e}")
        
        # If that failed, try the regex approach
        try:
            match = re.search(r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})', full_content, re.DOTALL)
            if match:
                json_str = match.group(0).strip()
                # Pre-process any f-strings
                processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
                parsed = json.loads(processed_json)
                if parsed.get("action") == "run_code" and "code" in parsed:
                    return parsed
                else:
                    log("! Parsed response was not valid 'run_code' format.")
        except json.JSONDecodeError as e:
            log(f"!! JSON parsing error with regex approach in generate_code_for_action: {e}")
        
        # Final fallback - aggressively look for just the first JSON-like structure
        try:
            simple_match = re.search(r'\{.*?\}', full_content, re.DOTALL)
            if simple_match:
                json_str = simple_match.group(0)
                # Pre-process any f-strings
                processed_json = re.sub(r"f(['\"])(.*?)\1", r"\1\2\1", json_str)
                parsed = json.loads(processed_json)
                if parsed.get("action") == "run_code" and "code" in parsed:
                    return parsed
        except Exception as e:
            log(f"!! All JSON extraction methods failed in generate_code_for_action: {e}")
        
        log("! No valid JSON object found in fallback code response.")

    except Exception as e:
        log(f"!! Failed to generate fallback code: {e}")

    return {"action": "unknown"}
