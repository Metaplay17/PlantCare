from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask("app")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app,
     origins=[r"http://localhost:\d+"],
     supports_credentials=True)

db = SQLAlchemy(app)
