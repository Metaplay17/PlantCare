from extensions import app
import datetime
from flask import jsonify, abort

from constants import *
from models import User, Photo, MainPhoto, TaskType, Plant, RepeatType, Calendar, db
import base64
from flask import current_app

import logging
from logging.handlers import RotatingFileHandler

import subprocess
from datetime import datetime
import os


def logical_backup():
    output_dir = os.getenv("DB_BACKUPS_DIR")
    if not output_dir:
        app.logger.critical("db backups path not found")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(output_dir, f"{db_name}_backup_{timestamp}.sql")

    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("PG_PASSWORD")

    if not db_name or not db_user or not env["PGPASSWORD"]:
        app.logger.critical("env variable for db backup not found")
        return

    cmd = [
        "pg_dump",
        "-U", db_user,
        "-h", "localhost",
        "-F", "p",  # plain text SQL
        "-f", backup_file,
        db_name
    ]

    try:
        subprocess.run(cmd, check=True, env=env)
        app.logger.info(f"Logical db backup created: {backup_file}")
    except subprocess.CalledProcessError as e:
        app.logger.critical(f"Logical db create error: {e}")


def physical_backup():
    output_dir = os.getenv("DB_BACKUPS_DIR")
    if not output_dir:
        app.logger.critical("db backups path not found")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    label = "physical_backup"

    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("PG_PASSWORD")

    if not db_name or not db_user or not env["PGPASSWORD"]:
        app.logger.critical("env variable for db backup not found")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(output_dir, f"physical_backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)

    PG_BASEBACKUP_PATH = "pg_basebackup"

    cmd = [
        PG_BASEBACKUP_PATH,
        "-U", db_user,
        "-D", backup_dir,
        "-Ft",  # формат tar
        "--gzip",  # сжатие
        "-l", label,
        "-P",  # progress bar
        "-v",  # verbose output
        "-w",  # не запрашивать пароль
    ]

    try:
        subprocess.run(cmd, check=True, env=env)
        app.logger.info(f"Logical db backup created: {backup_dir}")
    except subprocess.CalledProcessError as e:
        app.logger.critical(f"Logical db create error: {e}")


# Настройка логгера
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


def is_allowed_image(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_plant_main_photo(plant_id):
    photo = MainPhoto.query.filter(MainPhoto.plant_id == plant_id).first()
    if not photo:
        try:
            with open("static/photos/default-plant.png", "rb") as image_file:
                # 2. Читаем бинарные данные
                image_data = image_file.read()

                # 3. Кодируем в Base64 и декодируем в строку (utf-8)
                image_base64 = base64.b64encode(image_data).decode("utf-8")

                return image_base64
        except FileNotFoundError:
            app.logger.error("Default plant photo file not found")
            abort(500)
        except MemoryError:
            app.logger.error("Default plant photo file is too large")
            abort(500)
        except UnicodeDecodeError:
            app.logger.error("Default plant photo decoding error")
            abort(500)

    directory = os.path.join(current_app.root_path, 'static', 'userphotos')
    filename = Photo.query.filter(Photo.photo_id == photo.photo_id).first().filename
    try:
        with open(directory + "\\" + filename, "rb") as image_file:
            # 2. Читаем бинарные данные
            image_data = image_file.read()

            # 3. Кодируем в Base64 и декодируем в строку (utf-8)
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            return image_base64
    except FileNotFoundError:
        app.logger.error(f"Plant photo file not found, filename: {filename}")
        abort(500)
    except MemoryError:
        app.logger.error(f"Plant photo file is too large, filename: {filename}")
        abort(500)
    except UnicodeDecodeError:
        app.logger.error(f"Plant photo decoding error, filename: {filename}")
        abort(500)


def get_task_type_desc_by_type_id(type_id):
    task_type = TaskType.query.filter_by(task_type_id=type_id).first()
    return task_type.description


def get_repeat_type_desc_by_type_id(type_id):
    repeat_type = RepeatType.query.filter_by(repeat_type_id=type_id).first()
    return repeat_type.description


def get_plant_id_by_photo(photo_id, user_id):
    if not Plant.query.join(Photo, Photo.plant_id == Plant.plant_id).filter(
            (Plant.user_id == user_id) & (Photo.photo_id == photo_id)).first():
        return jsonify({"status": "Forbidden"}), 403

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
    start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=365)
    while start <= end:
        tasks.append(Calendar(task_id=task.task_id, entry_date=start))
        start += time_delta

    db.session.add_all(tasks)
    db.session.commit()


def is_login_exist(login):
    user = User.query.filter_by(login=login).first()
    if user:
        return True
    return False


def is_email_exist(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return True
    return False


def get_user_id_by_login(login):
    user = User.query.filter_by(login=login).first()
    if not user:
        abort(404)
    return user.user_id


def get_login_by_user_id(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        abort(404)
    return user.login


def get_username(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        abort(404)
    return jsonify({"username": user.username}), 200


