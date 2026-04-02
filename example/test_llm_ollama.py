from picarx.llm import Ollama

INSTRUCTIONS = "You are a helpful assistant. Reply in natural Japanese."
WELCOME = "こんにちは。日本語でお手伝いします。"

# If Ollama runs on the same Raspberry Pi, use "localhost".
# If it runs on another computer in your LAN, replace with that computer's IP address.
llm = Ollama(
    ip="localhost",
    model="llama3.2:3b"   # match the exact model name shown by `ollama list`
)

# Basic configuration
llm.set_max_messages(20)
llm.set_instructions(INSTRUCTIONS)
llm.set_welcome(WELCOME)

print(WELCOME)

while True:
    text = input(">>> ")
    if text.strip().lower() in {"exit", "quit"}:
        break

    # Response with streaming output
    response = llm.prompt(text, stream=True)
    for token in response:
        if token:
            print(token, end="", flush=True)
    print("")
