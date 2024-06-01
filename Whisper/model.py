import whisper
from pydub import AudioSegment
import os

model = whisper.load_model("base") # Use "base" model

mp3_folder_path = 'Dataset\cv-corpus-17.0-2024-03-15\zh-TW\clips'
# mp3_folder_path = 'test_input'
txt_folder_path = 'data_output_w'
# txt_folder_path = 'test_output'

filenames = [f for f in os.listdir(mp3_folder_path) if f.endswith('.mp3')]

for filename in filenames:
    mp3_file_path = os.path.join(mp3_folder_path, filename)
    
    # Convert mp3 to wav
    wav_filename = f"{os.path.splitext(filename)[0]}.wav"
    wav_path = os.path.join(mp3_folder_path, wav_filename)
    mp3_audio = AudioSegment.from_mp3(mp3_file_path)
    mp3_audio.export("tmp.wav", format="wav")
    
    result = model.transcribe("tmp.wav")

    # Store the result
    txt_filename = f"{os.path.splitext(filename)[0]}.txt"
    txt_path = os.path.join(txt_folder_path, txt_filename)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(result['text'])
    # print(f"Result for {filename} saved to {txt_path}")
