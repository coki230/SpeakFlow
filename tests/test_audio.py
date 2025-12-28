import io
import pytest
import sys
import os
from werkzeug.datastructures import FileStorage
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_file_success(client):
    # 1. 准备模拟的音频数据
    # 如果你已经有了 temp_audio.webm，可以用 open("temp_audio.webm", "rb")
    # 1. 以二进制读取模式打开保存的文件
    with open("temp_audio.webm", "rb") as fp:
        # 2. 包装成 FileStorage 对象
        audio_file = FileStorage(
            stream=fp,
            filename="temp_audio.webm",
            content_type="audio/webm",
        )

    # 2. 模拟 POST 请求
    response = client.post(
        '/send-audio',
        data={'audio': audio_file},
        content_type='multipart/form-data'
    )

    # 3. 断言结果
    assert response.status_code == 202
    json_data = response.get_json()
    assert "user_text" in json_data
    assert "bot_text" in json_data
    assert "audio_base64" in json_data
    print(f"\n测试通过！Bot 回复: {json_data['bot_text']}")