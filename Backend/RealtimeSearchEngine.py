from googlesearch import search
from groq import Groq
from json import loads, dumps
import datetime
from dotenv import dotenv_values
import requests
import re
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("username", "Aditya Varma")
Assistantname = env_vars.get("assistant", "PECCA")
GroqAPIKey = env_vars.get("GroqAPIKey", "")
client = Groq(api_key=GroqAPIKey)

System = f"""You are {Assistantname}, a very accurate AI chatbot that provides real-time information from the internet.
Your primary goal is to directly answer user questions based on the search data provided.
- ONLY use the information from the search results to formulate your answers
- Keep responses concise and factual
- Do not mention that you're using search results
- If the search results don't contain relevant information, admit you don't have enough information
- Never make up facts or information that isn't in the search results"""

try:
    with open('data/ChatLog.json', "r") as f:
        messages = loads(f.read())
except FileNotFoundError:
    os.makedirs('data', exist_ok=True)
    with open('data/ChatLog.json', "w") as f:
        messages = []
        f.write(dumps(messages))

def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = f"""Current date and time information:
Day: {day}
Date: {date}
Month: {month}
Year: {year}
Time: {hour} hours {minute} minutes {second} seconds."""
    return data

def GoogleSearch(query):
    try:
        search_results = list(search(query, num_results=3))
        if not search_results:
            return f"No search results found for '{query}'."
        return "\n\n".join([f"Source: {url}" for url in search_results])
    except Exception as e:
        return f"Error performing search: {str(e)}"

def RealtimeSearchEngine(prompt):
    global messages
    if not prompt.strip():
        return "I didn't receive a question. How can I help you today?"
    messages.append({"role": "user", "content": prompt})
    if any(term in prompt.lower() for term in ['time now', 'current time', 'date today', 'current date', 'what day is it']):
        time_info = Information()
        messages.append({"role": "assistant", "content": time_info})
        with open('data/ChatLog.json', "w") as f:
            f.write(dumps(messages))
        return time_info
    search_results = GoogleSearch(prompt)
    context = f"""USER QUERY: {prompt}

SEARCH RESULTS:
{search_results}

Your task is to provide a direct, accurate answer to the user's query based solely on the above search results. 
Do not mention that you're using search results. Just provide the answer as if you knew it directly.
If the search results don't contain relevant information to answer the query, admit that you don't have sufficient information.
Keep your response concise and focused."""
    groq_messages = [
        {"role": "system", "content": System},
        {"role": "user", "content": context}
    ]
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=groq_messages,
            temperature=0.2,
            max_tokens=800
        )
        assistant_response = response.choices[0].message.content
    except Exception as e:
        assistant_response = f"I apologize, but I encountered an error: {str(e)}. Please try again later."
    messages.append({"role": "assistant", "content": assistant_response})
    with open('data/ChatLog.json', "w") as f:
        f.write(dumps(messages))
    return assistant_response

def main():
    print(f"Welcome to {Assistantname}! Type 'exit' to quit.")
    while True:
        user_input = input(f"{Username}: ")
        if user_input.lower() == 'exit':
            break
        response = RealtimeSearchEngine(user_input)
        print(f"{Assistantname}: {response}")

if __name__ == "__main__":
    main()
