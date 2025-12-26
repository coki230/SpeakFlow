import whisper
import numpy as np
from pydub import AudioSegment
from io import BytesIO
import traceback

model = whisper.load_model("small.en")
def audio_to_text(file_path):
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

        result = model.transcribe(audio=samples, language='en')
        return result
    except Exception as e:
        print(traceback.format_exc())
        print(f"语音识别错误: {str(e)}")
        return None


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
