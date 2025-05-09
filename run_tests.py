import subprocess
import os
import time

def run_tests():
    # This script ('run_tests.py') is expected to be in the project root directory.
    # The AI assistant's code (main.py, etc.) is in a subdirectory (e.g., 'ai_os_assistant').
    
    assistant_code_subdir = "ai_os_assistant"  # Name of the subdirectory containing main.py
    main_script_in_subdir = "main.py"          # Name of the main Python script
    test_cases_in_subdir = "test_cases.txt"    # Name of the test cases file

    # Determine the absolute path to the subdirectory where main.py will run
    # This becomes the Current Working Directory (CWD) for the subprocess.
    assistant_run_cwd = os.path.abspath(assistant_code_subdir)

    # Determine the absolute path to the test_cases.txt file
    full_test_cases_path = os.path.join(assistant_run_cwd, test_cases_in_subdir)
    
    # The command to execute: ['python', 'main.py']
    # 'main.py' is relative to assistant_run_cwd.
    command_to_run = ["python", main_script_in_subdir]

    print(f"Starting AI OS Assistant test run...")
    print(f"Assistant CWD: {assistant_run_cwd}")
    print(f"Test cases file: {full_test_cases_path}")
    print(f"Executing: {' '.join(command_to_run)}")

    process = None
    try:
        process = subprocess.Popen(
            command_to_run,
            cwd=assistant_run_cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,        # Work with text streams (encodes/decodes automatically)
            bufsize=1,        # Line-buffered for stdout and stderr
            universal_newlines=True # Ensures consistent newline handling (though text=True often implies this)
        )
    except FileNotFoundError:
        print(f"Error: Could not start the assistant. Ensure 'python' is in your PATH and '{main_script_in_subdir}' exists in '{assistant_run_cwd}'.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while starting the assistant: {e}")
        return

    def read_until_prompt(proc, prompt_sequence="> "): # Changed prompt_marker to prompt_sequence
        # Reads and prints characters from proc.stdout until prompt_sequence is detected.
        output_chars = []    # To store all characters read for returning
        char_buffer = []     # To match against prompt_sequence

        while proc.stdout: # Check if stdout is available and not closed
            try:
                char = proc.stdout.read(1) # Read one character
            except Exception as e:
                print(f"\nError reading character from stdout: {e}", flush=True)
                break # Exit loop on read error

            if not char:  # Indicates EOF or that the process might have closed stdout
                print("\nDiagnostic: stdout returned EOF.", flush=True)
                # stderr will be handled by process.communicate() later if process terminates.
                # Avoid blocking here on stderr.read().
                break
            
            print(char, end='', flush=True) # Print assistant's output character by character
            output_chars.append(char)
            char_buffer.append(char)
            
            # Keep char_buffer the same size as prompt_sequence for matching
            if len(char_buffer) > len(prompt_sequence):
                char_buffer.pop(0)
            
            # Check if the current buffer matches the prompt_sequence
            if "".join(char_buffer) == prompt_sequence:
                break
        
        return "".join(output_chars)

    # Read and display initial output from the assistant (welcome messages, first prompt)
    print("\n--- Assistant Output (Initial Startup) ---", flush=True)
    read_until_prompt(process)
    print("--- End Assistant Output (Initial Startup) ---\n", flush=True)

    # Read test commands from the file
    test_commands = [] # Initialize to ensure it's defined
    try:
        with open(full_test_cases_path, 'r') as f:
            test_commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"Diagnostic: Found {len(test_commands)} test commands in '{full_test_cases_path}'.", flush=True)
        if not test_commands:
            print(f"Diagnostic: No executable test commands loaded. Check file content and ensure lines are not all comments or empty.", flush=True)
    except FileNotFoundError:
        print(f"Error: Test cases file not found at {full_test_cases_path}", flush=True)
        if process.stdin and not process.stdin.closed:
            try: process.stdin.write("exit\n"); process.stdin.flush()
            except BrokenPipeError: pass # Process might have already exited
        if process.poll() is None: process.terminate()
        process.wait()
        return
    except Exception as e:
        print(f"Error reading test cases file {full_test_cases_path}: {e}", flush=True)
        if process.stdin and not process.stdin.closed:
            try: process.stdin.write("exit\n"); process.stdin.flush()
            except BrokenPipeError: pass
        if process.poll() is None: process.terminate()
        process.wait()
        return

    # Diagnostic: Check process status before starting command loop
    initial_poll_status = process.poll()
    print(f"Diagnostic: AI Assistant process status before command loop: {'Terminated with code ' + str(initial_poll_status) if initial_poll_status is not None else 'Running'}", flush=True)

    if initial_poll_status is not None:
        print("Error: AI Assistant process terminated before test commands could be run.", flush=True)
    elif not test_commands:
        print("Info: No test commands to execute.", flush=True)
    else:
        # Execute each test command
        for cmd_to_test in test_commands:
            if process.poll() is not None: # Check if the assistant process terminated prematurely
                print(f"Error: Assistant process terminated unexpectedly during test execution. Last exit code: {process.returncode}", flush=True)
                break # Correctly indented to be conditional

            # This print statement and subsequent logic are now correctly part of the loop's iterated body
            print(f"\n>>> EXECUTING COMMAND: {cmd_to_test}", flush=True)
        
            if process.stdin and not process.stdin.closed:
                try:
                    process.stdin.write(cmd_to_test + "\n")
                    process.stdin.flush()
                except BrokenPipeError:
                    print(f"Error: Broken pipe when trying to send command: {cmd_to_test}. Assistant may have crashed.", flush=True)
                    break # Stop processing further commands
                except Exception as e:
                    print(f"Error writing to assistant's stdin: {e}", flush=True)
                    break
            else:
                print("Error: Cannot write to assistant's stdin (it's closed or None).", flush=True)
                break
        
            print(f"--- Assistant Output for '{cmd_to_test}' ---", flush=True)
        read_until_prompt(process)
        print(f"--- End Assistant Output for '{cmd_to_test}' ---\n", flush=True)
        # time.sleep(0.1) # Optional small delay if needed for stability

    # After all commands, send "exit" to the assistant
    if process.poll() is None: # If assistant is still running
        print("\n>>> SENDING 'exit' COMMAND TO ASSISTANT", flush=True)
        if process.stdin and not process.stdin.closed:
            try:
                process.stdin.write("exit\n")
                process.stdin.flush()
                process.stdin.close() # Close stdin after sending the last command
            except BrokenPipeError:
                print("Error: Broken pipe when trying to send 'exit' command. Assistant might have already exited.", flush=True)
            except Exception as e:
                print(f"Error sending 'exit' command: {e}", flush=True)
        else:
            print("Warning: Assistant's stdin is closed or None; cannot send 'exit' command.", flush=True)

    # Wait for the process to terminate and capture any final output
    print("\n--- Assistant Output (Final Shutdown) ---", flush=True)
    try:
        # communicate() waits for process to terminate.
        # It also reads all remaining data from stdout and stderr.
        stdout_data, stderr_data = process.communicate(timeout=10) # Wait up to 10s
        if stdout_data:
            print(stdout_data, end='', flush=True)
        if stderr_data:
            print(f"STDERR (Final): {stderr_data.strip()}", flush=True)
    except subprocess.TimeoutExpired:
        print("Timeout waiting for assistant to shut down gracefully. Terminating...", flush=True)
        process.kill() # Force kill
        # Attempt to get any last output after killing
        stdout_data, stderr_data = process.communicate()
        if stdout_data:
            print(stdout_data, end='', flush=True)
        if stderr_data:
            print(f"STDERR (Post-Kill): {stderr_data.strip()}", flush=True)
    except Exception as e:
        print(f"Error during final communication with assistant: {e}", flush=True)
            
    print("\n--- Test run finished ---", flush=True)
    if process.returncode is not None:
        print(f"Assistant process exited with code: {process.returncode}", flush=True)
    else:
        # This can happen if the process was killed and returncode wasn't set,
        # or if poll() was never updated after termination.
        final_poll = process.poll()
        if final_poll is not None:
            print(f"Assistant process exited with code: {final_poll}", flush=True)
        else:
            print("Assistant process exit code not definitively captured (may have been killed).", flush=True)

if __name__ == "__main__":
    run_tests()