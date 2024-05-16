import os
from datetime import datetime

from flask import Blueprint, request, render_template, session, flash, redirect, url_for, jsonify, g
from future.moves import subprocess
from sqlalchemy import or_, and_

from exts import db
from models import UserModel, DreamModel, ActivityModel

import random

import joblib

from ser import predict
from ml import predict_text, activity_tag
from sqlalchemy import or_

model = joblib.load('random_forest.joblib')

bp = Blueprint("dream", __name__, url_prefix="/dream")
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


@bp.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "GET":

        user = g.user
        last_dreams = DreamModel.query.filter_by(author_id=g.user.id).order_by(DreamModel.id.desc()).limit(3).all()
        # activities_art = ActivityModel.query.filter_by(classsification="Art").order_by(ActivityModel.id.desc()).limit(
        #     3).all()
        # activities_sport = ActivityModel.query.filter_by(classsification="Sport").order_by(
        #     ActivityModel.id).limit(3).all()
        # activities_leisure = ActivityModel.query.filter_by(classsification="Leisure").order_by(
        #     ActivityModel.id.desc()).limit(3).all()
        activities = ActivityModel.query.order_by(ActivityModel.id.desc()).limit(4).all()


        return render_template("add-dream.html", user=user, last_dreams=last_dreams,
                               activities=activities)
    else:

        data = request.form

        title = data["title"]
        content = data["message"]
        whether = data["Weather"]
        sleep = data["sleepDuration"]

        user_id = g.user.id

        # tag = model.predict([content])
        result = predict_text([content])[0]
        tags = activity_tag([content])
        activity_ids = find_activities_with_tags(tags)
        activity_ids_str = ','.join(map(str, activity_ids))
        # result = tag[0]
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        dream = DreamModel(title=title, content=content, whether=whether, sleep=sleep,author_id=user_id, tag=result, activity_ids=activity_ids_str, create_time=current_time)
        db.session.add(dream)
        db.session.commit()

        flash("Add successfully", category='success')
        return redirect(url_for("dream.my_dream"))


def find_activities_with_tags(tags):
    # tags 应该是一个包含两个元素的列表
    tag1, tag2 = tags
    print(tag1, tag2)

    # 查询数据库找到同时包含这两个标签的活动
    activities = ActivityModel.query.filter(
        or_(
            and_(ActivityModel.tag_1 == tag1, ActivityModel.tag_2 == tag2),
            and_(ActivityModel.tag_1 == tag1, ActivityModel.tag_3 == tag2),
            and_(ActivityModel.tag_2 == tag1, ActivityModel.tag_3 == tag2),
            and_(ActivityModel.tag_1 == tag2, ActivityModel.tag_2 == tag1),
            and_(ActivityModel.tag_1 == tag2, ActivityModel.tag_3 == tag1),
            and_(ActivityModel.tag_2 == tag2, ActivityModel.tag_3 == tag1)
        )
    ).all()
    print("activities:", activities)

    # 收集所有活动的ID
    activity_ids = [activity.id for activity in activities]
    return activity_ids

@bp.route("/check_dream/<int:dream_id>", methods=["GET", "POST"])
def check_dream(dream_id):
    if request.method == "GET":
        dream = DreamModel.query.filter_by(id=dream_id).first()
        title = dream.title
        content = dream.content
        whether = dream.whether
        sleep = dream.sleep
        tag = dream.tag
        data = dream.create_time
        audio = dream.audio
        activity_ids_str = dream.activity_ids
        name = UserModel.name

        activity_ids = activity_ids_str.split(',') if activity_ids_str else []
        activity_ids = [int(id) for id in activity_ids]

        page_number = request.args.get("page", 1, type=int)
        per_page = 4
        activities = ActivityModel.query.filter(ActivityModel.id.in_(activity_ids)).paginate(page=page_number, per_page=per_page)
        print(activities)
        return render_template("dream_details.html", title=title, content=content, whether=whether, sleep=sleep, tag=tag,
                               dream_id=dream_id,data=data, audio=audio, name=name, activities=activities)
    else:
        return redirect(url_for("dream.check_dream", dream_id=dream_id))

@bp.route("/my_dream")
def my_dream():
    session["route"] = "dream.my_dream"
    page_all = request.args.get("page_all", 1, type=int)
    dreams = DreamModel.query.filter_by(author_id=g.user.id).order_by(DreamModel.id.desc()).paginate(page=page_all,
                                                                                                     per_page=4)
    dreams_items = dreams.items
    dreams2 = DreamModel.query.filter_by(author_id=g.user.id).order_by(DreamModel.id.desc()).all()

    page_happy = request.args.get("page_happy", 1, type=int)
    dreams_happy = DreamModel.query.filter_by(author_id=g.user.id, tag="happy").order_by(DreamModel.id.desc()).paginate(
        page=page_happy, per_page=4)

    page_sad = request.args.get("page_sad", 1, type=int)
    dreams_sad = DreamModel.query.filter_by(author_id=g.user.id, tag="sad").order_by(DreamModel.id.desc()).paginate(
        page=page_sad, per_page=4)

    page_angry = request.args.get("page_angry", 1, type=int)
    dreams_angry = DreamModel.query.filter_by(author_id=g.user.id, tag="angry").order_by(DreamModel.id.desc()).paginate(
        page=page_angry, per_page=4)

    page_fear = request.args.get("page_fear", 1, type=int)
    dreams_fear = DreamModel.query.filter_by(author_id=g.user.id, tag="fear").order_by(DreamModel.id.desc()).paginate(
        page=page_fear, per_page=4)

    page_neutral = request.args.get("page_neutral", 1, type=int)
    dreams_neutral = DreamModel.query.filter_by(author_id=g.user.id, tag="neutral").order_by(
        DreamModel.id.desc()).paginate(page=page_neutral, per_page=4)

    activities_entertainment = ActivityModel.query.filter_by(classsification="Entertainment").order_by(ActivityModel.id.desc()).limit(
        3).all()
    activities_food = ActivityModel.query.filter_by(classsification="Food").order_by(
        ActivityModel.id.desc()).limit(3).all()
    activities_other = ActivityModel.query.filter_by(classsification="Other").order_by(
        ActivityModel.id.desc()).limit(3).all()

    return render_template("my_dream_list.html", dreams=dreams, dreams_items=dreams_items, pagination=dreams,
                           user=g.user,
                           dreams_happy=dreams_happy, dreams_neutral=dreams_neutral, dreams_fear=dreams_fear,
                           dreams_angry=dreams_angry, dreams_sad=dreams_sad, activities_entertainment=activities_entertainment,
                           activities_food=activities_food, activities_other=activities_other)

    # session["route"] = "dream.my_dream"
    # page_all = request.args.get("page_all", 1, type=int)
    # dreams = DreamModel.query.filter_by(author_id=g.user.id).order_by(DreamModel.id.desc()).paginate(page=page_all,
    #                                                                                                  per_page=4)
    #
    # dreams_items = dreams.items
    # dreams2 = DreamModel.query.filter_by(author_id=g.user.id).order_by(DreamModel.id.desc()).all()
    #
    #
    # page_neutral = request.args.get("page_neutral", 1, type=int)
    # dreams_neutral = DreamModel.query.filter_by(author_id=g.user.id, tag="neutral").order_by(
    #     DreamModel.id.desc()).paginate(page=page_neutral, per_page=4)
    #
    # return render_template("my_dream_list.html", dreams=dreams, dreams_items=dreams_items, pagination=dreams,
    #                        user=g.user,
    #                        # dreams_happy=dreams_happy,
    #                        dreams_neutral=dreams_neutral,
    #                        # dreams_fear=dreams_fear,
    #                        # dreams_angry=dreams_angry, dreams_sad=dreams_sad
    #                        )

def show_page(page_num):
    page = request.args.get("page", 1, type=int)

    # 获取第一个分页对象的项目列表和分页信息
    pagination1=DreamModel.query.filter_by(author_id=g.user.id).order_by(DreamModel.id.desc()).paginate(page=page,
                                                                                            per_page=4)
    items1 = pagination1.items


    # 获取第二个分页对象的项目列表和分页信息
    pagination1 = DreamModel.query.filter_by(author_id=g.user.id).order_by(DreamModel.id.desc()).paginate(page=page,
                                                                                                          per_page=4)
    items1 = pagination1.items
    items2, pagination2 = DreamModel.query.filter_by(author_id=g.user.id, tag="neutral").order_by(
        DreamModel.id.desc()).paginate(page=page, per_page=4)

    return render_template('show_page.html', items1=items1, pagination1=pagination1, items2=items2, pagination2=pagination2)


@bp.route("/delete/<int:dream_id>", methods=['GET', 'POST'])
def delete(dream_id):
    dream = DreamModel.query.get_or_404(dream_id)
    db.session.delete(dream)

    db.session.commit()
    flash("Delete successfully", category='success')
    return redirect(url_for("dream.my_dream"))

@bp.route("/search", methods=['GET', 'POST'])
def search():
    words = request.form.get('search')
    print(words)
    page_all = request.args.get("page_all", 1, type=int)
    dreams_search = DreamModel.query.filter(
        DreamModel.author_id == g.user.id,
        or_(
            DreamModel.content.like(f"%{words}%"),
            DreamModel.title.like(f"%{words}%")
        )
    ).order_by(DreamModel.id.desc()).paginate(page=page_all, per_page=4)
    dreams_items = dreams_search.items

    page_happy = request.args.get("page_happy", 1, type=int)
    dreams_happy = DreamModel.query.filter_by(author_id=g.user.id, tag="happy").order_by(DreamModel.id.desc()).paginate(
        page=page_happy, per_page=4)

    page_sad = request.args.get("page_sad", 1, type=int)
    dreams_sad = DreamModel.query.filter_by(author_id=g.user.id, tag="sad").order_by(DreamModel.id.desc()).paginate(
        page=page_sad, per_page=4)

    page_angry = request.args.get("page_angry", 1, type=int)
    dreams_angry = DreamModel.query.filter_by(author_id=g.user.id, tag="angry").order_by(DreamModel.id.desc()).paginate(
        page=page_angry, per_page=4)

    page_fear = request.args.get("page_fear", 1, type=int)
    dreams_fear = DreamModel.query.filter_by(author_id=g.user.id, tag="fear").order_by(DreamModel.id.desc()).paginate(
        page=page_fear, per_page=4)

    page_neutral = request.args.get("page_neutral", 1, type=int)
    dreams_neutral = DreamModel.query.filter_by(author_id=g.user.id, tag="neutral").order_by(
        DreamModel.id.desc()).paginate(page=page_neutral, per_page=4)

    activities_entertainment = ActivityModel.query.filter_by(classsification="Entertainment").order_by(
        ActivityModel.id.desc()).limit(
        3).all()
    activities_food = ActivityModel.query.filter_by(classsification="Food").order_by(
        ActivityModel.id.desc()).limit(3).all()
    activities_other = ActivityModel.query.filter_by(classsification="Other").order_by(
        ActivityModel.id.desc()).limit(3).all()

    return render_template("search_result.html", dreams=dreams_search, dreams_items=dreams_items, pagination=dreams_search,
                           user=g.user,
                           dreams_happy=dreams_happy, dreams_neutral=dreams_neutral, dreams_fear=dreams_fear,
                           dreams_angry=dreams_angry, dreams_sad=dreams_sad, activities_entertainment=activities_entertainment,
                           activities_food=activities_food, activities_other=activities_other)


@bp.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return 'No file is uploaded', 400

    audio_file = request.files['audio']
    title = request.form.get('title')
    whether = request.form.get('weather')
    sleep = request.form.get('sleepDuration')
    if audio_file.filename == '':
        return 'No file is selected', 400

    user_id = g.user.id
    random_number = random.randint(100000, 999999)
    input_file = "static/audio/" + str(user_id) + "+" + str(random_number) + ".webm"
    output_file = "static/audio/" + str(user_id) + "+" + str(random_number) + ".wav"

    # 保存原始文件
    audio_file.save(input_file)

    # 将.webm文件转换为.wav文件
    convert_webm_to_wav(input_file, output_file)

    # 使用ser.py的predict方法获取情绪标签
    predicted_labels = predict(output_file)
    tag = predicted_labels[0]  # 假设我们只关心第1个预测结果
    activity_ids = find_activities_with_tags(predicted_labels)
    activity_ids_str = ','.join(map(str, activity_ids))
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    dream = DreamModel(author_id=user_id, audio=output_file, title=title, whether=whether, sleep=sleep, tag=tag, activity_ids=activity_ids_str, create_time=current_time)
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