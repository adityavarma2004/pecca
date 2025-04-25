import speech_recognition as sr
import pyttsx3
from dotenv import dotenv_values

from RealtimeSearchEngine import RealtimeSearchEngine
from Chatbot import chat_bot
from Model import classify_query

class PECCA:
    def __init__(self):
        env_vars = dotenv_values(".env")
        self.username = env_vars.get("username", "User")
        self.assistant_name = env_vars.get("assistant", "PECCA")
        
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 175)
        
        self.recognizer = sr.Recognizer()
        
        print(f"{self.assistant_name} initialized!")
    
    def speak(self, text):
        print(f"{self.assistant_name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                print(f"{self.username}: {text}")
                return text
            except Exception as e:
                print(f"Error: {e}")
                return ""
    
    def text_input(self):
        return input(f"{self.username}: ")
    
    def process_command(self, query):
        classifications = classify_query(query)
        
        for classification in classifications:
            if classification.startswith("exit"):
                self.speak("Goodbye!")
                return False
                
            elif classification.startswith("general"):
                response = chat_bot(query)
                self.speak(response)
                
            elif classification.startswith("realtime") or classification.startswith("google search"):
                response = RealtimeSearchEngine(query)
                self.speak(response)
                
            else:
                self.speak(f"I understand you want to {classification}. This functionality is still being developed.")
                
        return True
    
    def run(self, use_voice=True):
        self.speak(f"Hello {self.username}, how can I help you?")
        
        running = True
        while running:
            if use_voice:
                query = self.listen()
                if not query:
                    continue
            else:
                query = self.text_input()
                
            if query.lower() in ["exit", "quit", "bye"]:
                self.speak("Goodbye!")
                break
                
            running = self.process_command(query)

if __name__ == "__main__":
    assistant = PECCA()
    
    use_voice = input("Use voice input? (y/n): ").lower() == 'y'
    
    assistant.run(use_voice)
