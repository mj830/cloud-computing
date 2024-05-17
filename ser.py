import joblib
import librosa as librosa
import pandas as pd

import extract_features
from keras.models import load_model
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder


def predict(input_file):
    # 加载模型
    model = load_model('emotion_recognition.keras')

    # 准备测试数据
    path_to_audio = input_file

    # 特征提取
    data, sampling_rate = librosa.load(path_to_audio)
    # 其他预处理步骤（如果需要），例如将数据转换为模型期望的格式
    feature = extract_features.get_features(path_to_audio)
    # print(feature)
    # for ele in feature:
    #     X.append(ele)
    # 加载预训练的标准化器
    scaler = joblib.load('scaler_model.pkl')
    # 第三步：标准化特征
    feature = np.array(feature).reshape(1, -1)  # 确保 feature 是二维数组
    feature_scaled = scaler.transform(feature)

    # 第四步：调整特征维度
    feature_scaled = np.expand_dims(feature_scaled, axis=2)
    predictions = model.predict(feature_scaled)

    # X.append(feature)
    # Features = pd.DataFrame(X)
    #
    # scaler.fit(Features)  # 拟合标准化器
    #
    # data_scaled = scaler.transform(X)
    #
    # # 调整数据维度
    # data_reshaped = np.expand_dims(data_scaled, axis=2)
    #
    # # 进行预测
    # predictions = model.predict(data_reshaped)
    # 获取概率最高的两个情绪
    top_indices = predictions[0].argsort()[-2:][::-1]  # 获取概率最高的两个索引，按概率从高到低排序

    # 第七步：解码预测结果（假设您有一个OneHotEncoder用于Y标签）
    encoder = OneHotEncoder()
    encoder.fit(np.array(['neutral', 'happy', 'sad', 'angry', 'fear']).reshape(-1, 1))  # 替换为实际的标签种类

    # 获取对应的标签
    labels = encoder.categories_[0]  # 获取所有标签
    top_labels = labels[top_indices]  # 获取概率最高的两个标签

    # 将结果以列表形式返回
    result = top_labels.tolist()
    print("Top 2 Predictions:", result)
    # 输出预测结果
    print(predictions)
    print(predictions[0])
    #
    # arr = np.array(predictions[0])
    #
    # # 找到最大值和第二大值的索引
    # max_index = np.argmax(arr)
    # arr[max_index] = -np.inf  # 将最大值设为负无穷，以便找第二大值
    # second_max_index = np.argmax(arr)
    #
    # # 定义类别标签列表（根据你的具体情况修改）
    # class_labels = ['neutral', 'happy', 'sad', 'angry', 'fear']
    #
    # # 根据索引获取类别标签
    # predicted_labels = class_labels[max_index]
    # predicted_labels2 = class_labels[second_max_index]
    #
    # labels = [predicted_labels, predicted_labels2]
    # 输出预测结果
    return result
#
# input_file = "static/audio/1+249533.wav"
# print(predict(input_file))
# input_file2 = "audio/1002_TSI_FEA_XX.wav"
# print(predict(input_file2))
# print(predict( "audio/1003_DFA_HAP_XX.wav"))
# print(predict( "audio/1002_WSI_ANG_XX.wav"))

