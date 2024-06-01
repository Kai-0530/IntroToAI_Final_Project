import paddle
from paddlespeech.cli.asr.infer import ASRExecutor
from pydub import AudioSegment
import os

# CUDA
device = paddle.get_device()
print("Using device:", device)

mp3_folder_path = 'Dataset\cv-corpus-17.0-2024-03-15\zh-TW\clips'
txt_folder_path = 'data_set_output'

filenames = [f for f in os.listdir(mp3_folder_path) if f.endswith('.mp3')]

asr = ASRExecutor()

for filename in filenames:
    mp3_file_path = os.path.join(mp3_folder_path, filename)
    
    # Convert mp3 to wav
    cvt_name = "tmp.wav"
    wav_filename = f"{os.path.splitext(filename)[0]}.wav"
    wav_path = os.path.join(mp3_folder_path, wav_filename)
    mp3_audio = AudioSegment.from_mp3(mp3_file_path)
    mp3_audio.export(cvt_name, format="wav")
    
    # Store result
    result = asr(audio_file=cvt_name, force_yes=True, device=device)
    txt_filename = f"{os.path.splitext(filename)[0]}.txt"
    txt_path = os.path.join(txt_folder_path, txt_filename)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"Result for {filename} saved to {txt_path}")