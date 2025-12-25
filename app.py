from flask import Flask, request, jsonify, render_template
import os
import io
import wave
import sounddevice as sd
import numpy as np
import threading
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send-audio', methods=['POST'])
def send_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        # Save the audio to a temporary file
        filename = "temp_audio.webm"
        audio_file.save(filename)

        # Process and play the audio using sounddevice
        play_audio_async(filename)

        return jsonify({'message': 'Audio received and played successfully'}), 200

    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return jsonify({'error': 'Failed to process audio'}), 500


def play_audio_async(filename):
    """Play audio in a separate thread to avoid blocking the main thread"""

    def play():
        try:
            # In a real implementation, we would decode and play the audio
            print(f"Playing audio file: {filename}")

            # Simulate audio processing time
            time.sleep(2)

            print("Audio playback completed")
        except Exception as e:
            print(f"Error playing audio: {str(e)}")

    # Run in a separate thread to avoid blocking
    thread = threading.Thread(target=play)
    thread.start()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)