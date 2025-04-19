# AI OS Assistant

A Python-based assistant that uses local LLMs to understand and execute system commands.

## Features

- Natural language processing for system commands
- File management operations (create, rename, sort)
- Command pattern storage to reduce LLM wait times
- Extensible action system

## Setup Instructions

1. Install Python (latest version recommended)
2. Install required dependencies: `pip install requests`
3. Install Ollama and a suitable LLM (deepseek-r1:32b or mistral recommended)
4. Set Ollama logging (Windows): `$env:OLLAMA_DEBUG="1"`
5. Run Ollama with the selected model: `ollama run deepseek-r1:32b` or `ollama run mistral`
6. Run the assistant: `run_ai_assistant.bat`

## Command Pattern Storage

The assistant includes a command pattern storage system that can recognize frequently used commands, reducing the need for LLM processing and cutting down wait times.

### How It Works

1. When you enter a command, the system first checks if it matches a stored pattern
2. If a match is found, it extracts variables (like filenames) and executes the command immediately
3. If no match is found, it processes your command through the LLM as usual
4. Certain command patterns are automatically identified and stored for future use

### Special Commands

- `store last`: Store the most recent command as a pattern for future use
- `clear patterns`: Clear all stored command patterns

### Example Usage

1. First time: "Create a file named report.txt"
   - The assistant will use the LLM to process this request
   - It may automatically identify this as a file creation pattern

2. Later: "Create a file named budget.xlsx"
   - The assistant will recognize this as matching the stored pattern
   - It will extract "budget.xlsx" as the filename
   - The command will execute immediately (skipping the LLM)

### Supported Pattern Types

The system can currently recognize and store patterns for:

- **File Creation**: Commands to create new files with different names
- **File Renaming**: Commands to rename files with specific patterns
- **File Sorting**: Commands to organize files into directories

More pattern types will be added in future updates.

## Extending the Assistant

To add new command actions, modify the following files:
- `dispatcher.py`: Add a new action handler
- `file_manager.py`: Implement the actual functionality
- `command_store.py`: Add pattern recognition for the new action