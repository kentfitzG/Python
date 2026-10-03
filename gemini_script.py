import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    raise SystemExit("Set GEMINI_API_KEY to your Google AI Studio API key before running this script.")
if "\n" in api_key or "\r" in api_key:
    raise SystemExit("GEMINI_API_KEY contains a newline; set it to the API key value only.")

client = genai.Client(api_key=api_key)

while True:
    try:
        question = input("Ask Gemini (type 'exit' to quit): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        break

    if question.lower() in {"exit", "quit"}:
        print("Goodbye!")
        break
    if not question:
        continue

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=question,
    )
    print(response.text)