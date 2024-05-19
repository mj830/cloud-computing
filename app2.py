import random
import string
import logging
import psutil
import GPUtil

import matplotlib
matplotlib.use('Agg')  # 使用 Agg 后端
import matplotlib.pyplot as plt

from flask import Flask, request, g, render_template, redirect, url_for
from future.moves import subprocess

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

@app.route('/')
def hello_world():  # put application's code here
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    return render_template("add-dream.html")

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

    memory_before_upload = psutil.virtual_memory().used / (1024 * 1024)  # 将内存使用量转换为MB
    # 获取磁盘存储容量信息
    disk_usage_before_upload = psutil.disk_usage('/')

    # 初始化数据收集
    cpu_utilization_save = []
    gpu_utilization_save = []
    cpu_utilization_predict = []
    gpu_utilization_predict = []
    gpu_memory_usage_save = []
    gpu_memory_usage_predict = []
    disk_io_stats = []
    disk_io_stats_save = []
    execution_times = []

    for audio_file in audio_files:
        print(audio_file)

        # 获取磁盘 I/O 信息
        disk_io_before_save = psutil.disk_io_counters()

        filename = audio_file.filename
        random_string = generate_random_string(12)
        input_file = "static/audio/" + filename + "+" + random_string
        output_file = "static/audio/" + filename + "+" + random_string +".wav"

        # 记录保存之前的CPU利用率
        cpu_before_save = psutil.cpu_percent(interval=None)

        # 获取 GPU 信息
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_before_save = gpus[0].load * 100
            gpu_memory_before_save = gpus[0].memoryUsed

        # 保存文件
        audio_file.save(input_file)
        # 将.webm文件转换为.wav文件
        convert_webm_to_wav(input_file, output_file)

        # 记录保存之后的CPU利用率
        cpu_after_save = psutil.cpu_percent(interval=None)
        # 记录保存文件前后CPU
        app.logger.info(f"CPU utilization before save: {cpu_before_save}%")
        app.logger.info(f"CPU utilization after save: {cpu_after_save}%")
        # 获取 GPU 信息
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_after_save = gpus[0].load * 100
            gpu_memory_after_save = gpus[0].memoryUsed
        if gpus:
            app.logger.info(f"GPU utilization before save: {gpu_before_save}%")
            app.logger.info(f"GPU utilization after save: {gpu_after_save}%")
            app.logger.info(f"GPU memory usage before save: {gpu_memory_before_save} MB")
            app.logger.info(f"GPU memory usage after save: {gpu_memory_after_save} MB")

        # 可视化CPU，GPU
        cpu_utilization_save.append((cpu_before_save, cpu_after_save))
        if gpus:
            gpu_utilization_save.append((gpu_before_save, gpu_after_save))
            gpu_memory_usage_save.append((gpu_memory_before_save, gpu_memory_after_save))

        # 获取磁盘 I/O 信息
        disk_io_after_save = psutil.disk_io_counters()

        # 计算磁盘 I/O 差异
        read_bytes_diff_save = disk_io_after_save.read_bytes - disk_io_before_save.read_bytes
        write_bytes_diff_save = disk_io_after_save.write_bytes - disk_io_before_save.write_bytes

        # 可视化disk io
        disk_io_stats_save.append((read_bytes_diff_save, write_bytes_diff_save))


        ### 预测阶段
        # 记录预测开始时的CPU利用率
        cpu_before = psutil.cpu_percent(interval=None)
        memory_before = psutil.virtual_memory().used / (1024 * 1024)  # 将内存使用量转换为MB

        # 获取 GPU 信息
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_before = gpus[0].load * 100
            gpu_memory_before = gpus[0].memoryUsed

        # 获取磁盘 I/O 信息
        disk_io_before = psutil.disk_io_counters()
        # 获取磁盘存储容量信息
        disk_usage_before = psutil.disk_usage('/')

        start_time = time.time()  # 开始计时
        # 使用ser.py的predict方法获取情绪标签
        predicted_labels = predict(output_file)
        end_time = time.time()  # 结束计时

        # 记录预测结束时的CPU利用率
        cpu_after = psutil.cpu_percent(interval=None)
        memory_after = psutil.virtual_memory().used / (1024 * 1024)  # 将内存使用量转换为MB

        # 获取 GPU 信息
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_after = gpus[0].load * 100
            gpu_memory_after = gpus[0].memoryUsed

        # 可视化预测后CPU，GPU
        cpu_utilization_predict.append((cpu_before, cpu_after))
        if gpus:
            gpu_utilization_predict.append((gpu_before, gpu_after))
            gpu_memory_usage_predict.append((gpu_memory_before, gpu_memory_after))

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

        # 可视化disk io
        disk_io_stats.append((read_bytes_diff, write_bytes_diff))

        # 计算磁盘存储容量差异
        total_diff = disk_usage_after.total - disk_usage_before.total
        used_diff = disk_usage_after.used - disk_usage_before.used
        free_diff = disk_usage_after.free - disk_usage_before.free
        percent_diff = disk_usage_after.percent - disk_usage_before.percent

        app.logger.info(f"CPU utilization before prediction: {cpu_before}%")
        app.logger.info(f"CPU utilization after prediction: {cpu_after}%")
        app.logger.info(f"Memory usage before prediction: {memory_before} MB")
        app.logger.info(f"Memory usage after prediction: {memory_after} MB")

        if gpus:
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

        execution_time = end_time - start_time
        # 可视化执行时间
        execution_times.append(execution_time)
        app.logger.info(f"Execution time: {execution_time} seconds")  # 记录性能

        tag = predicted_labels[0]  # 假设我们只关心第1个预测结果

        dream = DreamModel(audio=filename, tag=tag, run_time=execution_time)
        db.session.add(dream)

    # 记录整体结束时间
    end_time_general = time.time()  # 结束计时
    # 可视化execution time
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

    # 可视化图表
    generate_plots(cpu_utilization_save, gpu_utilization_save, cpu_utilization_predict, gpu_utilization_predict, gpu_memory_usage_save, gpu_memory_usage_predict, disk_io_stats_save, disk_io_stats, execution_times)

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


def generate_plots(cpu_utilization_save, gpu_utilization_save, cpu_utilization_predict, gpu_utilization_predict, gpu_memory_usage_save, gpu_memory_usage_predict, disk_io_stats_save, disk_io_stats, execution_times):
    # CPU Utilization Plot
    plt.figure()
    plt.plot([x[0] for x in cpu_utilization_save], label='Before Save')
    plt.plot([x[1] for x in cpu_utilization_save], label='After Save')
    plt.xlabel('File Index')
    plt.ylabel('CPU Utilization (%)')
    plt.title('CPU Utilization Before and After Save')
    plt.legend()
    plt.savefig('static/plots/cpu_utilization_save.png')

    # CPU Prediction Utilization Plot
    plt.figure()
    plt.plot([x[0] for x in cpu_utilization_predict], label='Before Predict')
    plt.plot([x[1] for x in cpu_utilization_predict], label='After Predict')
    plt.xlabel('File Index')
    plt.ylabel('CPU Utilization (%)')
    plt.title('CPU Utilization Before and After Predict')
    plt.legend()
    plt.savefig('static/plots/cpu_utilization_predict.png')

    # GPU Utilization Plot
    if gpu_utilization_save:
        plt.figure()
        plt.plot([x[0] for x in gpu_utilization_save], label='Before Save')
        plt.plot([x[1] for x in gpu_utilization_save], label='After Save')
        plt.xlabel('File Index')
        plt.ylabel('GPU Utilization (%)')
        plt.title('GPU Utilization Before and After Save')
        plt.legend()
        plt.savefig('static/plots/gpu_utilization_save.png')

    # GPU Predict Utilization Plot
    if gpu_utilization_predict:
        plt.figure()
        plt.plot([x[0] for x in gpu_utilization_save], label='Before Predict')
        plt.plot([x[1] for x in gpu_utilization_save], label='After Predict')
        plt.xlabel('File Index')
        plt.ylabel('GPU Utilization (%)')
        plt.title('GPU Utilization Before and After Predict')
        plt.legend()
        plt.savefig('static/plots/gpu_utilization_predict.png')

    # Memory Usage Plot
    if gpu_memory_usage_save:
        plt.figure()
        plt.plot([x[0] for x in gpu_memory_usage_save], label='Before Save')
        plt.plot([x[1] for x in gpu_memory_usage_save], label='After Save')
        plt.xlabel('File Index')
        plt.ylabel('Memory Usage (MB)')
        plt.title('GPU Memory Usage Before and After Save')
        plt.legend()
        plt.savefig('static/plots/gpu_memory_usage_save.png')

    # Memory Usage Plot
    if gpu_memory_usage_predict:
        plt.figure()
        plt.plot([x[0] for x in gpu_memory_usage_save], label='Before Predict')
        plt.plot([x[1] for x in gpu_memory_usage_save], label='After Predict')
        plt.xlabel('File Index')
        plt.ylabel('Memory Usage (MB)')
        plt.title('GPU Memory Usage Before and After Predict')
        plt.legend()
        plt.savefig('static/plots/gpu_memory_usage_predict.png')

    # Disk I/O Plot save
    plt.figure()
    read_bytes = [x[0] for x in disk_io_stats_save]
    write_bytes = [x[1] for x in disk_io_stats]
    plt.bar(range(len(disk_io_stats_save)), read_bytes, label='Read Bytes')
    plt.bar(range(len(disk_io_stats_save)), write_bytes, label='Write Bytes', bottom=read_bytes)
    plt.xlabel('File Index')
    plt.ylabel('Bytes')
    plt.title('Disk I/O Bytes Read and Written (Save)')
    plt.legend()
    plt.savefig('static/plots/disk_io_save.png')

    # Disk I/O Plot
    plt.figure()
    read_bytes = [x[0] for x in disk_io_stats]
    write_bytes = [x[1] for x in disk_io_stats]
    plt.bar(range(len(disk_io_stats)), read_bytes, label='Read Bytes')
    plt.bar(range(len(disk_io_stats)), write_bytes, label='Write Bytes', bottom=read_bytes)
    plt.xlabel('File Index')
    plt.ylabel('Bytes')
    plt.title('Disk I/O Bytes Read and Written')
    plt.legend()
    plt.savefig('static/plots/disk_io_predict.png')

    # Execution Times Plot
    plt.figure()
    plt.plot(execution_times, marker='o')
    plt.xlabel('File Index')
    plt.ylabel('Execution Time (s)')
    plt.title('Execution Time for Each Audio File')
    plt.savefig('static/plots/execution_times.png')

    # 总执行时间图
    plt.figure()
    plt.bar(['Total Execution Time'], [sum(execution_times)])
    plt.ylabel('Total Execution Time (s)')
    plt.title('Total Execution Time for All Files')
    plt.savefig('static/plots/total_execution_time.png')


if __name__ == '__main__':
    app.run(host='0.0.0.0')



