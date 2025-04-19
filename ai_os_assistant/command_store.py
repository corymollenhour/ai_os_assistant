import json
import os
import re
from typing import Dict, List, Optional, Tuple, Set
from utils import log
from difflib import SequenceMatcher

# File to store command patterns
COMMAND_STORE_FILE = "command_patterns.json"

# Keywords for common command categories
CATEGORY_KEYWORDS = {
    "file_creation": ["create file", "make file", "new file"],
    "open_webpage": ["open browser", "browse to", "go to website", "open url", "navigate to"],
    "file_rename": ["rename file", "change name", "change filename"],
    "file_deletion": ["delete file", "remove file", "erase file"],
    "directory_creation": ["create folder", "create directory", "make folder", "new folder"],
    "directory_deletion": ["delete folder", "delete directory", "remove folder", "remove directory"],
    "system_operation": ["shutdown", "restart", "reboot", "sleep", "hibernate"],
    "program_launch": ["launch", "run program", "execute program", "start application", "open app"],
    "search_query": ["search for", "find", "look up", "google", "bing", "search"],
}

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
    
    def detect_category(self, command: str) -> str:
        """
        Automatically detect the category of a command based on keywords.
        
        Args:
            command: The user command.
            
        Returns:
            Category name as a string.
        """
        command_lower = command.lower()
        
        # Check for category keywords
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in command_lower:
                    return category
        
        # Look for specific patterns in the command
        if re.search(r'\.(txt|doc|pdf|csv|xlsx?|json|html?|css|js|py|java|cpp|c|go|rs|php)$', command_lower):
            if "open" in command_lower or "read" in command_lower:
                return "file_open"
            elif "create" in command_lower or "make" in command_lower or "new" in command_lower:
                return "file_creation"
            
        # URLs or web addresses
        if re.search(r'(www\..+\..+|https?://.+\..+|.+\.(com|org|net|io|edu|gov))', command_lower):
            return "open_webpage"
        
        # For commands we don't recognize, use a default category
        return "custom_command"
    
    def extract_potential_variables(self, command: str, category: str) -> List[Dict[str, str]]:
        """
        Extract potential variables from a command based on its category.
        
        Args:
            command: The user command.
            category: The detected category.
            
        Returns:
            List of dicts with potential variable names and values.
        """
        variables = []
        
        # Different extraction rules based on category
        if category == "file_creation":
            # Look for filenames in commands
            filenames = re.findall(r'\b([\w\-\.]+\.(txt|doc|docx|pdf|csv|xlsx?|json|html?|css|js|py|java|cpp|c|go|rs|php))\b', command)
            if filenames:
                variables.append({
                    "name": "filename",
                    "value": filenames[0][0]  # Get the full filename, not just the extension
                })
        
        elif category == "open_webpage":
            # Look for URLs or domain names
            urls = re.findall(r'\b(www\.[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}|https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}|[a-zA-Z0-9\-\.]+\.(com|org|net|io|edu|gov))\b', command)
            if urls:
                variables.append({
                    "name": "url",
                    "value": urls[0][0] if isinstance(urls[0], tuple) else urls[0]
                })
        
        elif category == "search_query":
            # Try to extract search terms
            search_terms = re.findall(r'(?:search for|find|look up|google|bing|search)(?:\s+for)?\s+"([^"]+)"', command)
            if not search_terms:
                # Try without quotes
                match = re.search(r'(?:search for|find|look up|google|bing|search)(?:\s+for)?\s+(.+?)(?:\s+in|\s+on|\s+with|$)', command)
                if match:
                    search_terms = [match.group(1)]
            
            if search_terms:
                variables.append({
                    "name": "query",
                    "value": search_terms[0]
                })
        
        # Add more extraction rules for different categories as needed
        
        # If we couldn't find specific variables, look for any quoted text, paths, or numbers
        if not variables:
            # Quoted text
            quotes = re.findall(r'"([^"]+)"', command)
            if quotes:
                variables.append({
                    "name": "quoted_text",
                    "value": quotes[0]
                })
            
            # Paths
            paths = re.findall(r'[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*', command)
            if paths:
                variables.append({
                    "name": "path",
                    "value": paths[0]
                })
            
            # Numbers
            numbers = re.findall(r'\b\d+\b', command)
            if numbers:
                variables.append({
                    "name": "number",
                    "value": numbers[0]
                })
            
            # For search queries with no special pattern
            if category == "search_query":
                # Try to extract everything after "search for" or similar phrases
                match = re.search(r'(?:search for|find|look up|google|search)\s+(.+?)(?:\s+in|\s+on|\s+with|$)', command.lower())
                if match:
                    variables.append({
                        "name": "query",
                        "value": match.group(1).strip()
                    })
        
        return variables
    
    def create_pattern_from_command(self, command: str, variables: List[Dict[str, str]]) -> str:
        """
        Create a pattern from a command by replacing variable parts with placeholders.
        
        Args:
            command: The user command.
            variables: List of variable dictionaries with name and value.
            
        Returns:
            Pattern string with placeholders.
        """
        pattern = command
        
        # Replace variable values with placeholders
        for var in variables:
            name = var["name"]
            value = var["value"]
            if value in pattern:
                pattern = pattern.replace(value, f"{{{name}}}")
        
        return pattern
    
    def add_pattern(self, command: str, intent: dict, store_command: bool = False):
        """
        Add a new command pattern.
        
        Args:
            command: The user command.
            intent: The parsed intent.
            store_command: Whether to store this command (defaults to False).
        """
        if not store_command:
            # Only auto-store certain pattern types
            action = intent.get("action", "unknown")
            if action == "create_file" or (action == "run_code" and "open(" in intent.get("code", "")):
                # These are helpful to auto-store
                pass
            else:
                # Don't auto-store other patterns
                return
        
        # Detect the command category
        category = self.detect_category(command)
        
        # Extract potential variables
        variables = self.extract_potential_variables(command, category)
        
        # If no variables were found but we're forcing storage, at least store the raw command
        if not variables and store_command:
            if category not in self.patterns:
                self.patterns[category] = []
            
            # Store the exact command with its original intent
            pattern_exists = False
            for p in self.patterns[category]:
                if p.get("raw_command") == command:
                    pattern_exists = True
                    break
            
            if not pattern_exists:
                self.patterns[category].append({
                    "raw_command": command,
                    "pattern": command,  # No variables, so pattern is the same as the command
                    "intent_template": intent,
                    "variables": []
                })
                self.save_patterns()
                log(f"Added raw command pattern: {command}")
                print(f"✅ Stored command: {command}")
            return
        
        # Create a pattern with placeholders for variables
        pattern = self.create_pattern_from_command(command, variables)
        
        # Don't save if we couldn't create a meaningful pattern
        if pattern == command and variables:
            if store_command:
                log(f"Could not create a meaningful pattern for: {command}")
                print(f"⚠️ Could not extract variables from command: {command}")
            return
        
        # Add the pattern to the appropriate category
        if category not in self.patterns:
            self.patterns[category] = []
        
        # Check if this pattern already exists
        pattern_exists = False
        for p in self.patterns[category]:
            if p.get("pattern") == pattern:
                pattern_exists = True
                break
        
        if not pattern_exists:
            # Get variable names and create the pattern data
            var_names = [var["name"] for var in variables]
            
            # Create a template for the intent
            intent_template = intent.copy()
            
            # Replace variable values in the intent template
            for key, value in intent_template.items():
                if isinstance(value, str):
                    for var in variables:
                        if var["value"] in value:
                            intent_template[key] = value.replace(var["value"], f"{{{var['name']}}}")
            
            # Save the pattern
            self.patterns[category].append({
                "pattern": pattern,
                "intent_template": intent_template,
                "variables": var_names,
                "example_command": command  # Store an example for reference
            })
            self.save_patterns()
            log(f"Added {category} pattern: {pattern}")
            print(f"✅ Stored {category} pattern: {pattern}")
    
    def similarity_score(self, s1: str, s2: str) -> float:
        """Calculate the similarity between two strings using sequence matching."""
        # Normalize the strings by lowercasing and removing common words
        common_words = {"a", "an", "the", "my", "your", "our", "their", "to", "for", "in", "on", "with", "by", "and", "or"}
        
        def normalize(text):
            words = text.lower().split()
            return " ".join([w for w in words if w not in common_words])
            
        return SequenceMatcher(None, normalize(s1), normalize(s2)).ratio()
    
    def find_best_raw_command_match(self, command: str, category: str) -> Optional[Tuple[dict, float]]:
        """Find the best matching raw command in a category based on similarity."""
        if category not in self.patterns:
            return None
        
        best_pattern = None
        best_score = 0
        
        for pattern_data in self.patterns[category]:
            if "raw_command" in pattern_data:
                raw_command = pattern_data["raw_command"]
                score = self.similarity_score(command, raw_command)
                
                # Consider it a match if the similarity is high enough
                # Lower the threshold to catch more similar commands
                if score > 0.7 and score > best_score:
                    best_score = score
                    best_pattern = pattern_data
        
        if best_pattern:
            return best_pattern, best_score
        
        return None
    
    def match_command(self, command: str) -> Optional[Tuple[dict, Dict[str, str]]]:
        """
        Match a command against stored patterns.
        
        Args:
            command: The user command.
            
        Returns:
            Tuple of (intent, variables) if a match is found, None otherwise.
        """
        # First, try to detect the command category
        primary_category = self.detect_category(command)
        
        # Also check file_creation when category is uncertain
        categories_to_check = [primary_category]
        if primary_category == "custom_command":
            # Add other common categories to check
            categories_to_check.extend(["file_creation", "open_webpage", "search_query"])
        
        # Try to match against patterns in each category to check
        for category in categories_to_check:
            if category in self.patterns:
                # First try exact pattern matching
                for pattern_data in self.patterns[category]:
                    if "variables" not in pattern_data:
                        continue
                        
                    pattern_str = pattern_data["pattern"]
                    variables = pattern_data["variables"]
                    
                    # Skip raw commands (no variables)
                    if not variables:
                        continue
                    
                    # Convert pattern to regex with more flexible matching
                    regex_pattern = re.escape(pattern_str)
                    for var in variables:
                        placeholder = re.escape(f"{{{var}}}")
                        regex_pattern = regex_pattern.replace(placeholder, f"(?P<{var}>.+?)")
                    
                    # Make matching more flexible
                    # Allow any whitespace between words
                    regex_pattern = regex_pattern.replace("\\ ", r"\s+")
                    
                    match = re.match(f"^{regex_pattern}$", command, re.IGNORECASE)
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
                
                # If no exact match, try similarity matching for raw commands
                raw_match = self.find_best_raw_command_match(command, category)
                if raw_match:
                    pattern_data, score = raw_match
                    log(f"Found similar command match with score {score}: {pattern_data['raw_command']}")
                    print(f"🔍 Using similar command match ({int(score*100)}% similar)")
                    return pattern_data["intent_template"], {}
        
        # Try other categories as a fallback (commands might be miscategorized)
        for other_category, patterns in self.patterns.items():
            if other_category == category:
                continue
                
            for pattern_data in patterns:
                if "variables" not in pattern_data:
                    continue
                    
                pattern_str = pattern_data["pattern"]
                variables = pattern_data["variables"]
                
                # Skip raw commands in other categories
                if not variables:
                    continue
                
                # Convert pattern to regex
                regex_pattern = re.escape(pattern_str)
                for var in variables:
                    placeholder = re.escape(f"{{{var}}}")
                    regex_pattern = regex_pattern.replace(placeholder, f"(?P<{var}>.+?)")
                
                match = re.match(f"^{regex_pattern}$", command)
                if match:
                    # Found a match in another category
                    extracted_vars = match.groupdict()
                    intent = pattern_data["intent_template"].copy()
                    
                    for key, value in intent.items():
                        if isinstance(value, str):
                            for var, var_value in extracted_vars.items():
                                if f"{{{var}}}" in value:
                                    intent[key] = value.replace(f"{{{var}}}", var_value)
                    
                    return intent, extracted_vars
        
        # No pattern match found
        return None