# uv add edge-tts
# import edge_tts
# import asyncio
#
# async def amain():
#     communicate = edge_tts.Communicate("Hello! This is a free voice, I can help you to learn English", "en-US-GuyNeural")
#     await communicate.save("test.mp3")
#
# asyncio.run(amain())

import os
# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# 1. 加载模型和分词器 (以 Phi-3.5 为例，因为它对硬件很友好)
model_id = "microsoft/Phi-3.5-mini-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype="auto",
    # 将此项设为 False，强制使用 transformers 库内置的 Phi3 实现
    # 而不是从 .cache 文件夹加载那个报错的 modeling_phi3.py
    trust_remote_code=False
)

# 2. 构建对话管道
chat_pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)


def get_llm_response(user_text):
    messages = [
        {"role": "system", "content": "You are a concise English assistant. your name is lili"},
        {"role": "user", "content": user_text},
    ]

    # 构建 Prompt 模板
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    outputs = chat_pipe(prompt, max_new_tokens=100, do_sample=True, temperature=0.7)

    # 提取生成的回复内容
    full_text = outputs[0]['generated_text']
    response = full_text.split("<|assistant|>")[-1].strip()
    return response

# 测试流程
user_input = "how are you?"
ai_reply = get_llm_response(user_input)
print(ai_reply) # 传给你的 TTS 模型 (如 Edge-TTS)