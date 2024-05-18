import random
import string
import logging
import psutil
import ray

from flask import Flask, request, g, render_template, redirect, url_for
from future.moves import subprocess
from werkzeug.utils import secure_filename

import config
from exts import db
from models import DreamModel
from ser import predict
import time

import os
import shutil
from logging.handlers import RotatingFileHandler

# 配置日志记录器
# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
file_handler = RotatingFileHandler(filename='app.log', maxBytes=10000, backupCount=1)

# 配置日志记录器
# file_handler = RotatingFileHandler(filename='app.log', maxBytes=10000, backupCount=1)
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# file_handler.setFormatter(formatter)

# 获取根日志记录器并添加处理器
# logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().addHandler(file_handler)


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
with app.app_context():
    db.drop_all()
    db.create_all()

# 配置日志处理器
app.logger.addHandler(file_handler)

ray.init()

@app.route('/')
def hello_world():  # put application's code here
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    return render_template("add-dream.html")

@ray.remote
def process_audio_file(file_data, filename):
    random_string = generate_random_string(12)
    input_file = os.path.join("static/audio", filename + "+" + random_string)
    output_file = input_file + ".wav"

    # Save the uploaded file
    with open(input_file, 'wb') as f:
        f.write(file_data)

    # Convert .webm file to .wav file
    convert_webm_to_wav(input_file, output_file)

    start_time = time.time()
    cpu_before = psutil.cpu_percent(interval=None)
    memory_before = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

    # Predict emotion using predict function
    predicted_labels = predict(output_file)

    cpu_after = psutil.cpu_percent(interval=None)
    memory_after = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

    execution_time = time.time() - start_time

    tag = predicted_labels[0]  # Assuming we only care about the first prediction result

    dream = DreamModel(audio=filename, tag=tag, run_time=execution_time)

    # Clean up files
    os.remove(input_file)
    os.remove(output_file)

    return dream, execution_time, cpu_before, cpu_after, memory_before, memory_after


@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No file is uploaded', 400

    audio_files = request.files.getlist('audio')
    if not audio_files:
        return 'No file is uploaded', 400

    # 记录整体开始时间
    start_time_general = time.time()

    number = len(audio_files)
    print(number)

    # Prepare files for processing
    file_data_list = [(audio_file.read(), secure_filename(audio_file.filename)) for audio_file in audio_files]

    # Parallel processing using Ray
    futures = [process_audio_file.remote(file_data, filename) for file_data, filename in file_data_list]
    results = ray.get(futures)

    for dream, execution_time, cpu_before, cpu_after, memory_before, memory_after in results:
        app.logger.info(f"CPU utilization before prediction: {cpu_before}%")
        app.logger.info(f"CPU utilization after prediction: {cpu_after}%")
        app.logger.info(f"Memory usage before prediction: {memory_before} MB")
        app.logger.info(f"Memory usage after prediction: {memory_after} MB")
        app.logger.info(f"Execution time: {execution_time} seconds")
        db.session.add(dream)

    # 记录整体结束时间
    end_time_general = time.time()  # 结束计时
    execution_time_general = end_time_general - start_time_general
    app.logger.info(f"----- [ --- General Execution time for {number} files: {execution_time_general} seconds --- ] -----")  # 记录性能

    db.session.commit()

    folder_to_clear = 'static/audio'
    clear_folder(folder_to_clear)

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

def generate_random_string(length):
    letters = string.ascii_letters + string.digits  # 包含字母和数字
    return ''.join(random.choice(letters) for _ in range(length))

def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        app.logger.warning(f"The folder {folder_path} does not exist.")  # 记录警告
        return

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            app.logger.error(f"Failed to delete {file_path}. Reason: {e}")  # 记录错误

if __name__ == '__main__':
    app.run()



