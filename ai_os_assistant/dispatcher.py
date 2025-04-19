
from file_manager import rename_files, sort_files, create_file
from llm_agent import generate_code_for_action
from utils import log

def dispatch_command(intent: dict, user_prompt: str = ""):
    action = intent.get("action")

    try:
        if action == "rename_files":
            rename_files(intent["directory"], intent.get("pattern"))
        elif action == "sort_files":
            sort_files(intent["directory"], intent.get("file_type"), intent.get("group_by"))
        elif action == "create_file":
            create_file(intent["filename"], intent.get("content", ""))
        elif action == "run_code":
            code = intent.get("code", "")
            log(f"Running generated code:\n{code}")
            print("Running generated code:")
            print(code)
            safe_globals = {"__builtins__": __builtins__, "open": open, "range": range, "print": print}
            exec(code, safe_globals)
        else:
            log(f"Unknown action: {action} — falling back to LLM to generate code.")
            print(f"! Unknown action: '{action}', generating code via Ollama...")
            generated = generate_code_for_action(intent, user_prompt)
            code = generated.get("code")
            if code:
                log(f"Generated fallback code:\n{code}")
                print(code)
                safe_globals = {"__builtins__": __builtins__, "open": open, "range": range, "print": print}
                exec(code, safe_globals)
            else:
                print("!! LLM could not generate usable code.")
    except Exception as e:
        log(f"!! Error during action '{action}': {e}")
        print(f"!! Error: {e}")
