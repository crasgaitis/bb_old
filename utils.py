import os
import speech_recognition as sr
from pydub import AudioSegment
from moviepy import *

def prepare_voice_file(path: str) -> str:
    if os.path.splitext(path)[1] == '.wav':
        return path
    elif os.path.splitext(path)[1] in ('.mp3', '.m4a', '.ogg', '.flac'):
        audio_file = AudioSegment.from_file(
            path, format=os.path.splitext(path)[1][1:])
        wav_file = os.path.splitext(path)[0] + '.wav'
        audio_file.export(wav_file, format='wav')
        return wav_file
    else:
        raise ValueError(
            f'Unsupported audio format: {format(os.path.splitext(path)[1])}')

def transcribe_audio(audio_data, language) -> str:
    r = sr.Recognizer()
    text = r.recognize_google(audio_data, language=language)
    return text

def write_transcription_to_file(text, output_file) -> None:
    with open(output_file, 'w') as f:
        f.write(text)
        
# output_wav based on input_path
def do_transcription(input_path, output_wav, language = 'english'):
    # language = 'ko-KR'
    # input_path = "korean_hamin/2024-03-27_13-04-49_UTC.mp4"

    video_clip = VideoFileClip(input_path)

    audio_clip = video_clip.audio
    audio_clip.write_audiofile(output_wav)

    audio_clip.close()
    video_clip.close()

    wav_file = prepare_voice_file(output_wav)
    with sr.AudioFile(wav_file) as source:
        audio_data = sr.Recognizer().record(source)
        text = transcribe_audio(audio_data, language)
        write_transcription_to_file(text, "test.txt")