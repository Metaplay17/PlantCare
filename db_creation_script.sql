CREATE SEQUENCE IF NOT EXISTS plant_id_seq 
AS INT
INCREMENT BY 1
MINVALUE 1
NO MAXVALUE
START WITH 1;

CREATE SEQUENCE IF NOT EXISTS task_id_seq 
AS INT
INCREMENT BY 1
MINVALUE 1
NO MAXVALUE
START WITH 1;

CREATE SEQUENCE IF NOT EXISTS note_id_seq 
AS INT
INCREMENT BY 1
MINVALUE 1
NO MAXVALUE
START WITH 1;

CREATE SEQUENCE IF NOT EXISTS photo_id_seq 
AS INT
INCREMENT BY 1
MINVALUE 1
NO MAXVALUE
START WITH 1;

CREATE SEQUENCE IF NOT EXISTS task_detail_id_seq 
AS INT
INCREMENT BY 1
MINVALUE 1
NO MAXVALUE
START WITH 1;

CREATE SEQUENCE IF NOT EXISTS note_type_id_seq 
AS INT
INCREMENT BY 1
MINVALUE 1
NO MAXVALUE
START WITH 1;

CREATE SEQUENCE IF NOT EXISTS task_type_id_seq 
AS INT
INCREMENT BY 1
MINVALUE 1
NO MAXVALUE
START WITH 1;



CREATE TABLE IF NOT EXISTS plants (
    plant_id INT PRIMARY KEY DEFAULT nextval('plant_id_seq'),
    name VARCHAR(30),
    science_name VARCHAR(50),
    date_added DATE,
    place NUMERIC(5)
);

CREATE TABLE IF NOT EXISTS task_types (
    task_type_id INT PRIMARY KEY DEFAULT nextval('task_type_id_seq'),
    description TEXT
);

CREATE TABLE IF NOT EXISTS photos (
    photo_id INT PRIMARY KEY DEFAULT nextval('photo_id_seq'),
    plant_id INT,
    filename VARCHAR(50),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id)
);

CREATE TABLE IF NOT EXISTS main_photos (
    plant_id INT PRIMARY KEY
    photo_id INT
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id)
    FOREIGN KEY (photo_id) REFERENCES photos(photo_id)
);

CREATE TABLE IF NOT EXISTS note_types (
    note_type_id INT PRIMARY KEY DEFAULT nextval('note_type_id_seq'),
    description TEXT,
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id INT PRIMARY KEY DEFAULT nextval('task_id_seq'),
    plant_id INT,
    task_type_id INT,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
    FOREIGN KEY (task_type_id) REFERENCES tasks(task_type_id)
);

CREATE TABLE IF NOT EXISTS tasks_details (
    task_detail_id INT PRIMARY KEY DEFAULT nextval('task_detail_id_seq'),
    task_id INT,
    detail TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE TABLE IF NOT EXISTS notes (
    note_id INT PRIMARY KEY DEFAULT nextval('note_id_seq'),
    plant_id INT,
    note_type_id INT,
    note TEXT,
    photo_id INT,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
    FOREIGN KEY (note_type_id) REFERENCES note_types(note_type_id),
    FOREIGN KEY (photo_id) REFERENCES photos(photo_id)
);