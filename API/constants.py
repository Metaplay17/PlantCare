import re

IMAGE_FOLDER = 'static/userphotos/'  # Папка для загрузки
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Разрешенные форматы
password_regex = re.compile(r'^(?=.*\d)(?=.*[A-Z]).{8,30}$')
email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
username_regex = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
EXCLUDED_ENDPOINTS = [
    'log_in',
    'log_in_page',
    'sign_up_page',
    'register'
]