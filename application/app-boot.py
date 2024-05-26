import os
import openai
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify, send_file
from flask_bootstrap import Bootstrap
from pathlib import Path
from pytube import YouTube
import torch
import whisper
from whisper.utils import get_writer
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from datetime import datetime
import json
import markdown

app = Flask(__name__)
Bootstrap(app)
UPLOAD_FOLDER = './temp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max file size (50MB)
ALLOWED_EXTENSIONS = set(['pdf','txt', 'png', 'jpg', 'jpeg', 'gif','mp3','mp4','m4a'])

# Load OpenAI API key -> you need to set your own API key here
openai.api_key = ''
# Use CUDA, if available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base").to(DEVICE)

database = {
    'temp.txt': './temp/temp.txt',
    'temp.md': './temp/temp.md',
    'temp.srt': './temp/temp.srt',
    'temp.vtt': './temp/temp.vtt',
    'temp.tsv': './temp/temp.tsv',
}

def to_snake_case(name):
    return name.lower().replace(" ", "_").replace(":", "_").replace("__", "_")

def download_youtube_audio(url,  file_name = None):
    target_path = "./temp/"
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=target_path)
    video_title, ext = os.path.splitext(out_file)
    file_name = video_title + '.mp3'
    os.rename(out_file, file_name)
    return file_name

def download_multiple_files(files_to_send):
    zip_filename = './temp/transripts.zip'
    with ZipFile(zip_filename, 'w') as zipf:
        for file in files_to_send:
            zipf.write(file)
            os.remove(file)
    response = send_file(zip_filename, as_attachment=True)
    return response

def save_response_to_markdown(filename, response, files_to_send):
    name = filename.split('.')[0]
    response_filename = f"{name}.md"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], response_filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response)
    files_to_send.append(file_path)
    return response_filename

def chatgpt(file, filename, files_to_send):
    with open(file, 'r', encoding='utf-8') as f:
        transcript = f.read()

    print("Sending....", filename)
    prompt = "這是一段逐字稿。我需要詳細內容摘要並以Markdown格式輸出。以繁體中文回答。內容如下：\n\n" + transcript

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )

    summary = response.choices[0].message['content'].strip()
    print(summary)
    response_filename = save_response_to_markdown(filename, summary, files_to_send)
    return response_filename


@app.route('/transcribe_file', methods=['POST'])
def transcribe_file(model, file, plain, srt, vtt, tsv, summarize):
    files_to_send = []
    file_path = Path(file)
    output_directory = file_path.parent
    result = model.transcribe(file, verbose=False)
    options = {
        'max_line_width': None,
        'max_line_count': None,
        'highlight_words': False
    }
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open('./temp/upload-record.txt', 'a') as f:
        f.write(current_time + ': ' + str(file_path.stem) + '\n')
    txt_writer = get_writer("txt", output_directory)
    txt_writer(result, str(file_path.stem), options)
    txt_writer(result, 'temp', options)
    if plain:
        result_file = os.path.join(app.config['UPLOAD_FOLDER'], str(file_path.stem) + '.txt')
        files_to_send.append(result_file)
    if srt:
        srt_writer = get_writer("srt", output_directory)
        srt_writer(result, str(file_path.stem), options)
        srt_writer(result, 'temp', options)
        result_file = os.path.join(app.config['UPLOAD_FOLDER'], str(file_path.stem) + '.srt')
        files_to_send.append(result_file)
    if vtt:
        vtt_writer = get_writer("vtt", output_directory)
        vtt_writer(result, str(file_path.stem), options)
        vtt_writer(result, 'temp', options)
        result_file = os.path.join(app.config['UPLOAD_FOLDER'], str(file_path.stem) + '.vtt')
        files_to_send.append(result_file)
    if tsv:
        tsv_writer = get_writer("tsv", output_directory)
        tsv_writer(result, str(file_path.stem), options)
        tsv_writer(result, 'temp', options)
        result_file = os.path.join(app.config['UPLOAD_FOLDER'], str(file_path.stem) + '.tsv')
        files_to_send.append(result_file)
    if summarize:
        txt_file = os.path.join(app.config['UPLOAD_FOLDER'], str(file_path.stem) + '.txt')
        try:
            chatgpt(txt_file, str(file_path.stem), files_to_send)
        except Exception as e:
            print(f"Failed to summarize: {e}")
    os.remove(file)
    response = download_multiple_files(files_to_send)
    return response

@app.route('/')
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/transcribe', methods=['POST', 'GET'])
def transcribe():
    if request.method == 'POST':
        input_format = request.form.get('input_format')
        plain = request.form.get('plain') == 'true'
        srt = request.form.get('srt') == 'true'
        vtt = request.form.get('vtt') == 'true'
        tsv = request.form.get('tsv') == 'true'
        summarize = request.form.get('summarize') == 'true'
        result = None
        file = None
        if input_format == 'youtube':
            url = request.form.get('url')
            audio = download_youtube_audio(url)
            result = transcribe_file(model, audio, plain, srt, vtt, tsv, summarize)
        else:
            if input_format == 'mp3':
                file = request.files['mp3_file']
            elif input_format == 'm4a':
                file = request.files['m4a_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                result = transcribe_file(model, os.path.join(app.config['UPLOAD_FOLDER'], filename), plain, srt, vtt, tsv, summarize)
        file_list = []
        if summarize:
            file_list.append('summary')
        if plain:
            file_list.append('txt')
        if srt:
            file_list.append('srt')
        if vtt:
            file_list.append('vtt')
        if tsv:
            file_list.append('tsv')
        file_list_str = json.dumps(file_list)
        return redirect(url_for('select_result', file_list=file_list_str))
    return redirect(url_for('index'))

@app.route('/select_result', methods=['GET', 'POST'])
def select_result():
    file_list_str = request.args.get('file_list', default="[]")
    file_list = json.loads(file_list_str)
    if request.method == 'POST':
        selected_file = request.form['selected_file']
        if selected_file == 'summary':
            selected_file = 'md'
        return redirect(url_for('view_file', filename="temp." + selected_file, file_list=file_list_str))
    return render_template('select_file.html', selectfile_list=file_list)

@app.route('/result/<filename>')
def view_file(filename):
    file_list_str = request.args.get('file_list', default="[]")
    file_list = json.loads(file_list_str)
    import urllib.parse
    url_encoded = urllib.parse.quote(str(file_list).replace("'", '"'))
    if filename in database:
        file_path = database[filename]
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                if filename.endswith('.md'):
                    markdown_text = file.read()
                    content = markdown.markdown(markdown_text, extensions=['extra', 'toc', 'tables', 'codehilite', 'fenced_code'])
                else:
                    content = file.read()
            return render_template('file_content.html', content=content, url_encoded=url_encoded)
        else:
            return "文件不存在。"
    else:
        return "非法文件請求。"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
