from flask import Flask, request, jsonify
import speech_recognition as sr
import nltk
from nltk.corpus import cmudict
from pydub import AudioSegment
import os

app = Flask(__name__)

# Load CMU Pronouncing Dictionary
nltk.download('cmudict')
pron_dict = cmudict.dict()

def convert_audio(file_path):
    """ Converts any audio format to WAV (required for SpeechRecognition) """
    wav_path = file_path.rsplit(".", 1)[0] + ".wav"
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(wav_path, format="wav")
    return wav_path

def convert_to_text(file_path):
    """ Convert audio to text using Google Web Speech API (better than CMU Sphinx) """
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

def text_to_phonemes(text):
    """ Convert recognized words to phonemes using CMU Pronouncing Dictionary """
    words = text.split()
    phonemes = [pron_dict[word][0] if word in pron_dict else ["?"] for word in words]
    return phonemes

@app.route("/")
def home():
    return "Hello! This is a Speech-to-Phoneme API using Flask."

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Convert to WAV (if needed)
    if not file.filename.lower().endswith(".wav"):
        file_path = convert_audio(file_path)

    # Convert Speech to Text
    text = convert_to_text(file_path)
    if text is None:
        return jsonify({"error": "Speech not recognized"}), 400

    # Convert Text to Phonemes
    phonemes = text_to_phonemes(text)

    return jsonify({"filename": file.filename, "text": text, "phonemes": phonemes})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
