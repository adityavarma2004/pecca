import cohere
from rich import print
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
CohereAPIkey = env_vars.get("COHERE_API_KEY")
co = cohere.Client(api_key=CohereAPIkey)

funcs = ["exit", "general", "realtime", "open", "close", "play", "generate image", 
         "system", "content", "google search", "youtube search", "reminder"]

preamble = """
You are a Decision-Making Model that classifies user queries into specific categories.
Do not answer the query - only identify its type from these options:

1. 'general (query)': For questions that don't need real-time data 
   Examples: historical facts, advice, explanations, general knowledge

2. 'realtime (query)': For questions needing current information
   Examples: current events, latest news, real-time information

3. 'open (app/website)': For requests to open applications or websites

4. 'close (app/website)': For requests to close applications or websites

5. 'play (song/media)': For requests to play audio or video content

6. 'generate image (description)': ONLY for requests to create images
   Examples: "draw a cat", "make an image of mountains"

7. 'system (action)': For system commands like volume control

8. 'content (topic)': For requests to generate or write text content
   Examples: "write an email", "create a python script", "write html code"

9. 'google search (query)': For web search requests

10. 'youtube search (query)': For YouTube search requests

11. 'reminder (datetime message)': For setting reminders

12. 'exit': If the user wants to end the conversation

IMPORTANT: Requests to write or create code (HTML, Python, JavaScript, etc.) should be classified as 'content' NOT as 'generate image'.

For multiple actions, separate with commas (e.g., 'open browser, play music').
Default to 'general (query)' if unsure.
"""

def classify_query(user_query):
    try:
        response = co.chat(
            model='command',
            message=user_query,
            temperature=0.7,
            preamble=preamble,
            prompt_truncation='AUTO'
        )
        
        response_text = response.text.replace("\n", "")
        tasks = [task.strip() for task in response_text.split(",")]
        
        valid_tasks = []
        for task in tasks:
            for func in funcs:
                if task.startswith(func):
                    valid_tasks.append(task)
                    break
        
        if valid_tasks:
            return valid_tasks
        else:
            return [f"general ({user_query})"]
            
    except Exception as e:
        print(f"API Error: {str(e)}")
        return [f"general ({user_query})"]

if __name__ == "__main__":
    print("Query Classifier (type 'exit' to quit)")
    while True:
        user_input = input(">>> ")
        if user_input.lower() == 'exit':
            print("Exiting program.")
            break
        result = classify_query(user_input)
        print(result)
