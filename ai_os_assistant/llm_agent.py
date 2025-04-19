
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

        # Extract first JSON-like block from the content using a more precise pattern
        # Look for standalone JSON objects or ones with proper JSON formatting
        match = re.search(r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})', content, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in assistant's content")
        
        # Get the JSON string and clean it
        json_str = match.group(0).strip()
        
        try:
            # Try to parse the extracted JSON
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            log(f"!! JSON parsing error: {e} in string: {json_str}")
            # Fall back to a simpler extract if the complex regex fails
            simple_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if simple_match:
                try:
                    return json.loads(simple_match.group(0))
                except:
                    pass
            raise

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

        json_start = full_content.find('{')
        json_end = full_content.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = full_content[json_start:json_end]
            parsed = json.loads(json_str)
            if parsed.get("action") == "run_code" and "code" in parsed:
                return parsed
            else:
                log("! Parsed response was not valid 'run_code' format.")
        else:
            log("! No complete JSON object found.")

    except Exception as e:
        log(f"!! Failed to generate fallback code: {e}")

    return {"action": "unknown"}
