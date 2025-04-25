import speech_recognition as sr
from dotenv import dotenv_values
import os
import time

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default to en-US if not specified

# Create temp directory if it doesn't exist
current_dir = os.getcwd()
TemDirPath = rf"{current_dir}/Forontend/Files"
os.makedirs(TemDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    """Write the assistant status to a file"""
    with open(rf"{TemDirPath}/AssistantStatus.txt", "w") as file:
        file.write(Status)

def SpeechRecognition():
    """Perform speech recognition using speech_recognition library"""
    recognizer = sr.Recognizer()
    
    try:
        SetAssistantStatus("Listening...")
        print("Listening... (speak now)")
        
        with sr.Microphone() as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen for speech with timeout
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
        SetAssistantStatus("Processing...")
        print("Processing speech...")
        
        try:
            # Recognize speech using Google Speech Recognition
            recognized_text = recognizer.recognize_google(audio, language=InputLanguage)
            print(f"Recognized: {recognized_text}")
            return recognized_text
            
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            SetAssistantStatus("Not understood")
            return None
            
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            SetAssistantStatus("Service Error")
            return None
            
    except Exception as e:
        print(f"Error in SpeechRecognition: {e}")
        SetAssistantStatus("Error")
        return None

def main():
    """Main function to run the speech recognition system"""
    try:
        print("Starting Speech Recognition...")
        SetAssistantStatus("Ready")
        
        recognized_text = SpeechRecognition()
        
        if recognized_text:
            print(f"Speech recognized: {recognized_text}")
            SetAssistantStatus("Idle")
            return recognized_text
        else:
            print("No speech recognized")
            SetAssistantStatus("Idle")
            return None
            
    except Exception as e:
        print(f"Error in main: {e}")
        SetAssistantStatus("Error")
        return None

if __name__ == "__main__":
    main()