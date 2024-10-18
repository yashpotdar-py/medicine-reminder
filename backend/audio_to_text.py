import speech_recognition as sr

def convert_audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)  # Read the entire audio file
        try:
            text = recognizer.recognize_google(audio_data)  # Convert audio to text
            return text
        except sr.UnknownValueError:
            return None  # Audio unintelligible
        except sr.RequestError:
            return None  # API request error


if __name__ == "__main__":
    print(convert_audio_to_text('/home/kali/Downloads/harvard.wav'))