import os
import json
from command_store import CommandStore
from utils import log

def test_enhanced_pattern_matching():
    """Test the enhanced command pattern matching system."""
    # Create a test command store
    store = CommandStore()
    
    # Override the store patterns for testing
    store.patterns = {}
    
    print("\n=== Testing Command Pattern Storage and Matching ===\n")
    
    # Test 1: Auto-categorization
    print("--- Test 1: Command Categorization ---")
    test_commands = [
        "Open my default browser to www.example.com",
        "Create a file named report.txt",
        "Search for the best pizza recipes",
        "Launch Notepad and open the config file",
        "Delete all files in the temp directory",
        "Rename file data.csv to data_old.csv"
    ]
    
    for cmd in test_commands:
        category = store.detect_category(cmd)
        print(f"Command: '{cmd}'")
        print(f"Detected category: '{category}'\n")
    
    # Test 2: Variable extraction
    print("--- Test 2: Variable Extraction ---")
    variable_test_commands = [
        ("Open my default browser to www.example.com", "open_webpage"),
        ("Create a file named test.txt", "file_creation"),
        ("Search for quantum computing tutorials", "search_query"),
    ]
    
    for cmd, category in variable_test_commands:
        variables = store.extract_potential_variables(cmd, category)
        print(f"Command: '{cmd}'")
        print(f"Variables extracted: {variables}\n")
    
    # Test 3: Pattern creation and matching
    print("--- Test 3: Pattern Storage and Matching ---")
    
    # Example intents for different commands
    web_intent = {
        "action": "run_code",
        "code": "import webbrowser; webbrowser.open('www.example.com')"
    }
    
    file_intent = {
        "action": "create_file",
        "filename": "test.txt"
    }
    
    search_intent = {
        "action": "run_code",
        "code": "import webbrowser; webbrowser.open('https://www.google.com/search?q=quantum+computing+tutorials')"
    }
    
    # Store patterns
    test_storage = [
        ("Open my default browser to www.example.com", web_intent),
        ("Create a file named test.txt", file_intent),
        ("Search for quantum computing tutorials", search_intent)
    ]
    
    for cmd, intent in test_storage:
        print(f"Storing command: '{cmd}'")
        store.add_pattern(cmd, intent, store_command=True)
        print()
    
    # Test matching with variations
    test_matches = [
        "Open my default browser to www.github.com",
        "Create a file named report.docx",
        "Search for machine learning basics",
        # Similar but not exact
        "Open my web browser to www.github.com",
        # Non-matching command
        "Reboot the system in 5 minutes"
    ]
    
    print("\n--- Testing Pattern Matching with Variations ---")
    for test_cmd in test_matches:
        print(f"Testing command: '{test_cmd}'")
        match_result = store.match_command(test_cmd)
        
        if match_result:
            intent, variables = match_result
            print(f"✅ MATCHED: {test_cmd}")
            if variables:
                print(f"  Variables: {variables}")
            print(f"  Intent: {intent}")
        else:
            print(f"❌ NOT MATCHED: {test_cmd}")
        print()
    
    print("Test complete!")

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
        test_enhanced_pattern_matching()
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