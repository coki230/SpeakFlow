import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app, cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask-SocketIO 示例</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; }
        #messages { border: 1px solid #ccc; height: 300px; 
                    overflow-y: auto; padding: 10px; margin: 20px 0; }
        .message { padding: 8px; margin: 5px 0; border-radius: 4px; }
        .status { background: #e3f2fd; }
        .result { background: #c8e6c9; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Flask-SocketIO 示例</h1>

    <button onclick="startRecognition()">开始识别</button>
    <button onclick="sendMessage()">发送消息</button>

    <div id="messages"></div>

    <script>
        // 1. 连接到 Socket.IO 服务器
        const socket = io();

        // 2. 监听 'status' 事件（对应后端的 emit('status', ...)）
        socket.on('status', function(data) {
            addMessage('状态: ' + data.message, 'status');
        });

        // 3. 监听 'result' 事件
        socket.on('result', function(data) {
            addMessage('结果: ' + data.text, 'result');
        });

        // 4. 监听连接事件
        socket.on('connect', function() {
            addMessage('已连接到服务器', 'status');
        });

        // 触发语音识别
        function startRecognition() {
            socket.emit('start_recognition');
        }

        // 发送普通消息
        function sendMessage() {
            socket.emit('message', {text: 'Hello Server'});
        }

        // 显示消息
        function addMessage(text, className) {
            const div = document.getElementById('messages');
            const msg = document.createElement('div');
            msg.className = 'message ' + className;
            msg.textContent = text;
            div.appendChild(msg);
            div.scrollTop = div.scrollHeight;
        }
    </script>
</body>
</html>
"""


# 首页路由
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


# 监听客户端的 'start_recognition' 事件
@socketio.on('start_recognition')
def handle_recognition():
    # 发送状态更新
    emit('status', {'message': '正在识别语音...'})

    # 模拟识别过程
    import time
    time.sleep(2)

    # 发送识别结果
    emit('result', {'text': '识别完成：你好世界'})


# 监听客户端的 'message' 事件
@socketio.on('message')
def handle_message(data):
    print(f"收到消息: {data}")
    emit('status', {'message': f'服务器收到: {data["text"]}'})


# 客户端连接时触发
@socketio.on('connect')
def handle_connect():
    print('客户端已连接')
    emit('status', {'message': '欢迎连接!'})


# 客户端断开时触发
@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开')


if __name__ == '__main__':
    print("服务器启动: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)