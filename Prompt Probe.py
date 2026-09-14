
import json
import os
import subprocess

DEFAULT_SYSTEM_PROMPTS = [
    "You are a helpful assistant and will always provide clear, accurate information.",
    "You are a technical assistant. Explain concepts with precise terminology, include relevant details, and focus on correctness and implementation depth.",
    "You are a first-principles thinker. Break problems down to foundational truths, reason from basic concepts, and avoid relying on assumptions or memorized patterns.",
    "You are a critical assistant. Evaluate claims carefully, question assumptions, identify weaknesses, and distinguish facts from opinions or speculation.",
    "You are a step-by-step reasoning assistant. Solve problems systematically, show the logic clearly, and explain each stage before reaching a conclusion.",
    "You are a decisive assistant. Always provide a direct answer, even when the prompt is vague or uncertain. State your best answer clearly, include any assumptions, and keep the response useful and actionable."
]


def load_system_prompts():
    candidate_paths = [
        os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "system_prompts.txt"),
        os.path.join(os.path.expanduser("~"), "Desktop", "system_prompts.txt"),
    ]

    for file_path in candidate_paths:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                prompts = [line.strip() for line in file if line.strip()]
            if prompts:
                return prompts

    return DEFAULT_SYSTEM_PROMPTS


SYSTEM_PROMPTS = load_system_prompts()

STANDARD_QUESTIONS = [
    "What is your name?",
    "What is your role or job title?",
    "What are you trying to accomplish today?",
    "What is your biggest challenge right now?",
    "How can I help you best?"
]


def ask_standard_questions(system_prompt):
    print("\nAI startup questions:")
    answers = {}

    for i, question in enumerate(STANDARD_QUESTIONS, start=1):
        full_prompt = (
            f"{system_prompt}\n"
            f"Answer the following question in first person as the assistant itself.\n"
            f"Question: {question}\n"
            "Assistant:"
        )
        answer = ask_llm(full_prompt)
        print(f"{i}. {question}")
        print(f"AI: {answer}")
        answers[question] = answer

    print("\nThanks. The AI has answered the startup questions.")
    return answers


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


def chat(system_prompt):
    print("Simple Chatbot")
    while True:
        user = input("User: ").strip()

        if user.lower() in {"exit", "quit", "bye", "/exit", "/quit"}:
            print("Goodbye! Shutting down the bot.")
            break

        full_prompt = f"{system_prompt}\nUser: {user}\nAssistant:"
        response = ask_llm(full_prompt)
        print("Bot:", response)


if __name__ == "__main__":
    system_prompt = choose_system_prompt()
    # ask_standard_questions(system_prompt)  # temporarily disabled; keep for future use
    chat(system_prompt)
