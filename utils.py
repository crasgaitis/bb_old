from pydub.utils import make_chunks
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


def do_transcription(input_path, output_txt, language='en'):
    audio = AudioSegment.from_file(input_path)
    
    chunk_length_ms = 10 * 1000  
    chunks = make_chunks(audio, chunk_length_ms)

    recognizer = sr.Recognizer()
    
    full_transcription = ""

    for i, chunk in enumerate(chunks):
        chunk_filename = f"chunk_{i}.wav"
        chunk.export(chunk_filename, format="wav")

        with sr.AudioFile(chunk_filename) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language=language)
                full_transcription += text + " "
            except sr.UnknownValueError:
                print(f"Chunk {i}: Could not understand audio")
            except sr.RequestError as e:
                print(f"Chunk {i}: Request error: {e}")

    with open(output_txt, 'w') as f:
        f.write(full_transcription)

    print(f"Transcription saved to {output_txt}")
