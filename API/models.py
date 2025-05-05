from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_cors import CORS

app = Flask("app")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qazedcrfvs1A@localhost/PlantCare'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)


class TaskType(db.Model):
    __tablename__ = "task_types"
    task_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<TaskType(task_id={self.task_id})>"


class NoteType(db.Model):
    __tablename__ = "note_types"
    note_type_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<NoteType(note_type_id={self.note_type_id})>"


class RepeatType(db.Model):
    __tablename__ = "repeat_types"
    repeat_type_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))

    def __repr__(self):
        return f"<RepeatType(repeat_type_id={self.repeat_type_id})>"


class Plant(db.Model):
    __tablename__ = "plants"
    plant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    science_name = db.Column(db.String(50))
    date_added = db.Column(db.Date, default=date.today)
    place = db.Column(db.Numeric(precision=5, scale=1))
    photos = db.relationship('Photo', backref='plant', lazy=True)
    tasks = db.relationship('Task', backref='plant', lazy=True)
    notes = db.relationship('Note', backref='plant', lazy=True)

    def __repr__(self):
        return f"<Plant(name={self.name}, science_name={self.science_name})>"


class Photo(db.Model):
    __tablename__ = "photos"
    photo_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    filename = db.Column(db.String(50))
    notes = db.relationship('Note', backref='photo', lazy=True)

    def __repr__(self):
        return f"<Photo(photo_id={self.photo_id}, filename={self.filename})>"


class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    task_type_id = db.Column(db.Integer, db.ForeignKey('task_types.task_id'))
    task_date = db.Column(db.Date)
    repeat_type_id = db.Column(db.Integer, db.ForeignKey('repeat_types.repeat_type_id'))
    details = db.relationship('TaskDetail', backref='task', lazy=True)
    task_type = db.relationship('TaskType', backref='tasks')
    repeat_type = db.relationship('RepeatType', backref='tasks')

    def __repr__(self):
        return f"<Task(task_id={self.task_id})>"


class TaskDetail(db.Model):
    __tablename__ = "task_details"
    task_detail_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))
    detail = db.Column(db.Text)

    def __repr__(self):
        return f"<TaskDetail(task_detail_id={self.task_detail_id})>"


class Note(db.Model):
    __tablename__ = "notes"
    note_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    note_type_id = db.Column(db.Integer, db.ForeignKey('note_types.note_type_id'))
    note = db.Column(db.Text)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.photo_id'))
    note_type = db.relationship('NoteType', backref='notes')

    def __repr__(self):
        return f"<Note(note_id={self.note_id})>"
