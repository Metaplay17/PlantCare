from models import *
from flask import current_app
import os
import base64
from constants import *
from utils import *

app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER


@app.route('/plants')
def get_plants():
    plants = Plant.query.all()
    return jsonify([{"plant_id": p.plant_id, "name": p.name, "science_name": p.science_name, "date_added": p.date_added,
                     "place": p.place} for p in plants])


@app.route('/photos')
def get_photos():
    photos = Photo.query.all()
    result = []
    for p in photos:
        directory = os.path.join(current_app.root_path, 'static', 'userphotos')
        with open(directory + p.filename, "rb") as image_file:
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


@app.route('/plants', methods=['POST'])
def add_plant():
    data = request.json
    if "name" not in data.keys() or "science_name" not in data.keys() or "place" not in data.keys():
        return jsonify({"error": "Some attributes doesnt exist"}), 400

    if Plant.query.filter(Plant.name == data["name"]).all() or Plant.query.filter(Plant.place == data["place"]).all():
        return jsonify({"status": "conflict"}), 409

    new_plant = Plant(name=data["name"], science_name=data["science_name"], place=data["place"])
    db.session.add(new_plant)
    db.session.commit()
    return jsonify({"status": "success"}), 201


@app.route('/photos', methods=['POST'])
def add_photo():
    data = request.json()
    if "plant_id" not in data.keys():
        return jsonify({"error": "Some attributes doesn't exist"}), 400
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    image = request.files["image"]

    if not is_allowed_image(image.filename):
        return jsonify({"error": "File type not allowed"}), 400

    new_photo = Photo(plant_id=data["plant_id"], science_name=data["science_name"], place=data["place"])

    filename = str(new_photo.photo_id) + "_" + str(Plant.query.get(data["plant_id"]).name)  # Добавить username
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    db.session.add(new_photo)
    db.session.commit()

    return jsonify({"status": "success"}), 201


@app.route('/notes', methods=['POST'])
def add_note():
    data = request.json()
    if "plant_id" not in data.keys() or "note_type_id" not in data.keys() or "note" not in data.keys() \
            or "photo_id" not in data.keys():
        return jsonify({"error": "Some attributes doesn't exist"}), 400

    new_note = Note(plant_id=data["plant_id"], note_type_id=data["note_type_id"], note=data["note"],
                    photo_id=data["photo_id"])
    db.session.add(new_note)
    db.session.commit()


@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json()
    if "plant_id" not in data.keys() or "task_id" not in data.keys() or "task_type_id" not in data.keys() \
            or "task_detail" not in data.keys() or "repeat_type" not in data.keys():
        return jsonify({"error": "Some attribute doesn't exist"}), 400

    new_task = Task(plant_id=data["plant_id"], task_type_id=data["task_type_id"], repeat_type=data["repeat_type"])
    new_task_detail = TaskDetail(task_id=new_task.task_id, detail=data["task_detail"])
    new_task.details = new_task_detail
    db.session.add(new_task)
    db.session.add(new_task_detail)
    db.session.commit()


app.run()
