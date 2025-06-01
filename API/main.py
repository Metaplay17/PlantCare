import datetime
import json
import random

from models import *
from flask import current_app, render_template
import os
import base64
from constants import *
from utils import *

app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER


@app.route('/', methods=['GET'])
def start_page():
    return render_template('Home.html')


@app.route('/', methods=['POST'])
def core():
    data = request.json
    if data["action"] == "GetPage":
        if data["actionData"]["Page"] == "Plants":
            return render_template('plants.html')

        elif data["actionData"]["Page"] == "AddPlant":
            return render_template('add-plant.html', css_file='add-plant.css')

        elif data["actionData"]["Page"] == "AddNote":
            return render_template('add-note.html', css_file='add-note.css')

        elif data["actionData"]["Page"] == "AddTask":
            return render_template('add-task.html', css_file='add-task.css')

        elif data["actionData"]["Page"] == "Plant":
            return render_template('plant-card.html', css_file='plant-card.css')

        elif data["actionData"]["Page"] == "Photos":
            return render_template('photos.html', css_file='photos.css')

        elif data["actionData"]["Page"] == "Photo":
            return render_template('photo-card.html', css_file='photo-card.css')

        elif data["actionData"]["Page"] == "Notes":
            return render_template('notes.html', css_file='notes.css')

        elif data["actionData"]["Page"] == "Note":
            return render_template('note-card.html', css_file='note-card.css')

        elif data["actionData"]["Page"] == "Tasks":
            return render_template('tasks.html', css_file='tasks.css')

        elif data["actionData"]["Page"] == "Task":
            return render_template('task-card.html', css_file='task-card.css')

        elif data["actionData"]["Page"] == "Calendar":
            return render_template('calendar.html', css_file='calendar.css')

        elif data["actionData"]["Page"] == "FilterNotes":
            return render_template('filter-notes.html', css_file='filter-notes.css')

        elif data["actionData"]["Page"] == "FilterTasks":
            return render_template('filter-tasks.html', css_file='filter-tasks.css')

    elif data["action"] == "Plant":
        if "plant_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return get_plant(data["actionData"]["plant_id"])

    elif data["action"] == "Photo":
        if "photo_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return get_photo(data["actionData"]["photo_id"])

    elif data["action"] == "Note":
        if "note_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return get_note(data["actionData"]["note_id"])

    elif data["action"] == "Task":
        if "task_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return get_task(data["actionData"]["task_id"])

    elif data["action"] == "PlantIdByPhoto":
        if "photo_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return get_plant_id_by_photo(data["actionData"]["photo_id"])

    elif data["action"] == "ChangeMainPhoto":
        if "photo_id" not in data["actionData"].keys() or "plant_id" not in data[
            "actionData"].keys() or "selected" not in data["actionData"]:
            return jsonify({"status": "Bad Request"}), 400
        return change_main_photo(data["actionData"]["plant_id"], data["actionData"]["photo_id"],
                                 data["actionData"]["selected"])

    elif data["action"] == "ChangePlantPhoto":
        if "photo_id" not in data["actionData"].keys() or "plant_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return change_plant_photo(data["actionData"]["plant_id"], data["actionData"]["photo_id"])

    elif data["action"] == "IsMainPhoto":
        if "photo_id" not in data["actionData"].keys() or "plant_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return is_main_photo(data["actionData"]["plant_id"], data["actionData"]["photo_id"])

    elif data["action"] == "GetPlants":
        return get_plants()

    elif data["action"] == "GetFilteredPlants":
        return get_filtered_plants(data["actionData"])

    elif data["action"] == "GetPhotos":
        return get_photos()

    elif data["action"] == "GetFilteredPhotos":
        return get_filtered_photos(data["actionData"])

    elif data["action"] == "GetNotes":
        return get_notes()

    elif data["action"] == "GetTasks":
        return get_tasks()

    elif data["action"] == "GetTaskTypes":
        return get_task_types()

    elif data["action"] == "GetRepeatTypes":
        return get_repeat_types()

    elif data["action"] == "GetDateTasks":
        return get_date_tasks(str(data["actionData"]["date"]))

    elif data["action"] == "GetMonthTasks":
        return get_month_tasks(str(data["actionData"]["date"]))

    elif data["action"] == "AddPlant":
        return add_plant(data["actionData"])

    elif data["action"] == "AddNote":
        return add_note(data["actionData"])

    elif data["action"] == "AddTask":
        return add_task(data["actionData"])

    elif data["action"] == "UpdatePlant":
        return update_plant(data["actionData"])

    elif data["action"] == "UpdateTask":
        if "task_id" not in data["actionData"].keys() or "task_id" not in data[
            "actionData"].keys() or "task_name" not in data["actionData"].keys() or "task_description" not in data[
            "actionData"].keys() or "task_type_id" not in data["actionData"].keys() or "repeat_type_id" not in data[
            "actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return update_task(data["actionData"]["task_id"], data["actionData"]["task_name"],
                           data["actionData"]["task_description"], data["actionData"]["task_date"],
                           data["actionData"]["task_type_id"], data["actionData"]["repeat_type_id"], )

    elif data["action"] == "UpdateNote":
        if "note_id" not in data["actionData"].keys() or "name" not in data["actionData"].keys() or "description" not in \
                data["actionData"].keys() or "plant_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return update_note(data["actionData"]["note_id"], data["actionData"]["name"], data["actionData"]["description"], data["actionData"]["plant_id"])

    elif data["action"] == "AddPhoto":
        return add_photo(data["actionData"])

    elif data["action"] == "AddPhotoWithoutPlant":
        return add_photo_without_plant(data["actionData"])

    elif data["action"] == "DeletePhoto":
        return delete_photo(data["actionData"])

    elif data["action"] == "DeleteNote":
        return delete_note(data["actionData"])

    elif data["action"] == "DeleteTask":
        return delete_task(data["actionData"])


def get_plants():
    plants = Plant.query.all()
    return jsonify([{"plant_id": p.plant_id, "name": p.name, "science_name": p.science_name, "date_added": p.date_added,
                     "place": p.place, "main_photo": get_plant_main_photo(p.plant_id)} for p in plants])


def get_filtered_plants(data):
    name = data["name"]
    plants = Plant.query.filter(Plant.name.ilike(f'%{name}%') | Plant.science_name.ilike(f'%{name}%')).all()
    return jsonify([{"plant_id": p.plant_id, "name": p.name, "science_name": p.science_name, "date_added": p.date_added,
                     "place": p.place, "main_photo": get_plant_main_photo(p.plant_id)} for p in plants])


def get_filtered_photos(data):
    plant_id = data["plant_id"]
    photos = Photo.query.filter_by(plant_id=plant_id).all()
    result = []
    for p in photos:
        directory = os.path.join(current_app.root_path, 'static', 'userphotos')
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
    return jsonify(result), 200


def get_plant(plant_id):
    plant = Plant.query.filter(Plant.plant_id == plant_id).first()
    if not plant:
        return jsonify({"status": "Not Found"}), 404
    return jsonify({
        "plant_id": plant.plant_id,
        "name": plant.name,
        "science_name": plant.science_name,
        "place": plant.place,
        "main_photo": get_plant_main_photo(plant_id)
    })


def get_task(task_id):
    t = Task.query.filter_by(task_id=task_id).first()
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
    })


def get_photos():
    photos = Photo.query.all()
    result = []
    for p in photos:
        directory = os.path.join(current_app.root_path, 'static', 'userphotos')
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

    return jsonify(result)


def get_notes():
    notes = Note.query.all()
    result = []
    for n in notes:
        if n.photo_id:
            response = get_photo(n.photo_id)
            if response[1] != 200:
                photo = None
            else:
                response_dict = get_photo(n.photo_id)[0].get_json()
                photo = response_dict["image"]
        else:
            with open("static/photos/default-note.png", "rb") as image_file:
                # 2. Читаем бинарные данные
                image_data = image_file.read()

                # 3. Кодируем в Base64 и декодируем в строку (utf-8)
                photo = base64.b64encode(image_data).decode("utf-8")
        result.append({
            "note_id": n.note_id,
            "plant_id": n.plant_id,
            "image": photo,
            "note_name": n.note_name,
            "description": n.description,
            "date": n.date_added
        })

    return jsonify(result)


def get_filtered_notes(data):
    date_to = data["date_to"]
    date_from = data["date_from"]
    plant_id = data["plant_id"]
    notes = Note.query.filter_by()
    result = []
    for n in notes:
        if n.photo_id:
            response = get_photo(n.photo_id)
            if response[1] != 200:
                photo = None
            else:
                response_dict = get_photo(n.photo_id)[0].get_json()
                photo = response_dict["image"]
        else:
            with open("static/photos/default-note.png", "rb") as image_file:
                # 2. Читаем бинарные данные
                image_data = image_file.read()

                # 3. Кодируем в Base64 и декодируем в строку (utf-8)
                photo = base64.b64encode(image_data).decode("utf-8")
        result.append({
            "note_id": n.note_id,
            "image": photo,
            "note_name": n.note_name,
            "description": n.description,
            "date": n.date_added
        })

    return jsonify(result)


def get_tasks():
    tasks = Task.query.all()
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


def get_date_tasks(date):
    day = datetime.datetime.strptime(date, "%Y-%m-%d").date().day
    month = datetime.datetime.strptime(date, "%Y-%m-%d").date().month
    year = datetime.datetime.strptime(date, "%Y-%m-%d").date().year
    entries = Calendar.query.filter(
        (extract('month', Calendar.entry_date) == month) &
        (extract('year', Calendar.entry_date) == year) &
        (extract('day', Calendar.entry_date) == day)
    ).all()
    tasks = []
    for entry in entries:
        task = get_task(entry.task_id).get_json()
        calendar_task = {"task_id": task["task_id"],
                         "task_type": get_task_type_desc_by_type_id(task["task_type_id"]),
                         "task_name": task["task_name"]}
        tasks.append(calendar_task)
    return jsonify({"tasks": tasks}), 200


def get_month_tasks(date):
    parsed_date = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
    month = parsed_date.month
    year = parsed_date.year

    entries = Calendar.query.filter(
        (extract('month', Calendar.entry_date) == month) &
        (extract('year', Calendar.entry_date) == year)
    ).all()

    tasks = []
    for entry in entries:
        task = get_task(entry.task_id).get_json()

        calendar_task = {
            "task_type": get_task_type_desc_by_type_id(task["task_type_id"]),
            "task_name": task["task_name"],
            "task_day": entry.entry_date.day
        }
        tasks.append(calendar_task)

    return jsonify({"tasks": tasks}), 200


def get_photo(photo_id):
    photo = Photo.query.filter(Photo.photo_id == photo_id).first()
    if not photo:
        return jsonify({"status": "Not Found"}), 404
    directory = os.path.join(current_app.root_path, 'static', 'userphotos')
    with open(directory + "\\" + photo.filename, "rb") as image_file:
        # 2. Читаем бинарные данные
        image_data = image_file.read()

        # 3. Кодируем в Base64 и декодируем в строку (utf-8)
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        return jsonify({
            "photo_id": photo.photo_id,
            "image": image_base64
        }), 200


def get_note(note_id):
    n = Note.query.filter_by(note_id=note_id).first()
    if not n:
        return jsonify({"status": "Note not found"}), 404

    if n.photo_id:
        response = get_photo(n.photo_id)
        if response[1] != 200:
            photo = None
        else:
            response_dict = get_photo(n.photo_id)[0].get_json()
            photo = response_dict["image"]
    else:
        with open("static/photos/default-note.png", "rb") as image_file:
            # 2. Читаем бинарные данные
            image_data = image_file.read()

            # 3. Кодируем в Base64 и декодируем в строку (utf-8)
            photo = base64.b64encode(image_data).decode("utf-8")
    return jsonify({
        "note_id": n.note_id,
        "plant_id": n.plant_id,
        "image": photo,
        "name": n.note_name,
        "description": n.description,
        "date_added": n.date_added
    })


def add_plant(data):
    if "name" not in data.keys() or "science_name" not in data.keys() or "place" not in data.keys():
        return jsonify({"error": "Some attributes doesnt exist"}), 400

    if Plant.query.filter(Plant.name == data["name"] or Plant.place == data["place"]).first():
        return jsonify({"status": "conflict"}), 409

    new_plant = Plant(name=data["name"], science_name=data["science_name"], place=data["place"])
    db.session.add(new_plant)
    db.session.commit()

    if data["main_photo"]:
        data["plant_id"] = new_plant.plant_id
        add_main_photo(data)

    return jsonify({"status": "success"}), 200


def add_note(data):
    if "name" not in data.keys() or "description" not in data.keys() or "plant_id" not in data.keys() or "date" not in data.keys() or "image" not in data.keys():
        return jsonify({"error": "Some attributes doesnt exist"}), 400

    if Note.query.filter(Note.note_name == data["name"]).first():
        return jsonify({"status": "conflict"}), 409

    photo_id = None

    if data["date"]:
        note_date = data["date"]
    else:
        note_date = datetime.datetime.today()

    if data["image"]:
        image = data["image"]

        filename = str(Plant.query.filter_by(plant_id=data["plant_id"]).first().name) + str(random.randrange(1, 10000)) + ".jpg"  # Добавить username
        file_data = base64.b64decode(image)
        with open(app.config["UPLOAD_FOLDER"] + filename, "wb") as f:
            f.write(file_data)
        new_photo = Photo(plant_id=data["plant_id"], filename=filename)
        db.session.add(new_photo)
        db.session.commit()
        print("photo_id", new_photo.photo_id)
        photo_id = new_photo.photo_id

    new_note = Note(note_name=data["name"], description=data["description"], date_added=note_date, photo_id=photo_id, plant_id=data["plant_id"])
    db.session.add(new_note)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def add_task(data):
    if "name" not in data.keys() or "description" not in data.keys() or "plant_id" not in data.keys() or "task_type_id" not in data.keys() or "frequency_id" not in data.keys():
        return jsonify({"status": "Bad Request"}), 400

    t = Task.query.filter_by(task_name=data["name"]).first()
    if t:
        return jsonify({"status": "Conflict"}), 409

    if data["date"]:
        task_date = data["date"]
    else:
        task_date = datetime.datetime.today()

    task = Task(task_name=data["name"], task_description=data["description"], plant_id=data["plant_id"], task_type_id=data["task_type_id"], repeat_type_id=data["frequency_id"], task_date=task_date)
    db.session.add(task)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def update_plant(data):
    if "plant_id" not in data.keys() or "plant_name" not in data.keys() or "plant_science_name" not in data.keys() or "plant_place" not in data.keys():
        return jsonify({"error": "Some attributes don't exist"}), 400

    if Plant.query.filter(
            (Plant.plant_id != data["plant_id"]) &
            ((Plant.name == data["plant_name"]) | (Plant.place == data["plant_place"]))
    ).first():
        return jsonify({"error": "Some attributes conflict"}), 409

    plant = Plant.query.filter(Plant.plant_id == data["plant_id"]).first()
    plant.name = data["plant_name"]
    plant.science_name = data["plant_science_name"]
    plant.place = data["plant_place"]

    db.session.commit()
    return jsonify({"result": "Success"}), 200


def update_note(note_id, name, description, plant_id):
    note = Note.query.filter_by(note_id=note_id).first()
    if not note:
        return jsonify({"status": "Note not found"}), 404

    note.note_name = name
    note.description = description
    note.plant_id = plant_id

    db.session.commit()
    return jsonify({"status": "success"}), 200


def update_task(task_id, task_name, task_description, task_date, task_type_id, repeat_type_id):
    task = Task.query.filter_by(task_id=task_id).first()
    if not task:
        return jsonify({"status": "Task Not Found"}), 404
    task.task_name = task_name
    task.task_description = task_description
    task.task_date = task_date
    task.task_type_id = task_type_id
    task.repeat_type_id = repeat_type_id
    db.session.commit()
    update_task_calendar(task)
    return jsonify({"status": "success"}), 200


def add_photo(data):
    if "plant_id" not in data.keys():
        return jsonify({"error": "Some attributes doesn't exist"}), 400
    if 'image' not in data.keys():
        return jsonify({"error": "No file part"}), 400

    image = data["image"]

    if not is_allowed_image(image.filename):
        return jsonify({"error": "File type not allowed"}), 400

    filename = str(Plant.query.get(data["plant_id"]).name) + str(random.randrange(1, 10000))  # Добавить username
    new_photo = Photo(plant_id=data["plant_id"], filename=filename)

    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    db.session.add(new_photo)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def add_photo_without_plant(data):
    if 'image' not in data.keys():
        return jsonify({"error": "No file part"}), 400

    image = data["image"]

    filename = "username" + str(random.randrange(1, 10000)) + ".jpg"  # Добавить username
    new_photo = Photo(plant_id=None, filename=filename)
    header, encoded = image.split(",", 1)
    file_data = base64.b64decode(encoded)
    with open(app.config["UPLOAD_FOLDER"] + filename, "wb") as f:
        f.write(file_data)

    db.session.add(new_photo)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def add_main_photo(data):
    if "plant_id" not in data.keys():
        return jsonify({"error": "Some attributes doesn't exist"}), 400
    if 'main_photo' not in data.keys():
        return jsonify({"error": "No file part"}), 400

    plant = db.session.get(Plant, data["plant_id"])
    filename = "null_" + str(random.randrange(1, 10000))
    if plant:
        filename = str(plant.name) + str(random.randrange(1, 10000)) + ".jpg"
    file_data = base64.b64decode(data["main_photo"])
    with open(app.config["UPLOAD_FOLDER"] + filename, "wb") as f:
        f.write(file_data)

    new_photo = Photo(plant_id=data["plant_id"], filename=filename)
    db.session.add(new_photo)
    db.session.commit()

    main_photo = MainPhoto(plant_id=data["plant_id"], photo_id=new_photo.photo_id)
    db.session.add(main_photo)
    db.session.commit()

    return jsonify({"status": "success"}), 200


def change_main_photo(plant_id, photo_id, selected):
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


def change_plant_photo(plant_id, photo_id):
    photo = Photo.query.filter(Photo.photo_id == photo_id).first()
    if photo:
        photo.plant_id = plant_id
        db.session.commit()
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "Photo not found"}), 404


def is_main_photo(plant_id, photo_id):
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


def delete_photo(data):
    if "photo_id" not in data.keys():
        return jsonify({"status": "Bad Request"}), 404

    note = Note.query.filter_by(photo_id=data["photo_id"]).first()
    if note:
        note.photo_id = None

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


def delete_note(data):
    if "note_id" not in data.keys():
        return jsonify({"status": "Bad Request"}), 400

    note = Note.query.filter_by(note_id=data["note_id"]).first()
    photo = Photo.query.filter_by(photo_id=note.photo_id).first()
    if photo:
        delete_photo({"photo_id": photo.photo_id})

    db.session.delete(note)
    db.session.commit()
    return jsonify({"status": "success"}), 200


def delete_task(data):
    if "task_id" not in data.keys():
        return jsonify({"status": "Bad Request"}), 400

    task = Task.query.filter_by(task_id=data["task_id"]).first()
    Calendar.query.filter_by(task_id=task.task_id).delete()

    db.session.delete(task)
    db.session.commit()
    return jsonify({"status": "success"}), 200


app.run()
