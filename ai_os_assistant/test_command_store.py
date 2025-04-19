import os
import json
from command_store import CommandStore
from utils import log

def test_pattern_matching():
    # Create a test command store
    store = CommandStore()
    
    # Override the store file for testing
    store.patterns = {}
    
    # Add a file creation pattern
    create_file_command = "Create a file named test.txt"
    create_file_intent = {
        "action": "create_file",
        "filename": "test.txt"
    }
    store.add_pattern(create_file_command, create_file_intent, store_command=True)
    
    # Add a code pattern for file creation
    code_command = "Make me a file called data.csv"
    code_intent = {
        "action": "run_code",
        "code": "open('data.csv', 'w').close()"
    }
    store.add_pattern(code_command, code_intent, store_command=True)
    
    # Test matching existing patterns
    print("\n--- Testing pattern matching ---")
    
    # Test file creation pattern
    new_command = "Create a file named report.docx"
    match_result = store.match_command(new_command)
    
    if match_result:
        intent, variables = match_result
        print(f"✅ Matched: {new_command}")
        print(f"  Intent: {intent}")
        print(f"  Variables: {variables}")
    else:
        print(f"❌ Failed to match: {new_command}")
    
    # Test code pattern
    new_code_command = "Make me a file called users.json"
    match_result = store.match_command(new_code_command)
    
    if match_result:
        intent, variables = match_result
        print(f"✅ Matched: {new_code_command}")
        print(f"  Intent: {intent}")
        print(f"  Variables: {variables}")
    else:
        print(f"❌ Failed to match: {new_code_command}")
    
    # Test non-matching command
    non_matching = "Delete all files in the tmp directory"
    match_result = store.match_command(non_matching)
    
    if not match_result:
        print(f"✅ Correctly did not match: {non_matching}")
    else:
        print(f"❌ Incorrectly matched: {non_matching}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    # Delete the command pattern file if it exists (for clean testing)
    if os.path.exists("command_patterns.json"):
        temp_filename = "command_patterns_backup.json"
        # Backup existing patterns
        try:
            with open("command_patterns.json", 'r') as src, open(temp_filename, 'w') as dst:
                dst.write(src.read())
            print(f"Backed up existing patterns to {temp_filename}")
        except Exception as e:
            print(f"Warning: Could not backup patterns: {e}")
    
    try:
        test_pattern_matching()
    finally:
        # Restore the original patterns file if it was backed up
        if os.path.exists("command_patterns_backup.json"):
            try:
                with open("command_patterns_backup.json", 'r') as src, open("command_patterns.json", 'w') as dst:
                    dst.write(src.read())
                os.remove("command_patterns_backup.json")
                print("Restored original patterns file")
            except Exception as e:
                print(f"Warning: Could not restore patterns: {e}")