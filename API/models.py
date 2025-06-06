from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask("app")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qazedcrfvs1A@localhost/PlantCare'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app,
     origins=[r"http://localhost:\d+"],
     supports_credentials=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TaskType(db.Model):
    __tablename__ = "task_types"
    task_type_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<TaskType(task_id={self.task_id})>"


class RepeatType(db.Model):
    __tablename__ = "repeat_types"
    repeat_type_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(20))

    def __repr__(self):
        return f"<RepeatType(repeat_type_id={self.repeat_type_id})>"


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    login = db.Column(db.String(20))
    email = db.Column(db.String(30))
    password_hash = db.Column(db.Text)
    code = db.Column(db.Numeric(precision=6, scale=0), default=0)
    isActivated = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User(username={self.username})>"


class Plant(db.Model):
    __tablename__ = "plants"
    plant_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    science_name = db.Column(db.String(50))
    date_added = db.Column(db.Date, default=date.today)
    place = db.Column(db.Numeric(precision=5, scale=1))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    photos = db.relationship('Photo', backref='plant', lazy=True)
    tasks = db.relationship('Task', backref='plant', lazy=True)
    notes = db.relationship('Note', backref='plant', lazy=True)

    def __repr__(self):
        return f"<Plant(name={self.name}, science_name={self.science_name})>"


class Photo(db.Model):
    __tablename__ = "photos"
    photo_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    filename = db.Column(db.String(80))
    notes = db.relationship('Note', backref='photo', lazy=True)

    def __repr__(self):
        return f"<Photo(photo_id={self.photo_id}, filename={self.filename})>"


class MainPhoto(db.Model):
    __tablename__ = "main_photos"
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'), primary_key=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.photo_id'))


class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(50))
    task_description = db.Column(db.Text)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    task_type_id = db.Column(db.Integer, db.ForeignKey('task_types.task_type_id'))
    task_date = db.Column(db.Date)
    repeat_type_id = db.Column(db.Integer, db.ForeignKey('repeat_types.repeat_type_id'))
    task_type = db.relationship('TaskType', backref='tasks')
    repeat_type = db.relationship('RepeatType', backref='tasks')

    def __repr__(self):
        return f"<Task(task_id={self.task_id})>"


class Note(db.Model):
    __tablename__ = "notes"
    note_id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.plant_id'))
    note_name = db.Column(db.String(70))
    description = db.Column(db.Text)
    photo_id = db.Column(db.Integer, db.ForeignKey('photos.photo_id'))
    date_added = db.Column(db.Date, default=date.today)

    def __repr__(self):
        return f"<Note(note_id={self.note_id})>"


class Calendar(db.Model):
    __tablename__ = "calendar"
    entry_id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.task_id'))




