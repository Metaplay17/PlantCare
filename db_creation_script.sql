-- Пользователи
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    login VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(30) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Типы задач
CREATE TABLE task_types (
    task_type_id SERIAL PRIMARY KEY,
    description TEXT
);

-- Типы повторений
CREATE TABLE repeat_types (
    repeat_type_id SERIAL PRIMARY KEY,
    description VARCHAR(20)
);

-- Растения
CREATE TABLE plants (
    plant_id SERIAL PRIMARY KEY,
    name VARCHAR(30),
    science_name VARCHAR(50),
    date_added DATE DEFAULT CURRENT_DATE,
    place NUMERIC(5,1),
    user_id INTEGER NOT NULL REFERENCES users(user_id)
);

-- Фотографии
CREATE TABLE photos (
    photo_id SERIAL PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(plant_id),
    filename VARCHAR(50),
    user_id INTEGER NOT NULL REFERENCES users(user_id)
);

-- Основные фотографии (один к одному: растение ↔ фото)
CREATE TABLE main_photos (
    plant_id INTEGER PRIMARY KEY REFERENCES plants(plant_id),
    photo_id INTEGER UNIQUE REFERENCES photos(photo_id)
);

-- Задачи
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    task_name VARCHAR(50),
    task_description TEXT,
    plant_id INTEGER REFERENCES plants(plant_id),
    task_type_id INTEGER REFERENCES task_types(task_type_id),
    task_date DATE,
    repeat_type_id INTEGER REFERENCES repeat_types(repeat_type_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id)
);

-- Заметки
CREATE TABLE notes (
    note_id SERIAL PRIMARY KEY,
    plant_id INTEGER REFERENCES plants(plant_id),
    note_name VARCHAR(70),
    description TEXT,
    photo_id INTEGER REFERENCES photos(photo_id),
    date_added DATE DEFAULT CURRENT_DATE,
    user_id INTEGER NOT NULL REFERENCES users(user_id)
);

-- Календарь
CREATE TABLE calendar (
    entry_id SERIAL PRIMARY KEY,
    entry_date DATE,
    task_id INTEGER REFERENCES tasks(task_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id)
);

-- Фильтрация по пользователю
CREATE INDEX idx_plants_user_id ON plants(user_id);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_notes_user_id ON notes(user_id);