from flask import Flask, request, jsonify
import speech_recognition as sr
import os
from io import BytesIO

app = Flask(__name__)

# CMU Pronouncing Dictionary Path
CMU_DICT_PATH = "./cmudict"

def load_cmu_dict():
    """Load CMU Pronouncing Dictionary into a dictionary"""
    cmu_dict = {}
    if not os.path.exists(CMU_DICT_PATH):
        print(f"Error: CMU Pronouncing Dictionary not found at {CMU_DICT_PATH}")
        return cmu_dict 

    with open(CMU_DICT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) > 1:
                word = parts[0].lower() 
                phonemes = parts[1:]
                cmu_dict[word] = phonemes
    return cmu_dict

# Load pronunciation dictionary
pron_dict = load_cmu_dict()

@app.route('/')
def home():
    return 'Hello, World! Flask API is running on Render.'

@app.route('/about')
def about():
    return 'This API converts speech to phonemes using CMU Pronouncing Dictionary.'

@app.route('/upload', methods=['POST'])
def upload():
    """Handles audio file uploads and converts speech to phonemes"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    # Convert audio to phonemes directly from memory
    phonemes = convert_to_phonemes(file)

    return jsonify({"filename": file.filename, "phonemes": phonemes})

def convert_to_phonemes(file):
    """Convert speech to phonemes using CMU dictionary"""
    recognizer = sr.Recognizer()

    with BytesIO(file.read()) as audio_file:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

    try:
        text = recognizer.recognize_sphinx(audio)  # Use PocketSphinx for offline recognition
        phonemes = text_to_phonemes(text)
        return phonemes
    except sr.UnknownValueError:
        return "Speech not recognized"
    except sr.RequestError:
        return "Error with speech recognition service"

def text_to_phonemes(text):
    """Convert recognized text into phonemes using CMU dictionary"""
    words = text.lower().split()
    phonemes = [pron_dict[word] if word in pron_dict else ["?"] for word in words]
    return phonemes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
