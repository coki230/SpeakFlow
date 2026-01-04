# test STT
# import whisper
# voice_2_text_model = whisper.load_model("small.en")
# result = voice_2_text_model.transcribe(audio="temp_audio.webm", language='en')
# print(result)


# test grammar model
from llama_cpp import Llama
brain_model = Llama(
    model_path="D:/lm-model/models/Triangle104/Qwen2.5-3B-Instruct-Q4_K_M-GGUF/qwen2.5-3b-instruct-q4_k_m.gguf",
    n_ctx=2048,  # 上下文长度
    n_gpu_layers=-1,  # 全部放入 GPUd
    n_threads=8,  # 配合你强大的 CPU 核心数
)
sentence = "I boughts ten apple yestarday."
prompt = f"""Correct the grammar of the following sentence and output ONLY the corrected version without any explanation or quotes:
Original: {sentence}
Corrected:"""

output = brain_model(
    prompt,
    max_tokens=64,
    temperature=1,
    stop=["\n", "Original:"]
)
corrected= output["choices"][0]["text"].strip()

# 测试
print(corrected)  # I bought ten apples yesterday.