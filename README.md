# AI OS Assistant

A Python-based assistant that uses local LLMs to understand and execute system commands.

## Requirements

Before you begin, ensure you have the following installed:

### System Requirements
- Operating System: Windows 10/11, macOS, or Linux
- RAM: Minimum 16GB (32GB recommended for larger LLM models)
- Storage: At least 10GB free space for LLM models
- Internet connection (for initial setup and downloads)

### Required Software
- Python 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- Ollama ([Download Ollama](https://ollama.ai/download))
- Git (optional, for cloning the repository)

## Installation

1. **Install Python**
   - Download Python from [python.org](https://www.python.org/downloads/)
   - During installation, ensure you check "Add Python to PATH"
   - Verify installation by opening a terminal/command prompt and running:
     ```
     python --version
     ```

2. **Install Ollama**
   - Download Ollama from [ollama.ai/download](https://ollama.ai/download)
   - Follow the installation instructions for your operating system
   - Verify installation by opening a terminal/command prompt and running:
     ```
     ollama --version
     ```

3. **Get the AI OS Assistant**
   - Clone the repository (if you have Git):
     ```
     git clone [repository-url]
     ```
   - Or download and extract the ZIP file from the repository

4. **Install Python Dependencies**
   - Open a terminal/command prompt in the project directory
   - Run:
     ```
     pip install -r ai_os_assistant/requirements.txt
     ```

5. **Setup Ollama and LLM**
   - Enable Ollama logging (Windows only):
     ```
     $env:OLLAMA_DEBUG="1"
     ```
   - Pull and run your chosen LLM model:
     ```
     ollama pull deepseek-r1:32b  # or mistral
     ollama run deepseek-r1:32b   # or mistral
     ```

6. **Run the Assistant**
   - Execute the provided batch file:
     ```
     run_ai_assistant.bat
     ```

## Features

- Natural language processing for system commands
- File management operations (create, rename, sort)
- Command pattern storage to reduce LLM wait times
- Automatic command categorization and variable extraction
- Extensible action system

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

## Troubleshooting

Common issues and solutions:

1. **Python not found**
   - Ensure Python is added to PATH during installation
   - Try restarting your terminal/command prompt

2. **Ollama connection issues**
   - Verify Ollama is running (`ollama serve`)
   - Check if the correct model is installed (`ollama list`)

3. **LLM model errors**
   - Ensure you have sufficient RAM for your chosen model
   - Try using a smaller model like 'mistral' if you experience issues

For more help, please check the [issues section](repository-issues-url) of our repository.