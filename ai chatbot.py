import subprocess
import json

SYSTEM_PROMPTS = [
    "You are a helpful assistant and will always provide clear, accurate information.",
    "You are a technical assistant. Explain concepts with precise terminology, include relevant details, and focus on correctness and implementation depth.",
    "You are a first-principles thinker. Break problems down to foundational truths, reason from basic concepts, and avoid relying on assumptions or memorized patterns.",
    "You are a critical assistant. Evaluate claims carefully, question assumptions, identify weaknesses, and distinguish facts from opinions or speculation.",
    "You are a step-by-step reasoning assistant. Solve problems systematically, show the logic clearly, and explain each stage before reaching a conclusion.",
    "You are a decisive assistant. Always provide a direct answer, even when the prompt is vague or uncertain. State your best answer clearly, include any assumptions, and keep the response useful and actionable."
]


def choose_system_prompt():
    print("Choose a system prompt:")
    for index, prompt in enumerate(SYSTEM_PROMPTS, start=1):
        print(f"  {index}. {prompt}")

    while True:
        choice = input(f"Select a prompt number (1-{len(SYSTEM_PROMPTS)}): ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(SYSTEM_PROMPTS):
                return SYSTEM_PROMPTS[index]
        print(f"Invalid selection. Please choose a number from 1 to {len(SYSTEM_PROMPTS)}.")


def ask_llm(prompt):
    result = subprocess.run(
        ["ollama", "run", "llama3.1"],
        input=json.dumps({"prompt": prompt}),
        text=True,
        capture_output=True
    )
    return result.stdout.strip()


def chat():
    print("Simple Chatbot (Vulnerable)")
    system_prompt = choose_system_prompt()
    while True:
        user = input("User: ")
        full_prompt = f"{system_prompt}\nUser: {user}\nAssistant:"
        response = ask_llm(full_prompt)
        print("Bot:", response)


if __name__ == "__main__":
    chat()
