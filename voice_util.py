import whisper
import numpy as np
from pydub import AudioSegment
from io import BytesIO
import traceback
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


class VoiceUtil:
    def __init__(self):
        self.voice_2_text_model = whisper.load_model("small.en")

        model_id = "microsoft/Phi-3.5-mini-instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        brain_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype="auto",
            # 将此项设为 False，强制使用 transformers 库内置的 Phi3 实现
            # 而不是从 .cache 文件夹加载那个报错的 modeling_phi3.py
            trust_remote_code=False
        )
        self.chat_pipe = pipeline("text-generation", model=brain_model, tokenizer=self.tokenizer)

    def audio_to_text(self, file_path):
        """
        将音频文件转换为文字
        支持多种音频格式
        """
        try:
            file_path.seek(0)
            file = file_path.read()

            samples = webm_to_ndarray(file)

            # import scipy.io.wavfile as wavfile
            # wavfile.write("debug_after_process.wav", 16000, samples)

            result = self.voice_2_text_model.transcribe(audio=samples, language='en')
            return result['text']
        except Exception as e:
            print(traceback.format_exc())
            print(f"语音识别错误: {str(e)}")
            return None

    def get_llm_response(self, user_text):
        messages = [
            {"role": "system", "content": "You are a concise English assistant. your name is lili"},
            {"role": "user", "content": user_text},
        ]

        # 构建 Prompt 模板
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        outputs = self.chat_pipe(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)

        # 提取生成的回复内容
        full_text = outputs[0]['generated_text']
        response = full_text.split("<|assistant|>")[-1].strip()
        return response
