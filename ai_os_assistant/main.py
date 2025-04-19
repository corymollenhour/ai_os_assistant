
from llm_agent import parse_prompt
from dispatcher import dispatch_command
from command_store import CommandStore
from utils import log

def main():
    log("Assistant started.")
    print("AI OS Assistant. Type a command or 'exit' to quit.")
    print("Special commands:")
    print("  - 'store last': Store the last command as a pattern")
    print("  - 'no store': Execute the next command without storing it")
    print("  - 'clear patterns': Clear all stored command patterns")
    
    # Initialize the command store
    command_store = CommandStore()
    last_prompt = ""
    last_intent = None
    skip_next_store = False

    while True:
        prompt = input("> ")
        if prompt.lower() in ["exit", "quit"]:
            log("Assistant exited by user.")
            break
        
        # Special command to store the last command as a pattern
        if prompt.lower() == "store last":
            if last_prompt and last_intent:
                log(f"Storing command as pattern: {last_prompt}")
                command_store.add_pattern(last_prompt, last_intent, store_command=True)
                continue
            else:
                print("No previous command to store.")
                continue
        
        # Special command to skip storing the next command
        if prompt.lower() == "no store":
            skip_next_store = True
            print("Next command will not be stored as a pattern.")
            continue
        
        # Special command to clear all patterns
        if prompt.lower() == "clear patterns":
            command_store.patterns = {}
            command_store.save_patterns()
            print("✅ All command patterns cleared.")
            continue

        log(f"User prompt: {prompt}")
        
        # Check if the command matches a stored pattern
        match_result = command_store.match_command(prompt)
        
        if match_result:
            intent, variables = match_result
            category = command_store.detect_category(prompt)
            log(f"Matched command pattern in category '{category}'. Variables: {variables}")
            
            # Show variables if any were extracted
            if variables:
                var_display = ", ".join([f"{k}='{v}'" for k, v in variables.items()])
                print(f"🔍 Recognized command pattern in category '{category}' with variables: {var_display}")
            else:
                print(f"🔍 Recognized similar command in category '{category}'")
            
            # Flag that this intent came from a pattern
            from_pattern = True
        else:
            # No match found, use LLM to parse the prompt
            intent = parse_prompt(prompt)
            log(f"LLM returned intent: {intent}")
            
            # Store the command and intent for future use
            last_prompt = prompt
            last_intent = intent
            
            # Store all commands by default unless skipped
            if not skip_next_store:
                command_store.add_pattern(prompt, intent, store_command=True)
            else:
                print("Command not stored as requested.")
                skip_next_store = False
                
            # Flag that this intent came from the LLM
            from_pattern = False
        
        # Dispatch the command
        dispatch_command(intent, prompt, from_pattern)

if __name__ == "__main__":
    main()
