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

        elif data["actionData"]["Page"] == "Plant":
            return render_template('plant-card.html', css_file='plant-card.css')

        elif data["actionData"]["Page"] == "Photos":
            return render_template('photos.html', css_file='photos.css')

        elif data["actionData"]["Page"] == "Photo":
            return render_template('photo-card.html', css_file='photo-card.css')

    elif data["action"] == "Plant":
        if "plant_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return get_plant(data["actionData"]["plant_id"])

    elif data["action"] == "Photo":
        if "photo_id" not in data["actionData"].keys():
            return jsonify({"status": "Bad Request"}), 400
        return get_photo(data["actionData"]["photo_id"])

    elif data["action"] == "GetPlants":
        return get_plants()

    elif data["action"] == "GetPhotos":
        return get_photos()

    elif data["action"] == "AddPlant":
        return add_plant(data["actionData"])

    elif data["action"] == "UpdatePlant":
        return update_plant(data["actionData"])

    elif data["action"] == "AddPhoto":
        return add_photo(data["actionData"])

    elif data["action"] == "AddNote":
        return add_note(data["actionData"])

    elif data["action"] == "AddTask":
        return add_task(data["actionData"])


def get_plants():
    plants = Plant.query.all()
    return jsonify([{"plant_id": p.plant_id, "name": p.name, "science_name": p.science_name, "date_added": p.date_added,
                     "place": p.place, "main_photo": get_plant_main_photo(p.plant_id)} for p in plants])


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


def add_photo(data):
    if "plant_id" not in data.keys():
        return jsonify({"error": "Some attributes doesn't exist"}), 400
    if 'image' not in data.keys():
        return jsonify({"error": "No file part"}), 400

    image = data["image"]

    if not is_allowed_image(image.filename):
        return jsonify({"error": "File type not allowed"}), 400

    filename = str(Plant.query.get(data["plant_id"]).name) + str(random.randrange(1,10000))  # Добавить username
    new_photo = Photo(plant_id=data["plant_id"], filename=filename)

    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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


def add_note(data):
    if "plant_id" not in data.keys() or "note_type_id" not in data.keys() or "note" not in data.keys() \
            or "photo_id" not in data.keys():
        return jsonify({"error": "Some attributes doesn't exist"}), 400

    new_note = Note(plant_id=data["plant_id"], note_type_id=data["note_type_id"], note=data["note"],
                    photo_id=data["photo_id"])
    db.session.add(new_note)
    db.session.commit()


def add_task(data):
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
