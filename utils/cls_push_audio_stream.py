import threading
import io
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment, silence

class PushAudioStreamWriter(speechsdk.audio.PushAudioOutputStreamCallback):
    def __init__(self):
        super().__init__()
        self.audio_buffer = io.BytesIO()
        self.lock = threading.Lock()

    def write(self, audio_buffer: memoryview) -> int:
        with self.lock:
            self.audio_buffer.write(audio_buffer.tobytes())
        return len(audio_buffer)

    def close(self):
        pass  # No action needed on close for buffering approach

    def get_audio_segment(self):
        with self.lock:
            self.audio_buffer.seek(0)
            audio_segment = AudioSegment.from_raw(self.audio_buffer, sample_width=2, frame_rate=16000, channels=1)
            self.audio_buffer = io.BytesIO()  # Reset buffer for the next chunk
        return audio_segment


    def remove_silence(self, audio_segment, silence_thresh=-40, min_silence_len=500, keep_silence=150):
        non_silent_ranges = silence.detect_nonsilent(audio_segment, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
        non_silent_audio = [audio_segment[start:end] for start, end in non_silent_ranges]
        combined_audio = AudioSegment.empty()
        for segment in non_silent_audio:
            combined_audio += segment + AudioSegment.silent(duration=keep_silence)
        return combined_audio


stream_writer = PushAudioStreamWriter()
