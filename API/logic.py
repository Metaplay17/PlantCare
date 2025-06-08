from extensions import app, db
from models import Note, Task, Photo, MainPhoto, TaskType, Plant, RepeatType, Calendar
from utils import (get_plant_main_photo, get_repeat_type_desc_by_type_id, get_task_type_desc_by_type_id,
                update_task_calendar, get_login_by_user_id)
from constants import IMAGE_FOLDER

from datetime import datetime
import uuid
from sqlalchemy import extract
import os
import base64
from flask import jsonify, abort, current_app


def get_plants(user_id):
    plants = Plant.query.filter_by(user_id=user_id).all()
    return jsonify([{"plant_id": p.plant_id, "name": p.name, "science_name": p.science_name, "date_added": p.date_added,
                     "place": p.place, "main_photo": get_plant_main_photo(p.plant_id)} for p in plants]), 200


def get_plant(plant_id, user_id):
    plant = Plant.query.filter((Plant.plant_id == plant_id) & (Plant.user_id == user_id)).first()
    if not plant:
        return jsonify({"status": "Plant Not Found"}), 404
    return jsonify({
        "plant_id": plant.plant_id,
        "name": plant.name,
        "science_name": plant.science_name,
        "place": plant.place,
        "main_photo": get_plant_main_photo(plant_id)
    }), 200


def get_task(task_id, user_id):
    t = Task.query.join(Plant, Task.plant_id == Plant.plant_id).filter((Task.task_id == task_id) & (Plant.user_id == user_id)).first()
    if not t:
        return jsonify({"status": "Task Not Found"}), 404
    return jsonify({
        "task_id": t.task_id,
        "plant_id": t.plant_id,
        "task_name": t.task_name,
        "task_description": t.task_description,
        "task_type_id": t.task_type_id,
        "task_date": t.task_date,
        "repeat_type_id": t.repeat_type_id
    }), 200


def get_photos(user_id):
    photos = Photo.query.join(Plant, Plant.plant_id == Photo.plant_id).filter(Plant.user_id == user_id).all()
    result = []
    for p in photos:
        directory = os.path.join(current_app.root_path, 'static', 'userphotos')
        try:
            with open(directory + "\\" + p.filename, "rb") as image_file:
                # 2. Читаем бинарные данные
                image_data = image_file.read()

                # 3. Кодируем в Base64 и декодируем в строку (utf-8)
                image_base64 = base64.b64encode(image_data).decode("utf-8")

                result.append({
                    "photo_id": p.photo_id,
                    "plant_id": p.plant_id,
                    "image": image_base64
                })
        except FileNotFoundError:
            app.logger.error(f"Photo file not found: {p.filename}")
            abort(500)
        except MemoryError:
            app.logger.error(f"Photo file is too large: {p.filename}")
            abort(500)
        except UnicodeDecodeError:
            app.logger.error(f"Photo file decoding error: {p.filename}")
            abort(500)

    return jsonify(result), 200


def get_notes(user_id):
    notes = Note.query.join(Plant, Note.plant_id == Plant.plant_id).filter(Plant.user_id == user_id).all()
    result = []
    for n in notes:
        if n.photo_id:
            response = get_photo(n.photo_id, user_id)
            if response[1] != 200:
                photo = None
            else:
                response_dict = get_photo(n.photo_id, user_id)[0].get_json()
                photo = response_dict["image"]
        else:
            try:
                with open("static/photos/default-note.png", "rb") as image_file:
                    # 2. Читаем бинарные данные
                    image_data = image_file.read()

                    # 3. Кодируем в Base64 и декодируем в строку (utf-8)
                    photo = base64.b64encode(image_data).decode("utf-8")
            except FileNotFoundError:
                app.logger.error("Default note photo file not found")
                abort(500)
            except MemoryError:
                app.logger.error("Default note photo file is too large")
                abort(500)
            except UnicodeDecodeError:
                app.logger.error("Default note photo decoding error")
                abort(500)
        result.append({
            "note_id": n.note_id,
            "plant_id": n.plant_id,
            "image": photo,
            "note_name": n.note_name,
            "description": n.description,
            "date": n.date_added
        })

    return jsonify(result), 200


def get_tasks(user_id):
    tasks = Task.query.join(Plant, Task.plant_id == Plant.plant_id).filter(Plant.user_id == user_id).all()
    result = []
    for t in tasks:
        result.append({
            "task_id": t.task_id,
            "plant_id": t.plant_id,
            "task_name": t.task_name,
            "task_description": t.task_description,
            "task_type": get_task_type_desc_by_type_id(t.task_type_id),
            "task_date": t.task_date,
            "repeating": get_repeat_type_desc_by_type_id(t.repeat_type_id)
        })
    return jsonify(result), 200


def get_date_tasks(date, user_id):
    day = datetime.strptime(date, "%Y-%m-%d").date().day
    month = datetime.strptime(date, "%Y-%m-%d").date().month
    year = datetime.strptime(date, "%Y-%m-%d").date().year
    entries = Calendar.query.join(Task, Task.task_id == Calendar.task_id).join(Plant, Task.plant_id == Plant.plant_id).filter(
        (extract('month', Calendar.entry_date) == month) &
        (extract('year', Calendar.entry_date) == year) &
        (extract('day', Calendar.entry_date) == day) &
        (Plant.user_id == user_id)
    ).all()
    tasks = []
    for entry in entries:
        task = get_task(entry.task_id, user_id)[0].get_json()
        calendar_task = {"task_id": task["task_id"],
                         "task_type": get_task_type_desc_by_type_id(task["task_type_id"]),
                         "task_name": task["task_name"]}
        tasks.append(calendar_task)
    return jsonify({"tasks": tasks}), 200


def get_month_tasks(date, user_id):
    try:
        if not date:
            app.logger.warning("Empty date month tasks")
            abort(400)
        parsed_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
        month = parsed_date.month
        year = parsed_date.year
    except ValueError:
        app.logger.warning("Incorrect date format")
        abort(400)

    entries = Calendar.query.join(Task, Task.task_id == Calendar.task_id).join(Plant, Plant.plant_id == Task.plant_id).filter(
        (extract('month', Calendar.entry_date) == month) &
        (extract('year', Calendar.entry_date) == year) &
        (Plant.user_id == user_id)
    ).all()

    tasks = []
    for entry in entries:
        task = get_task(entry.task_id, user_id)[0].get_json()

        calendar_task = {
            "task_type": get_task_type_desc_by_type_id(task["task_type_id"]),
            "task_name": task["task_name"],
            "task_day": entry.entry_date.day
        }
        tasks.append(calendar_task)

    return jsonify({"tasks": tasks}), 200


def get_photo(photo_id, user_id):
    photo = Photo.query.join(Plant, Plant.plant_id == Photo.plant_id).filter((Photo.photo_id == photo_id) & (Plant.user_id == user_id)).first()
    if not photo:
        abort(404)
    directory = os.path.join(current_app.root_path, 'static', 'userphotos')
    try:
        with open(directory + "\\" + photo.filename, "rb") as image_file:
            # 2. Читаем бинарные данные
            image_data = image_file.read()

            # 3. Кодируем в Base64 и декодируем в строку (utf-8)
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            return jsonify({
                "photo_id": photo.photo_id,
                "image": image_base64
            }), 200
    except FileNotFoundError:
        app.logger.error(f"Photo file not found: {photo.filename}")
        abort(500)
    except MemoryError:
        app.logger.error(f"Photo file is too large: {photo.filename}")
        abort(500)
    except UnicodeDecodeError:
        app.logger.error(f"Photo file decoding error: {photo.filename}")
        abort(500)


def get_note(note_id, user_id):
    n = Note.query.filter_by(note_id=note_id).first()
    if not n:
        return jsonify({"status": "Note not found"}), 404

    if n.photo_id:
        response = get_photo(n.photo_id, user_id)
        if response[1] != 200:
            photo = None
        else:
            response_dict = get_photo(n.photo_id, user_id)[0].get_json()
            photo = response_dict["image"]
    else:
        try:
            with open("static/photos/default-note.png", "rb") as image_file:
                # 2. Читаем бинарные данные
                image_data = image_file.read()

                # 3. Кодируем в Base64 и декодируем в строку (utf-8)
                photo = base64.b64encode(image_data).decode("utf-8")
        except FileNotFoundError:
            app.logger.error(f"Photo file not found: Note id: {n.note_id}")
            abort(500)
        except MemoryError:
            app.logger.error(f"Photo file is too large: Note id: {n.note_id}")
            abort(500)
        except UnicodeDecodeError:
            app.logger.error(f"Photo file decoding error: Note id: {n.note_id}")
            abort(500)

    return jsonify({
        "note_id": n.note_id,
        "plant_id": n.plant_id,
        "image": photo,
        "name": n.note_name,
        "description": n.description,
        "date_added": n.date_added
        }), 200


def add_plant(data, user_id):
    if "name" not in data.keys() or "science_name" not in data.keys() or "place" not in data.keys():
        abort(400)

    if Plant.query.filter(((Plant.name == data["name"]) | (Plant.place == data["place"])) & (Plant.user_id == user_id)).first():
        return jsonify({"status": "Имя или место уже используется"}), 409

    new_plant = Plant(name=data["name"], science_name=data["science_name"], place=data["place"], user_id=user_id)
    db.session.add(new_plant)
    db.session.commit()

    if data["main_photo"]:
        data["plant_id"] = new_plant.plant_id
        add_main_photo(data, user_id)

    return jsonify({"status": "success"}), 200


def add_note(data, user_id):
    if not Plant.query.filter((Plant.user_id == user_id) & (Plant.plant_id == data["plant_id"])).first():
        return jsonify({"Растение не найдено"}), 404

    if "name" not in data.keys() or "description" not in data.keys() or "plant_id" not in data.keys() or "date" not in data.keys() or "image" not in data.keys():
        abort(400)

    if Note.query.join(Plant, Plant.plant_id == Note.plant_id).filter((Note.note_name == data["name"]) & (Plant.user_id == user_id)).first():
        return jsonify({"status": "Название заметки уже используется"}), 409

    photo_id = None

    if data["date"]:
        note_date = data["date"]
    else:
        note_date = datetime.today()

    if data["image"]:
        image = data["image"]

        filename = get_login_by_user_id(user_id) + "_" + str(Plant.query.filter_by(plant_id=data["plant_id"]).first().name) + "_" + str(uuid.uuid4()) + ".jpg"
        try:
            file_data = base64.b64decode(image)
        except ValueError as e:
            app.logger.error(f"Decoding photo file error, filename: {filename}, error: {e}")
            abort(500)

        try:
            with open(app.config["UPLOAD_FOLDER"] + filename, "wb") as f:
                f.write(file_data)
        except FileNotFoundError:
            app.logger.error(f"Photo file not found")
            abort(500)
        except MemoryError:
            app.logger.error(f"Photo file is too large")
            abort(500)
        except UnicodeDecodeError:
            app.logger.error(f"Photo file decoding error")
            abort(500)

        new_photo = Photo(plant_id=data["plant_id"], filename=filename)
        db.session.add(new_photo)
        db.session.commit()
        photo_id = new_photo.photo_id

    new_note = Note(note_name=data["name"], description=data["description"], date_added=note_date, photo_id=photo_id,
                    plant_id=data["plant_id"])
    db.session.add(new_note)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def add_task(data, user_id):
    if not Plant.query.filter((Plant.user_id == user_id) & (Plant.plant_id == data["plant_id"])).first():
        return jsonify({"Растение не найдено"}), 404

    if "name" not in data.keys() or "description" not in data.keys() or "plant_id" not in data.keys() or "task_type_id" not in data.keys() or "frequency_id" not in data.keys():
        abort(400)

    t = Task.query.filter_by(task_name=data["name"]).first()
    if t:
        return jsonify({"status": "Название задачи уже используется"}), 409

    if data["date"]:
        task_date = data["date"]
    else:
        task_date = datetime.today()

    task = Task(task_name=data["name"], task_description=data["description"], plant_id=data["plant_id"],
                task_type_id=data["task_type_id"], repeat_type_id=data["frequency_id"], task_date=task_date)
    db.session.add(task)
    db.session.commit()

    update_task_calendar(task)

    return jsonify({"status": "success"}), 200


def update_plant(data, user_id):
    if not Plant.query.filter((Plant.user_id == user_id) & (Plant.plant_id == data["plant_id"])).first():
        return jsonify({"Растение не найдено"}), 404

    if "plant_id" not in data.keys() or "plant_name" not in data.keys() or "plant_science_name" not in data.keys() or "plant_place" not in data.keys():
        abort(400)

    if Plant.query.filter(
            (Plant.plant_id != data["plant_id"]) &
            ((Plant.name == data["plant_name"]) | (Plant.place == data["plant_place"]))
    ).first():
        return jsonify({"Имя или место уже испольуется"}), 409

    plant = Plant.query.filter(Plant.plant_id == data["plant_id"]).first()
    plant.name = data["plant_name"]
    plant.science_name = data["plant_science_name"]
    plant.place = data["plant_place"]

    db.session.commit()
    return jsonify({"result": "Success"}), 200


def update_note(note_id, name, description, plant_id, user_id):
    note = Note.query.join(Plant, Plant.plant_id == Note.plant_id).filter((Note.note_id == note_id) & (Plant.user_id == user_id)).first()
    if not note:
        return jsonify({"Заметка не найдена"}), 404

    note.note_name = name
    note.description = description
    note.plant_id = plant_id

    db.session.commit()
    return jsonify({"status": "success"}), 200


def update_task(task_id, task_name, task_description, task_date, task_type_id, repeat_type_id, user_id):
    task = Task.query.join(Plant, Plant.plant_id == Task.plant_id).filter((Task.task_id == task_id) & (Plant.user_id == user_id)).first()
    if not task:
        return jsonify({"Задача не найдена"}), 404
    task.task_name = task_name
    task.task_description = task_description
    task.task_date = task_date
    task.task_type_id = task_type_id
    task.repeat_type_id = repeat_type_id

    db.session.commit()
    update_task_calendar(task)
    return jsonify({"status": "success"}), 200


def add_photo(data, user_id):
    if not Plant.query.filter((Plant.user_id == user_id) & (Plant.plant_id == data["plant_id"])).first():
        return jsonify({"Растение не найдено"}), 404

    if "plant_id" not in data.keys() or 'image':
        abort(400)

    image = data["image"]

    # Добавить проверку на тип

    filename = get_login_by_user_id(user_id) + "_" + Plant.query.filter_by(plant_id=data["plant_id"]).first().name + "_" + str(uuid.uuid4()) + ".jpg"
    new_photo = Photo(plant_id=data["plant_id"], filename=filename)

    file_data = base64.b64decode(image)
    try:
        with open(app.config["UPLOAD_FOLDER"] + filename, "wb") as f:
            f.write(file_data)
    except FileNotFoundError:
        app.logger.error(f"Photo file not found, filename: {filename}")
        abort(500)
    except MemoryError:
        app.logger.error(f"Photo file is too large, filename: {filename}")
        abort(500)
    except UnicodeDecodeError:
        app.logger.error(f"Photo file decoding error, filename: {filename}")
        abort(500)

    db.session.add(new_photo)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def add_main_photo(data, user_id):
    if not Plant.query.filter((Plant.user_id == user_id) & (Plant.plant_id == data["plant_id"])).first():
        return jsonify({"Растение не найдено"}), 404

    if "plant_id" not in data.keys() or 'main_photo' not in data.keys():
        abort(400)

    plant = db.session.get(Plant, data["plant_id"])
    if plant:
        filename = get_login_by_user_id(user_id) + "_" + str(plant.name) + "_" + str(uuid.uuid4()) + ".jpg"
    else:
        app.logger.error(f"Plant not found (adding main photo): Plant id: {data['plant_id']}")
        return jsonify({"Растение не найдено"}), 404
    file_data = base64.b64decode(data["main_photo"])
    try:
        with open(app.config["UPLOAD_FOLDER"] + filename, "wb") as f:
            f.write(file_data)
    except FileNotFoundError:
        app.logger.error(f"Photo file not found, filename: {filename}")
        abort(500)
    except MemoryError:
        app.logger.error(f"Photo file is too large, filename: {filename}")
        abort(500)
    except UnicodeDecodeError:
        app.logger.error(f"Photo file decoding error, filename: {filename}")
        abort(500)

    new_photo = Photo(plant_id=data["plant_id"], filename=filename)
    db.session.add(new_photo)
    db.session.commit()

    main_photo = MainPhoto(plant_id=data["plant_id"], photo_id=new_photo.photo_id)
    db.session.add(main_photo)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def change_main_photo(plant_id, photo_id, selected, user_id):
    if not Plant.query.filter((Plant.user_id == user_id) & (Plant.plant_id == plant_id)).first():
        return jsonify({"Растение не найдено"}), 404

    if not Plant.query.join(Photo, Photo.plant_id == Plant.plant_id).filter((Plant.user_id == user_id) & (Photo.photo_id == photo_id)).first():
        return jsonify({"Фото не найдено"}), 404

    # Находим существующую запись
    main_photo = MainPhoto.query.filter_by(photo_id=photo_id).first()

    if main_photo:
        if not selected:
            # Если запись существует и чекбокс не выбран, удаляем запись
            db.session.delete(main_photo)
            db.session.commit()
            return jsonify({"status": "Main photo deleted"}), 200
        else:
            # Если запись существует и чекбокс выбран, обновляем plant_id
            main_photo.plant_id = plant_id
            db.session.commit()
            return jsonify({"status": "Main photo updated"}), 200

    elif selected:
        # Если запись не существует и чекбокс выбран, создаем новую запись
        new_main_photo = MainPhoto(photo_id=photo_id, plant_id=plant_id)
        db.session.add(new_main_photo)
        db.session.commit()
        return jsonify({"status": "Main photo created"}), 200

    else:
        # Если запись не существует и чекбокс не выбран, ничего не делаем
        return jsonify({"status": "No changes made"}), 200


def change_plant_photo(plant_id, photo_id, user_id):
    photo = Photo.query.join(Plant, Plant.plant_id == Photo.plant_id).filter(Photo.photo_id == photo_id, Plant.user_id == user_id).first()
    if photo:
        photo.plant_id = plant_id
        db.session.commit()
        return jsonify({"status": "success"}), 200

    abort(404)


def is_main_photo(plant_id, photo_id, user_id):
    if not Plant.query.filter((Plant.user_id == user_id) & (Plant.plant_id == plant_id)).first():
        abort(404)

    if not Plant.query.join(Photo, Photo.plant_id == Plant.plant_id).filter(
            (Plant.user_id == user_id) & (Photo.photo_id == photo_id)).first():
        abort(404)

    main_photo = MainPhoto.query.filter(MainPhoto.photo_id == photo_id, MainPhoto.plant_id == plant_id).first()
    if main_photo:
        return jsonify({"status": "success", "isMainPhoto": True})
    else:
        return jsonify({"status": "success", "isMainPhoto": False})


def get_task_types():
    task_types = TaskType.query.all()
    result = []
    for t in task_types:
        result.append({
            "task_type_id": t.task_type_id,
            "task_type_description": t.description
        })
    return jsonify(result), 200


def get_repeat_types():
    repeat_types = RepeatType.query.all()
    result = []
    for t in repeat_types:
        result.append({
            "repeat_type_id": t.repeat_type_id,
            "repeat_type_description": t.description
        })
    return jsonify(result), 200


def delete_photo(data, user_id):
    if "photo_id" not in data.keys():
        abort(400)

    if not Plant.query.join(Photo, Photo.plant_id == Plant.plant_id).filter(
            (Plant.user_id == user_id) & (Photo.photo_id == data["photo_id"])).first():
        return jsonify({"Фото не найдено"}), 404

    note = Note.query.filter_by(photo_id=data["photo_id"]).first()
    if note:
        note.photo_id = None
        db.session.commit()

    main_photo = MainPhoto.query.filter_by(photo_id=data["photo_id"]).first()
    if main_photo:
        db.session.delete(main_photo)

    photo = Photo.query.filter_by(photo_id=data["photo_id"]).first()
    if photo:
        path = photo.filename
        os.remove(IMAGE_FOLDER + path)
        db.session.delete(photo)

    db.session.commit()
    return jsonify({"status": "success"}), 200


def delete_note(data, user_id):
    if "note_id" not in data.keys():
        abort(400)

    if not Plant.query.join(Note, Note.plant_id == Plant.plant_id).filter(
            (Plant.user_id == user_id) & (Note.plant_id == Plant.plant_id)).first():
        return jsonify({"Заметка не найдена"}), 404

    note = Note.query.filter_by(note_id=data["note_id"]).first()
    photo = Photo.query.filter_by(photo_id=note.photo_id).first()
    if photo:
        delete_photo({"photo_id": photo.photo_id}, user_id)

    db.session.delete(note)
    db.session.commit()
    return jsonify({"status": "success"}), 200


def delete_task(data, user_id):
    if "task_id" not in data.keys():
        abort(400)

    task = Task.query.join(Plant, Plant.plant_id == Task.task_id).filter((Task.task_id == data["task_id"]) & (Plant.user_id == user_id)).first()
    if not task:
        return jsonify({"Задача не найдена"}), 404

    Calendar.query.filter_by(task_id=task.task_id).delete()

    db.session.delete(task)
    db.session.commit()
    return jsonify({"status": "success"}), 200


def delete_plant(data, user_id):
    if "plant_id" not in data.keys():
        abort(400)

    plant = Plant.query.filter_by(plant_id=data["plant_id"], user_id=user_id).first()
    if not plant:
        return jsonify({"Растение не найдено"}), 404

    photos = Photo.query.filter_by(plant_id=plant.plant_id).all()
    notes = Note.query.filter_by(plant_id=plant.plant_id).all()
    tasks = Task.query.filter_by(plant_id=plant.plant_id).all()

    for p in photos:
        delete_photo({"photo_id": p.photo_id}, user_id)
    for n in notes:
        delete_note({"note_id": n.note_id}, user_id)
    for t in tasks:
        delete_task({"task_id": t.task_id}, user_id)

    db.session.delete(plant)
    db.session.commit()
    return jsonify({"status": "success"}), 200
