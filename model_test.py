import whisper
voice_2_text_model = whisper.load_model("small.en")
result = voice_2_text_model.transcribe(audio="temp_audio.webm", language='en')
print(result)