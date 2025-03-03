from flask import Flask, request, jsonify
import speech_recognition as sr
import os
from io import BytesIO

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CMU_DICT_PATH = os.path.join(BASE_DIR, "cmudict")

def load_cmu_dict():
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
    return 'Hello, World! Flask API is running.'

@app.route('/about')
def about():
    return 'This API converts speech to phonemes using CMU Pronouncing Dictionary.'

@app.route('/upload', methods=['POST'])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    phonemes = convert_to_phonemes(file)
    return jsonify({"filename": file.filename, "phonemes": phonemes})

def convert_to_phonemes(file):
    recognizer = sr.Recognizer()

    with BytesIO(file.read()) as audio_file:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

    try:
        text = recognizer.recognize_sphinx(audio)
        phonemes = text_to_phonemes(text)
        return phonemes
    except sr.UnknownValueError:
        return "Speech not recognized"
    except sr.RequestError:
        return "Error with speech recognition service"

def text_to_phonemes(text):
    words = text.lower().split()
    phonemes = [pron_dict[word] if word in pron_dict else ["?"] for word in words]
    return phonemes

if __name__ == "__main__":
    app.run(debug=True)
