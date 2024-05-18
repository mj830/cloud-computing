import random
import string
import logging
import psutil
import GPUtil
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

from sqlalchemy import func
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
    print("test")
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    return render_template("add-dream.html")

@ray.remote
def process_audio_file(file_data, filename):
    random_string = generate_random_string(12)
    input_file = os.path.join("static/audio", filename + "+" + random_string)
    output_file = input_file + ".wav"

    # 记录保存之前的CPU利用率
    cpu_before_save = psutil.cpu_percent(interval=None)

    # 获取 GPU 信息
    gpus = GPUtil.getGPUs()
    gpu_before_save = 0
    gpu_memory_before_save = 0
    if gpus:
        gpu_before_save = gpus[0].load * 100
        gpu_memory_before_save = gpus[0].memoryUsed

    # Save the uploaded file
    with open(input_file, 'wb') as f:
        f.write(file_data)

    # Convert .webm file to .wav file
    convert_webm_to_wav(input_file, output_file)

    # 记录保存之后的CPU利用率
    cpu_after_save = psutil.cpu_percent(interval=None)

    # 获取 GPU 信息
    gpus = GPUtil.getGPUs()
    gpu_after_save = 0
    gpu_memory_after_save = 0
    if gpus:
        gpu_after_save = gpus[0].load * 100
        gpu_memory_after_save = gpus[0].memoryUsed


    cpu_before = psutil.cpu_percent(interval=None)
    memory_before = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

    # 获取 GPU 信息
    gpus = GPUtil.getGPUs()
    gpu_before = 0
    gpu_memory_before = 0
    if gpus:
        gpu_before = gpus[0].load * 100
        gpu_memory_before = gpus[0].memoryUsed

    # 获取磁盘 I/O 信息
    disk_io_before = psutil.disk_io_counters()
    # 获取磁盘存储容量信息
    disk_usage_before = psutil.disk_usage('/')

    start_time = time.time()
    # Predict emotion using predict function
    predicted_labels = predict(output_file)

    cpu_after = psutil.cpu_percent(interval=None)
    memory_after = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

    # 获取 GPU 信息
    gpus = GPUtil.getGPUs()
    gpu_after = 0
    gpu_memory_after = 0
    if gpus:
        gpu_after = gpus[0].load * 100
        gpu_memory_after = gpus[0].memoryUsed

    # 获取磁盘 I/O 信息
    disk_io_after = psutil.disk_io_counters()
    # 获取磁盘存储容量信息
    disk_usage_after = psutil.disk_usage('/')

    # 计算磁盘 I/O 差异
    read_count_diff = disk_io_after.read_count - disk_io_before.read_count
    write_count_diff = disk_io_after.write_count - disk_io_before.write_count
    read_bytes_diff = disk_io_after.read_bytes - disk_io_before.read_bytes
    write_bytes_diff = disk_io_after.write_bytes - disk_io_before.write_bytes
    read_time_diff = disk_io_after.read_time - disk_io_before.read_time
    write_time_diff = disk_io_after.write_time - disk_io_before.write_time

    # 计算磁盘存储容量差异
    total_diff = disk_usage_after.total - disk_usage_before.total
    used_diff = disk_usage_after.used - disk_usage_before.used
    free_diff = disk_usage_after.free - disk_usage_before.free
    percent_diff = disk_usage_after.percent - disk_usage_before.percent


    execution_time = time.time() - start_time

    tag = predicted_labels[0]  # Assuming we only care about the first prediction result

    dream = DreamModel(audio=filename, tag=tag, run_time=execution_time)

    # Clean up files
    os.remove(input_file)
    os.remove(output_file)

    return dream, execution_time, cpu_before, cpu_after, memory_before, memory_after, cpu_before_save, cpu_after_save, gpu_before_save, gpu_after_save, gpu_memory_before_save, gpu_memory_after_save, gpu_before, gpu_after, gpu_memory_before, gpu_memory_after, disk_io_before, disk_io_after, read_count_diff, write_count_diff, read_bytes_diff, write_bytes_diff, read_time_diff, write_time_diff, disk_usage_before, disk_usage_after, total_diff, used_diff, free_diff, percent_diff


@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No file is uploaded', 400

    audio_files = request.files.getlist('audio')
    if not audio_files:
        return 'No file is uploaded', 400

    print("开始记录整体时间")
    # 记录整体开始时间
    start_time_general = time.time()

    number = len(audio_files)
    print(number)

    memory_before_upload = psutil.virtual_memory().used / (1024 * 1024)  # 将内存使用量转换为MB
    # 获取磁盘存储容量信息
    disk_usage_before_upload = psutil.disk_usage('/')

    # Prepare files for processing
    file_data_list = [(audio_file.read(), secure_filename(audio_file.filename)) for audio_file in audio_files]

    # Parallel processing using Ray
    futures = [process_audio_file.remote(file_data, filename) for file_data, filename in file_data_list]
    results = ray.get(futures)

    for dream, execution_time, cpu_before, cpu_after, memory_before, memory_after, cpu_before_save, cpu_after_save, gpu_before_save, gpu_after_save, gpu_memory_before_save, gpu_memory_after_save, gpu_before, gpu_after, gpu_memory_before, gpu_memory_after, disk_io_before, disk_io_after, read_count_diff, write_count_diff, read_bytes_diff, write_bytes_diff, read_time_diff, write_time_diff, disk_usage_before, disk_usage_after, total_diff, used_diff, free_diff, percent_diff in results:
        app.logger.info(f"CPU utilization before save: {cpu_before_save}%")
        app.logger.info(f"CPU utilization after save: {cpu_after_save}%")
        app.logger.info(f"GPU utilization before save: {gpu_before_save}%")
        app.logger.info(f"GPU utilization after save: {gpu_after_save}%")
        app.logger.info(f"GPU memory usage before save: {gpu_memory_before_save} MB")
        app.logger.info(f"GPU memory usage after save: {gpu_memory_after_save} MB")

        app.logger.info(f"CPU utilization before prediction: {cpu_before}%")
        app.logger.info(f"CPU utilization after prediction: {cpu_after}%")
        app.logger.info(f"Memory usage before prediction: {memory_before} MB")
        app.logger.info(f"Memory usage after prediction: {memory_after} MB")

        app.logger.info(f"GPU utilization before prediction: {gpu_before}%")
        app.logger.info(f"GPU utilization after prediction: {gpu_after}%")
        app.logger.info(f"GPU memory usage before prediction: {gpu_memory_before} MB")
        app.logger.info(f"GPU memory usage after prediction: {gpu_memory_after} MB")

        app.logger.info(f"Disk I/O before prediction: {disk_io_before}")
        app.logger.info(f"Disk I/O after prediction: {disk_io_after}")
        app.logger.info(
            f"Disk I/O difference - read_count: {read_count_diff}, write_count: {write_count_diff}, read_bytes: {read_bytes_diff}, write_bytes: {write_bytes_diff}, read_time: {read_time_diff}, write_time: {write_time_diff}")

        # 记录磁盘存储容量信息及差异
        app.logger.info(
            f"Disk usage before prediction: total={disk_usage_before.total} bytes, used={disk_usage_before.used} bytes, free={disk_usage_before.free} bytes, percent={disk_usage_before.percent}%")
        app.logger.info(
            f"Disk usage after prediction: total={disk_usage_after.total} bytes, used={disk_usage_after.used} bytes, free={disk_usage_after.free} bytes, percent={disk_usage_after.percent}%")
        app.logger.info(
            f"Disk usage difference - total: {total_diff} bytes, used: {used_diff} bytes, free: {free_diff} bytes, percent: {percent_diff}%")

        app.logger.info(f"Execution time: {execution_time} seconds")
        db.session.add(dream)

    # 记录整体结束时间
    end_time_general = time.time()  # 结束计时
    execution_time_general = end_time_general - start_time_general
    app.logger.info(f"----- [ --- General Execution time for {number} files: {execution_time_general} seconds --- ] -----")  # 记录性能

    db.session.commit()

    memory_after_upload = psutil.virtual_memory().used / (1024 * 1024)  # 将内存使用量转换为MB
    memory_diff_upload = memory_after_upload - memory_before_upload
    app.logger.info(f"Memory usage difference (Upload audio): {memory_diff_upload} MB")

    # 获取磁盘存储容量信息
    disk_usage_after_upload = psutil.disk_usage('/')
    # 计算磁盘存储容量差异
    total_diff_upload = disk_usage_after_upload.total - disk_usage_before_upload.total
    used_diff_upload = disk_usage_after_upload.used - disk_usage_before_upload.used
    free_diff_upload = disk_usage_after_upload.free - disk_usage_before_upload.free
    percent_diff_upload = disk_usage_after_upload.percent - disk_usage_before_upload.percent
    app.logger.info(
        f"Disk usage difference (Upload audio)- total: {total_diff_upload} bytes, used: {used_diff_upload} bytes, free: {free_diff_upload} bytes, percent: {percent_diff_upload}%")

    total_run_time = db.session.query(func.sum(DreamModel.run_time)).scalar()
    app.logger.info(f"----- [ --- Origin sum for Execution times: {total_run_time} seconds --- ] -----")  # 记录初始总时间

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
    app.run(host='0.0.0.0')



