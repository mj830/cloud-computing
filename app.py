from random import random

from flask import Flask, request, g, render_template
from future.moves import subprocess

import config
from exts import db
from models import DreamModel
from ser import predict

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
with app.app_context():
    # db.drop_all()
    db.create_all()


@app.route('/')
def hello_world():  # put application's code here

    return render_template("add-dream.html")

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No file is uploaded', 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return 'No file is selected', 400

    random_number = random.randint(100000, 999999)
    input_file = "static/audio/" + str(random_number) + ".webm"
    output_file = "static/audio/" + str(random_number) + ".wav"

    # 保存原始文件
    audio_file.save(input_file)

    # 将.webm文件转换为.wav文件
    convert_webm_to_wav(input_file, output_file)

    # 使用ser.py的predict方法获取情绪标签
    predicted_labels = predict(output_file)
    tag = predicted_labels[0]  # 假设我们只关心第1个预测结果
    dream = DreamModel(audio=output_file, tag=tag)
    db.session.add(dream)
    db.session.commit()

    return {'message': 'File uploaded successfully', 'tag': tag}, 200
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

if __name__ == '__main__':
    app.run()


