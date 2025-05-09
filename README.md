# AI OS Assistant

A Python-based assistant that uses local LLMs to understand and execute system commands.

## Features

- Natural language processing for system commands
- File management operations (create, rename, sort)
- Command pattern storage to reduce LLM wait times
- Automatic command categorization and variable extraction
- Extensible action system

## Setup Instructions

1. Install Python (latest version recommended)
2. Install required dependencies: `pip install requests`
3. Install Ollama and a suitable LLM (deepseek-r1:32b or mistral recommended)
4. Set Ollama logging (Windows): `$env:OLLAMA_DEBUG="1"`
5. Run Ollama with the selected model: `ollama run deepseek-r1:32b` or `ollama run mistral`
6. Run the assistant: `run_ai_assistant.bat`

## Command Pattern Storage

The assistant includes an enhanced command pattern storage system that can recognize and store any type of command, automatically categorize it, extract variables, and reuse the pattern for similar future commands.

### How It Works

1. **Automatic Storage**: By default, every command you use is stored (unless you use the `no store` command)
2. **Command Categorization**: The system automatically categorizes commands (e.g., "open_webpage", "file_creation", "search_query")
3. **Variable Extraction**: Variables like URLs, filenames, search terms are automatically identified and extracted
4. **Pattern Matching**: When you enter a similar command, the system recognizes the pattern and extracts the new variables
5. **Similarity Matching**: Even if the commands aren't exactly the same, the system can recognize similar commands

### Special Commands

- `store last`: Store the most recent command as a pattern for future use
- `no store`: Execute the next command without storing it as a pattern
- `clear patterns`: Clear all stored command patterns

### Example Usage

**Web Browsing Example:**

1. First time: "Open my default browser to www.example.com"
   - The system stores this as a pattern in the "open_webpage" category
   - It extracts "www.example.com" as the {url} variable

2. Later: "Open my default browser to www.github.com"
   - The system recognizes this as matching the stored pattern
   - It extracts "www.github.com" as the new URL 
   - The command executes immediately (skipping the LLM)

**File Creation Example:**

1. First time: "Create a file named report.txt"
   - The system stores this as a pattern in the "file_creation" category
   - It extracts "report.txt" as the {filename} variable

2. Later: "Create a file named data.csv"
   - The system recognizes this as matching the stored pattern
   - It extracts "data.csv" as the new filename
   - The command executes immediately (skipping the LLM)

### Supported Pattern Categories

The system can automatically categorize and extract variables for many types of commands:

- **File Operations**: Creating, renaming, moving, or deleting files
- **Web Operations**: Opening websites, searching online
- **System Operations**: Launching programs, checking system status
- **Custom Commands**: Any other type of command will be stored with its full content

More categories can be easily added by updating the `CATEGORY_KEYWORDS` dictionary in `command_store.py`.

## Extending the Assistant

To add new command actions, modify the following files:
- `dispatcher.py`: Add a new action handler
- `file_manager.py`: Implement the actual functionality
- `command_store.py`: Add pattern recognition for the new action type