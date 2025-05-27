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

