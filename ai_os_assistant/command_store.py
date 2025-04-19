import json
import os
import re
from typing import Dict, List, Optional, Tuple
from utils import log

# File to store command patterns
COMMAND_STORE_FILE = "command_patterns.json"

class CommandStore:
    def __init__(self):
        self.patterns = {}
        self.load_patterns()
    
    def load_patterns(self):
        """Load command patterns from file."""
        if os.path.exists(COMMAND_STORE_FILE):
            try:
                with open(COMMAND_STORE_FILE, 'r') as f:
                    self.patterns = json.load(f)
            except Exception as e:
                log(f"Error loading command patterns: {e}")
                self.patterns = {}
        else:
            self.patterns = {}
    
    def save_patterns(self):
        """Save command patterns to file."""
        try:
            with open(COMMAND_STORE_FILE, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            log(f"Error saving command patterns: {e}")
    
    def add_pattern(self, command: str, intent: dict, store_command: bool = False):
        """
        Add a new command pattern.
        
        Args:
            command: The user command.
            intent: The parsed intent.
            store_command: Whether to store this command (defaults to False).
        """
        if not store_command:
            return
            
        # Create a pattern category based on the action
        category = intent.get("action", "unknown")
        
        # Extract potential variable parts from the command
        if category == "create_file":
            # Example: "Create a file named test.txt"
            # Pattern: "Create a file named {filename}"
            filename = intent.get("filename", "")
            if filename and filename in command:
                pattern = command.replace(filename, "{filename}")
                if category not in self.patterns:
                    self.patterns[category] = []
                
                # Check if this pattern already exists
                pattern_exists = False
                for p in self.patterns[category]:
                    if p["pattern"] == pattern:
                        pattern_exists = True
                        break
                
                if not pattern_exists:
                    self.patterns[category].append({
                        "pattern": pattern,
                        "intent_template": intent,
                        "variables": ["filename"]
                    })
                    self.save_patterns()
                    log(f"Added pattern: {pattern}")
                    print(f"✅ Stored command pattern: {pattern}")
        
        elif category == "run_code" and "code" in intent:
            # For now, we'll only extract file creation patterns from code
            code = intent.get("code", "")
            # Match patterns like open('filename.txt', 'w')
            matches = re.findall(r"open\(['\"](.*?)['\"]\s*,\s*['\"]w['\"]", code)
            if matches:
                filename = matches[0]
                # Create a pattern based on the command and filename
                if filename in command:
                    pattern = command.replace(filename, "{filename}")
                    if "file_creation" not in self.patterns:
                        self.patterns["file_creation"] = []
                    
                    # Check if this pattern already exists
                    pattern_exists = False
                    for p in self.patterns["file_creation"]:
                        if p["pattern"] == pattern:
                            pattern_exists = True
                            break
                    
                    if not pattern_exists:
                        # Create a template that will generate file creation code
                        self.patterns["file_creation"].append({
                            "pattern": pattern,
                            "intent_template": {
                                "action": "run_code",
                                "code": "open('{filename}', 'w').close()"
                            },
                            "variables": ["filename"]
                        })
                        self.save_patterns()
                        log(f"Added file creation pattern: {pattern}")
                        print(f"✅ Stored file creation pattern: {pattern}")
    
    def match_command(self, command: str) -> Optional[Tuple[dict, Dict[str, str]]]:
        """
        Match a command against stored patterns.
        
        Args:
            command: The user command.
            
        Returns:
            Tuple of (intent, variables) if a match is found, None otherwise.
        """
        for category, patterns in self.patterns.items():
            for pattern_data in patterns:
                pattern_str = pattern_data["pattern"]
                variables = pattern_data["variables"]
                
                # Convert pattern to regex by escaping special chars and replacing {var} with capture groups
                regex_pattern = re.escape(pattern_str)
                for var in variables:
                    placeholder = re.escape(f"{{{var}}}")
                    regex_pattern = regex_pattern.replace(placeholder, f"(?P<{var}>.+?)")
                
                match = re.match(f"^{regex_pattern}$", command)
                if match:
                    # Extract variables
                    extracted_vars = match.groupdict()
                    
                    # Create intent using the template and extracted variables
                    intent = pattern_data["intent_template"].copy()
                    
                    # Replace variables in all intent fields
                    for key, value in intent.items():
                        if isinstance(value, str):
                            for var, var_value in extracted_vars.items():
                                if f"{{{var}}}" in value:
                                    intent[key] = value.replace(f"{{{var}}}", var_value)
                    
                    return intent, extracted_vars
        
        return None