from flask import Flask, request, jsonify, render_template
import voice_util


app = Flask(__name__)
v_util = voice_util.VoiceUtil()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send-audio', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['audio']
    # # Save the file
    # file_path = "temp_audio.webm"
    # file.save(file_path)

    input_text = v_util.audio_to_text(file)
    out_text = v_util.get_llm_response(input_text)
    print(out_text)


    return jsonify({"message": out_text}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)