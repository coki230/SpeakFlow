import whisper
import numpy as np
from pydub import AudioSegment
from io import BytesIO
import traceback
import edge_tts
import base64
import io
from llama_cpp import Llama
import re

# import os
# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


def webm_to_ndarray(webm_bytes):
    # pydub 可以识别 webm 格式
    audio = AudioSegment.from_file(BytesIO(webm_bytes), format="webm")
    print(f"原始采样率: {audio.frame_rate}, 通道: {audio.channels}, 时长: {len(audio) / 1000}s, sample_width: {audio.sample_width}")

    # 转换为 Whisper 需要的 16k 单声道浮点数组
    audio = audio.set_frame_rate(16000).set_channels(1)
    samples = np.array(audio.get_array_of_samples())
    if audio.sample_width == 2:  # 16-bit
        samples = samples.astype(np.float32) / 32768.0
    elif audio.sample_width == 4:  # 32-bit
        samples = samples.astype(np.float32) / 2147483648.0
    return samples

model_path="D:/lm-model/models/akshaykdeo/Phi-3.5-mini-instruct-Q4_K_M-GGUF/Phi-3.5-mini-instruct-Q4_K_M.gguf"
class VoiceUtil:
    def __init__(self):
        self.voice_2_text_model = whisper.load_model("small.en")


        self.brain_model = Llama(
            model_path=model_path,
            n_ctx=2048,  # 上下文长度
            n_gpu_layers=-1,  # 全部放入 GPU
            n_threads=8,  # 配合你强大的 CPU 核心数
        )
        self.min_tts_len = 10

    def audio_to_text(self, file):
        """
        将音频文件转换为文字
        支持多种音频格式
        """
        try:
            samples = webm_to_ndarray(file)

            # import scipy.io.wavfile as wavfile
            # wavfile.write("debug_after_process.wav", 16000, samples)

            result = self.voice_2_text_model.transcribe(audio=samples, language='en')
            return result['text']
        except Exception as e:
            print(traceback.format_exc())
            print(f"语音识别错误: {str(e)}")
            return None

    def send_response(self, text):
        # pass
        print("*" * 20, end="\n")
        print(text)
        print("*" * 20, end="\n")


    def get_llm_response(self, user_text):
        messages = [
            {"role": "system", "content": "You are a concise English assistant. your name is coki"},
            {"role": "user", "content": user_text},
        ]

        # 调用接口
        response_generator = self.brain_model.create_chat_completion(
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            repeat_penalty=1.1,
            stream=True,
        )
        full_content = ""
        # 这里的 current_buffer 存储尚未断句的文字
        current_buffer = ""
        # 这里的 pending_buffer 存储已经断句但还没达到最小长度的文字
        pending_buffer = ""

        print("AI 正在回答: ", end="")

        for chunk in response_generator:
            token = chunk['choices'][0]['delta'].get('content', '')
            if token:
                full_content += token
                current_buffer += token

                # 1. 检查当前累加的 token 是否构成了断句
                # 注意：这里使用正则匹配标点。如果 token 是 "Hello!"，则匹配成功
                if re.search(r'[.!?;]\s|\n|[.!?;]$', current_buffer):
                    # 把这一句完整的话存入待发送区
                    pending_buffer += " " + current_buffer.strip()
                    current_buffer = ""  # 清空当前句缓冲区

                    # 2. 检查待发送区的内容是否达到 TTS 要求的长度
                    if len(pending_buffer.strip()) >= self.min_tts_len:
                        # 只有够长了，才塞进队列
                        self.send_response(pending_buffer.strip())
                        pending_buffer = ""  # 塞完后清空

            # 3. 扫尾工作：处理所有残余文字
            # 即使最后一句很短，也要强行合并发送
        final_remains = (pending_buffer + " " + current_buffer).strip()
        if final_remains:
            self.send_response(final_remains)

        print("\n[回答结束]")
        return full_content

    async def get_bot_audio_base64(self, text, voice="en-US-GuyNeural"):
        # 1. 初始化 edge-tts
        communicate = edge_tts.Communicate(text, voice)

        # 2. 创建一个内存字节流容器
        audio_buffer = io.BytesIO()

        # 3. 将生成的音频块写入容器
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        # 4. 获取完整的字节数据
        bot_audio_bytes = audio_buffer.getvalue()

        # 5. 转化为 Base64 字符串
        bot_audio_base64 = base64.b64encode(bot_audio_bytes).decode('utf-8')

        return bot_audio_base64
