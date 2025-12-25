from flask import Flask, render_template, request, jsonify
import json
import time
from datetime import datetime

app = Flask(__name__)


# 模拟语音处理函数 - 在实际应用中这里可以集成真实的语音识别和AI模型
def process_voice(text):
    """
    处理语音输入并返回响应
    这里使用简单的规则匹配，实际应用中可以集成AI模型
    """
    # 基本的对话逻辑
    text = text.lower()

    if "你好" in text or "您好" in text:
        return "你好！很高兴见到你！"
    elif "时间" in text:
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        return f"现在是{current_time}"
    elif "天气" in text:
        return "今天天气不错，适合外出散步。"
    elif "谢谢" in text:
        return "不客气！有什么可以帮助你的吗？"
    elif "再见" in text or "拜拜" in text:
        return "再见！祝你有美好的一天！"
    elif "名字" in text:
        return "我是语音对话助手，很高兴为您服务。"
    elif "帮助" in text:
        return "我可以帮你回答问题、提供信息、进行对话等。请告诉我你需要什么帮助。"
    else:
        # 随机回复
        responses = [
            "我理解你说的：'{}'。能告诉我更多吗？".format(text),
            "这个话题很有趣！关于 '{}'，我想说...".format(text),
            "谢谢你分享 '{}'。这让我想到...".format(text),
            "你说得对，'{}'确实很重要。".format(text),
            "明白了，关于 '{}' 我可以给你一些建议。".format(text)
        ]
        return responses[hash(text) % len(responses)]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process-voice', methods=['POST'])
def process_voice_endpoint():
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({'error': '没有收到语音内容'}), 400

        print(f"接收到语音内容: {text}")

        # 处理语音内容
        response_text = process_voice(text)

        # 模拟处理延迟
        time.sleep(0.5)

        return jsonify({
            'response': response_text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        print(f"处理错误: {str(e)}")
        return jsonify({'error': '处理失败'}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
