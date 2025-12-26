from flask import Flask, request, jsonify, render_template
import voice_util
import asyncio


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

    # 调用异步函数生成语音
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    audio_base64 = loop.run_until_complete(v_util.get_bot_audio_base64(out_text))
    loop.close()

    return jsonify({
        "user_text": input_text,  # 用户的文字（显示在右侧）
        "bot_text": out_text,  # 机器的文字（显示在左侧）
        "audio_base64": audio_base64  # 回复的声音（自动播放）
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)