from groq import Groq
from json import load, dump
import json.decoder
import datetime
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Username = env_vars.get("username", "User")
Assistantname = env_vars.get("assistant", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey", "")

client = Groq(api_key=GroqAPIKey)

System = f"""
You are {Assistantname}, a highly intelligent and helpful AI assistant created to provide accurate, relevant, and concise responses to {Username}'s questions.

Core Identity:
- When asked "who are you", you'll respond clearly: "I am {Assistantname}, an AI assistant designed to help answer your questions and assist with various tasks."
- You have a friendly, respectful, and direct communication style.
- You provide factual information when known and acknowledge limitations when uncertain.

Response Guidelines:
- Be concise and directly address the question without unnecessary explanations.
- Provide complete answers but avoid excessive details unless specifically requested.
- Respond only in English, even if questions are asked in other languages.
- Do not mention your training data, limitations, or algorithms unless directly relevant.
- Never apologize for being an AI.
- Avoid disclaimers or notes at the end of your responses.

Important: Focus on giving relevant, accurate, and helpful answers tailored to the user's specific needs.
"""

os.makedirs("Data", exist_ok=True)

try:
    with open("Data/ChatLog.json", "r") as f:
        content = f.read()
        messages = load(f) if content.strip() else []
except (FileNotFoundError, json.decoder.JSONDecodeError):
    with open("Data/ChatLog.json", "w") as f:
        dump([], f)
    messages = []

def get_realtime_information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = f"""
Current date and time information:
Day: {day}
Date: {date}
Month: {month}
Year: {year}
Time: {hour} hours {minute} minutes {second} seconds.

Use this information only when the user explicitly asks about the current time or date.
"""
    return data

def answer_modifier(answer):
    lines = answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def chat_bot(query):
    try:
        global messages

        if not messages or messages[0].get("role") != "system":
            messages = [{"role": "system", "content": System}] + messages

        messages = [msg for msg in messages if not (msg.get("role") == "system" and "Current date and time information:" in msg.get("content", ""))]

        messages.append({"role": "user", "content": query})

        realtime_info = get_realtime_information()
        messages.append({"role": "system", "content": realtime_info})

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages
        )

        answer = response.choices[0].message.content

        messages = [msg for msg in messages if not (msg.get("role") == "system" and "Current date and time information:" in msg.get("content", ""))]
        messages.append({"role": "assistant", "content": answer})

        try:
            with open("Data/ChatLog.json", "w") as f:
                dump(messages, f, indent=4)
        except Exception as save_error:
            print(f"Error saving chat log: {save_error}")

        return answer_modifier(answer)

    except Exception as e:
        print(f"Error: {e}")

        if "model" in str(e).lower():
            try:
                messages = [{"role": "system", "content": System}]
                messages.append({"role": "user", "content": query})

                response = client.chat.completions.create(
                    model="gemma-7b-it",
                    messages=messages
                )

                answer = response.choices[0].message.content
                messages.append({"role": "assistant", "content": answer})

                with open("Data/ChatLog.json", "w") as f:
                    dump(messages, f, indent=4)

                return answer_modifier(answer)

            except Exception as alt_error:
                print(f"Alternative model error: {alt_error}")

        messages = [{"role": "system", "content": System}]

        try:
            with open("Data/ChatLog.json", "w") as f:
                dump(messages, f, indent=4)
        except Exception as save_error:
            print(f"Error resetting chat log: {save_error}")

        return f"An error occurred with the AI service. Please try again later or check your API key."

if __name__ == "__main__":
    print(f"Starting chat with {Assistantname}. Type 'exit', 'quit', or 'bye' to end the conversation.")
    while True:
        user_input = input(f"{Username}: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"{Assistantname}: Goodbye!")
            break
        response = chat_bot(user_input)
        print(f"{Assistantname}: {response}")
