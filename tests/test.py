from gtts import gTTS
import os

# Text for speech
text = "Hello, this is a test audio file for speech recognition."

# Generate speech
tts = gTTS(text, lang="en")

# Save as MP3
mp3_filename = "test_audio.mp3"
tts.save(mp3_filename)
print(f"MP3 file saved as {mp3_filename}")

# Convert MP3 to WAV using ffmpeg (Requires ffmpeg installed)
wav_filename = "test_audio.wav"
os.system(f"ffmpeg -i {mp3_filename} {wav_filename}")
print(f"WAV file saved as {wav_filename}")
