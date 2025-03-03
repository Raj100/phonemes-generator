import os
import nltk
import speech_recognition as sr
from flask import Flask, request, jsonify
from nltk.corpus import cmudict

# Download CMU Pronouncing Dictionary
nltk.download("cmudict")
cmu_dict = cmudict.dict()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return jsonify({"message": "Flask API for phoneme generation is running!"})

@app.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Convert speech to text
    recognizer = sr.Recognizer()
    with sr.AudioFile(filepath) as source:
        audio = recognizer.record(source)
    
    try:
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Error with speech recognition service"}), 500

    # Get phonemes
    words = text.lower().split()
    phonemes = {word: cmu_dict.get(word, ["Not found"]) for word in words}

    return jsonify({"text": text, "phonemes": phonemes})

# Vercel requires the app to be called as 'app'
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run()
