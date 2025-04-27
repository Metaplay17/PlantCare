from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask("app")
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qazedcrfvs1A@localhost/plantcare'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # отключаем уведомления


class TaskType(db.Model):
    __tablename__ = "task_types"
    task_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)


class NoteType(db.Model):
    __tablename__ = "note_types"
    note_type_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)


class Plant(db.Model):
    __tablename__ = "plants"
    plant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    science_name = db.Column(db.String(50))
    date_added = db.Column(db.Date, default=date.today())
    place = db.Numeric(precision=2)
    photos = db.relationship('Photo', backref='plant_id', lazy=True)  # Связь 1 ко многим
    tasks = db.relationship('Task', backref='plant_id', lazy=True)
    notes = db.relationship('Note', backref='plant_id', lazy=True)


class Photo(db.Model):
    __tablename__ = "photos"
    photo_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))  # Внешний ключ
    filename = db.Column(db.String(50))


class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    task_type_id = db.Column(db.Integer, db.ForeignKey('task_types.task_type_id'))
    details = db.relationship('TaskDetail', backref='task_id', lazy=True)


class TaskDetail(db.Model):
    __tablename__ = "task_details"
    task_detail_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    detail = db.Column(db.Text)


class Note(db.Model):
    __tablename__ = "notes"
    note_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    note_type_id = db.Column(db.Integer, db.ForeignKey('note_types.note_type_id'))
    note = db.Column(db.Text)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.photo_id'))


