from werkzeug.datastructures import FileStorage
# import voice_util
import voice_util_new as voice_util
import asyncio

@profile
def for_test():
    v_util = voice_util.VoiceUtil()
    with open("temp_audio.webm", "rb") as fp:
        # 2. 包装成 FileStorage 对象
        audio_file = FileStorage(
            stream=fp,
            filename="temp_audio.webm",
            content_type="audio/webm",
        )

        input_text = v_util.audio_to_text(audio_file)
        print(input_text)
        out_text = v_util.get_llm_response(input_text)
        print(out_text)

        # 调用异步函数生成语音
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_base64 = loop.run_until_complete(v_util.get_bot_audio_base64(out_text))
        loop.close()
        print(audio_base64)

if __name__ == "__main__":
    for_test()