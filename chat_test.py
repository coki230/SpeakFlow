from llama_cpp import Llama
import time


class Phi3Assistant:
    def __init__(self, model_path="D:/lm-model/models/akshaykdeo/Phi-3.5-mini-instruct-Q4_K_M-GGUF/Phi-3.5-mini-instruct-Q4_K_M.gguf"):
        print("正在加载模型到 AMD 核显...")
        # n_gpu_layers: -1 代表将所有模型层都交给 Radeon 8060S 处理
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # 上下文长度
            n_gpu_layers=-1,  # 全部放入 GPU
            n_threads=8,  # 配合你强大的 CPU 核心数
        )
        print("模型加载完成！")

    def chat(self, user_text):
        start_time = time.perf_counter()

        messages = [
            {"role": "system", "content": "You are a concise English assistant. your name is lili"},
            {"role": "user", "content": user_text},
        ]

        # 调用接口
        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            repeat_penalty=1.1
        )

        content = response['choices'][0]['message']['content'].strip()
        end_time = time.perf_counter()

        print(f"推理耗时: {end_time - start_time:.2f} 秒")
        return content

# 实例化
brain = Phi3Assistant()
print(brain.chat("Hello, what is your name?"))