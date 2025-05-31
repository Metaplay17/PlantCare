import datetime

from constants import *
from models import *
import base64
import os
from flask import current_app


def is_allowed_image(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_plant_main_photo(plant_id):
    photo = MainPhoto.query.filter(MainPhoto.plant_id == plant_id).first()
    if not photo:
        with open("static/photos/default-plant.png", "rb") as image_file:
            # 2. Читаем бинарные данные
            image_data = image_file.read()

            # 3. Кодируем в Base64 и декодируем в строку (utf-8)
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            return image_base64

    directory = os.path.join(current_app.root_path, 'static', 'userphotos')
    filename = Photo.query.filter(Photo.photo_id == photo.photo_id).first().filename
    with open(directory + "\\" + filename, "rb") as image_file:
        # 2. Читаем бинарные данные
        image_data = image_file.read()

        # 3. Кодируем в Base64 и декодируем в строку (utf-8)
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        return image_base64


def get_task_type_desc_by_type_id(type_id):
    task_type = TaskType.query.filter_by(task_type_id=type_id).first()
    return task_type.description


def get_repeat_type_desc_by_type_id(type_id):
    repeat_type = RepeatType.query.filter_by(repeat_type_id=type_id).first()
    return repeat_type.description


def get_plant_id_by_photo(photo_id):
    photo = Photo.query.filter(Photo.photo_id == photo_id).first()
    return jsonify({"plant_id": photo.plant_id})


def update_task_calendar(task):
    # Удаление старых задач
    Calendar.query.filter_by(task_id=task.task_id).delete()

    # Определение типа повторения
    repeat_type = get_repeat_type_desc_by_type_id(task.repeat_type_id)
    if repeat_type == "1 day":
        time_delta = datetime.timedelta(days=1)
    elif repeat_type == "3 days":
        time_delta = datetime.timedelta(days=3)
    elif repeat_type == "1 week":
        time_delta = datetime.timedelta(days=7)
    elif repeat_type == "2 weeks":
        time_delta = datetime.timedelta(days=14)
    elif repeat_type == "1 month":
        time_delta = datetime.timedelta(days=30)
    elif repeat_type == "3 months":
        time_delta = datetime.timedelta(days=90)
    elif repeat_type == "6 months":
        time_delta = datetime.timedelta(days=180)
    elif repeat_type == "1 year":
        time_delta = datetime.timedelta(days=365)
    else:
        raise ValueError(f"Unknown repeat type: {repeat_type}")

    # Генерация новых задач
    tasks = []
    start = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=30)
    while start <= end:
        tasks.append(Calendar(task_id=task.task_id, entry_date=start))
        start += time_delta

    # Добавление задач в базу данных
    try:
        db.session.add_all(tasks)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e



