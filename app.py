from random import random

from flask import Flask, request, g, render_template, redirect, url_for
from future.moves import subprocess

import config
from exts import db
from models import DreamModel
from ser import predict
import time

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
with app.app_context():
    db.drop_all()
    db.create_all()


@app.route('/')
def hello_world():  # put application's code here
    return render_template("add-dream.html")

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No file is uploaded', 400

    audio_files = request.files.getlist('audio')
    if not audio_files:
        return 'No file is uploaded', 400

    for audio_file in audio_files:
        print(audio_file)
        start_time = time.time()  # 开始计时

        filename = audio_file.filename
        input_file = "static/audio/" + filename
        output_file = "static/audio/" + filename

        audio_file.save(input_file)

        # 将.webm文件转换为.wav文件
        convert_webm_to_wav(input_file, output_file)

        # 使用ser.py的predict方法获取情绪标签
        predicted_labels = predict(output_file)
        tag = predicted_labels[0]  # 假设我们只关心第1个预测结果

        end_time = time.time()  # 结束计时
        execution_time = end_time - start_time

        dream = DreamModel(audio=filename, tag=tag, run_time=execution_time)
        db.session.add(dream)

    db.session.commit()

    return redirect(url_for("my_dream"))

def convert_webm_to_wav(input_file, output_file):
    """
    Converts a .webm file to a .wav file using FFmpeg.

    Args:
    - input_file: The path to the input .webm file.
    - output_file: The path where the output .wav file will be saved.
    """
    # Constructing the FFmpeg command for conversion
    command = ['ffmpeg', '-i', input_file, output_file]

    try:
        # Executing the FFmpeg command
        subprocess.run(command, check=True)
        print(f"Conversion successful. File saved as {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

@app.route("/my_dream")
def my_dream():
    page_all = request.args.get("page_all", 1, type=int)
    dreams = DreamModel.query.filter_by().paginate(page=page_all, per_page=4)

    return render_template("my_dream_list.html", dreams=dreams, pagination=dreams)

if __name__ == '__main__':
    app.run()


