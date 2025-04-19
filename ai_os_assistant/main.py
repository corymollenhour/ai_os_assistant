
from llm_agent import parse_prompt
from dispatcher import dispatch_command
from command_store import CommandStore
from utils import log

def main():
    log("Assistant started.")
    print("AI OS Assistant. Type a command or 'exit' to quit.")
    print("Special commands:")
    print("  - 'store last': Store the last command as a pattern")
    print("  - 'clear patterns': Clear all stored command patterns")
    
    # Initialize the command store
    command_store = CommandStore()
    last_prompt = ""
    last_intent = None

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
            log(f"Matched command pattern. Variables: {variables}")
            print(f"🔍 Recognized command pattern (skipping LLM call)")
            # Flag that this intent came from a pattern
            from_pattern = True
        else:
            # No match found, use LLM to parse the prompt
            intent = parse_prompt(prompt)
            log(f"LLM returned intent: {intent}")
            
            # Store the command and intent for potential later storage
            last_prompt = prompt
            last_intent = intent
            
            # Automatically identify and store certain command patterns
            command_store.add_pattern(prompt, intent, store_command=False)
            # Flag that this intent came from the LLM
            from_pattern = False
        
        # Dispatch the command
        dispatch_command(intent, prompt, from_pattern)

if __name__ == "__main__":
    main()
