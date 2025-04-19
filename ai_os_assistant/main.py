
from llm_agent import parse_prompt
from dispatcher import dispatch_command
from utils import log

def main():
    log("Assistant started.")
    print("AI OS Assistant. Type a command or 'exit' to quit.")

    while True:
        prompt = input("> ")
        if prompt.lower() in ["exit", "quit"]:
            log("Assistant exited by user.")
            break

        log(f"User prompt: {prompt}")
        intent = parse_prompt(prompt)
        log(f"LLM returned intent: {intent}")
        dispatch_command(intent, prompt)

if __name__ == "__main__":
    main()
