from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse
import voice_util
import base64
import uvicorn

app = FastAPI()

@app.get("/")
async def get():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    v_util = voice_util.VoiceUtil()
    await websocket.accept()
    try:
        while True:
            # 1. 接收前端传来的数据
            data = await websocket.receive_json()

            if "audio" in data:
                # 接收 Base64 音频
                audio_bytes = base64.b64decode(data["audio"])

                # 2. ASR 识别 (建议在单独的线程运行，避免阻塞事件循环)
                input_text = await v_util.audio_to_text(audio_bytes)
                if not input_text: continue

                await websocket.send_json({"type": "user_text", "text": input_text})

                # 3. LLM 流式生成
                # 假设 v_util.brain_model.create_chat_completion 支持 stream=True
                await v_util.get_llm_response(input_text, websocket)

    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == "__main__":
    # 使用 uvicorn 运行，完美支持多核并行
    uvicorn.run(app, host="0.0.0.0", port=5000)