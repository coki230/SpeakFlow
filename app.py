from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import voice_util
import asyncio
import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", max_size=10 * 1024 * 1024)  # 10MB

v_util = voice_util.VoiceUtil()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': '连接成功'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('audio_data')
def handle_audio(data):
    """处理接收到的音频数据"""
    try:
        # 从 base64 解码音频数据
        audio_blob = base64.b64decode(data['audio'])

        # 发送处理状态
        emit('status', {'message': '正在识别语音...'})

        # 语音转文字
        input_text = v_util.audio_to_text(audio_blob)

        # 发送用户文本
        emit('user_text', {'text': input_text})

        # 发送处理状态
        emit('status', {'message': '正在思考回复...'})

        # 获取 LLM 响应
        out_text = v_util.get_llm_response(input_text, emit)

        # # 发送机器人文本
        # emit('bot_text', {'text': out_text})

        # # 发送处理状态
        # emit('status', {'message': '正在生成语音...'})

        print(f"input text: {input_text}, output text: {out_text}")


        # 发送完成状态
        emit('status', {'message': '已就绪'})

    except Exception as e:
        print(f"Error processing audio: {e}")
        emit('error', {'message': '处理语音时出错，请重试'})
        emit('status', {'message': '处理出错'})


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)