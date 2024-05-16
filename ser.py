import librosa as librosa
import pandas as pd

import extract_features
from keras.models import load_model
import numpy as np
from sklearn.preprocessing import StandardScaler


def predict(input_file):
    # 加载模型
    model = load_model('emotion_recognition.keras')

    # 准备测试数据
    path_to_audio = input_file

    # 特征提取
    data, sampling_rate = librosa.load(path_to_audio)
    # 其他预处理步骤（如果需要），例如将数据转换为模型期望的格式

    X, Y = [], []
    feature = extract_features.get_features(path_to_audio)
    for ele in feature:
        X.append(ele)
        # appending emotion 3 times as we have made 3 augmentation techniques on each audio file.
    # 标准化

    Features = pd.DataFrame(X)
    X = Features.iloc[:, :-1].values

    scaler = StandardScaler()
    # X = scaler.fit_transform(X)
    scaler.fit(Features.iloc[:, :-1].values)  # 拟合标准化器

    data_scaled = scaler.transform(X)

    # 调整数据维度
    data_reshaped = np.expand_dims(data_scaled, axis=2)

    # 进行预测
    predictions = model.predict(data_reshaped)

    # 输出预测结果
    # print(predictions)
    # print(predictions[0])

    arr = np.array(predictions[0])

    # 找到最大值和第二大值的索引
    max_index = np.argmax(arr)
    arr[max_index] = -np.inf  # 将最大值设为负无穷，以便找第二大值
    second_max_index = np.argmax(arr)

    # 定义类别标签列表（根据你的具体情况修改）
    class_labels = ['neutral', 'happy', 'sad', 'angry', 'fear']

    # 根据索引获取类别标签
    predicted_labels = class_labels[max_index]
    predicted_labels2 = class_labels[second_max_index]

    labels = [predicted_labels, predicted_labels2]
    # 输出预测结果
    return labels
#
input_file = "static/audio/1001_DFA_SAD_XX.wav"
print(predict(input_file))
# input_file2 = "audio/1+958094.wav"
# predict(input_file2)