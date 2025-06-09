from flask import render_template, request, redirect, url_for, make_response, current_app


from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from utils import get_plant_id_by_photo, get_username

from flask_jwt_extended import (
    JWTManager, create_access_token,
    create_refresh_token, set_refresh_cookies, set_access_cookies,
    jwt_required, get_jwt_identity,
    unset_jwt_cookies, verify_jwt_in_request,
)

from logic import *
import sendmail
import bcrypt
import random
import time
from custom_exceptions import *
from constants import *
from utils import is_email_exist, is_login_exist, get_user_id_by_login
from redis_conf import r, jobstore
from extensions import app, db
from models import User
from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError, DBAPIError, IntegrityError, OperationalError
from custom_exceptions import TooFrequentRequest


load_dotenv()

jwt_secret_key = os.getenv("JWT_SECRET_KEY")

app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

app.config['JWT_SECRET_KEY'] = jwt_secret_key
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900  # 15 минут
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400 * 7  # 7 дней
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_SAMESITE"] = "None"  # работает только через HTTPS
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt = JWTManager(app)

scheduler = BackgroundScheduler()
scheduler.add_jobstore(jobstore)


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def log_request_time(response):
    elapsed = (time.time() - request.start_time) * 1000  # в мс
    app.logger.info(f"Request to {request.path} took {elapsed:.2f}ms")
    return response


@app.before_request
def refresh_token_middleware():
    if request.endpoint in EXCLUDED_ENDPOINTS:
        return  # Пропускаем middleware
    try:
        verify_jwt_in_request()
        return
    except Exception:
        pass
    try:
        # Вызываем /auth/refresh напрямую
        @jwt_required(refresh=True)
        def call_refresh():
            current_user = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user)

            response = make_response(jsonify({"status": "Token has been refreshed"}))
            set_access_cookies(response, new_access_token)
            return response

        refresh_response = call_refresh()

        # Получаем оригинальный путь
        original_path = request.path
        original_query = request.query_string.decode()

        # Формируем URL для редиректа
        redirect_url = original_path
        if original_query:
            redirect_url += '?' + original_query

        # Объединяем Set-Cookie из refresh и редирект
        redirect_response = redirect(redirect_url)
        for header, value in refresh_response.headers:
            redirect_response.headers[header] = value
        return redirect_response

    except Exception as e:
        return redirect(url_for('log_in_page'))


@app.route('/login', methods=['GET'])
def log_in_page():
    try:
        verify_jwt_in_request()
    except Exception:
        return render_template('sign-in.html', css_file='sign-in.css')
    return redirect(url_for('start_page'))


@app.route('/sign-up', methods=['GET'])
def sign_up_page():
    try:
        verify_jwt_in_request()
    except Exception:
        return render_template('sign-up.html', css_file='sign-up.css')
    return redirect(url_for('start_page'))


@app.route('/recover-password')
def recover_password_page():
    try:
        verify_jwt_in_request()
    except Exception:
        return render_template('recover-password.html', css_file='recover-password.css')
    return redirect(url_for('start_page'))


@app.route('/', methods=['GET'])
@jwt_required()
def start_page():
    return render_template('Home.html')


@app.route('/api', methods=['POST'])
@jwt_required()
def core():
    login = get_jwt_identity()
    user_id = get_user_id_by_login(login)
    data = request.json
    app.logger.info(f"Action: {data['action']} ActionData: {data['actionData'].keys()}, user_id: {user_id}")
    if data["action"] == "GetPage":
        if data["actionData"]["Page"] == "Plants":
            return render_template('plants.html')

        elif data["actionData"]["Page"] == "AddPlant":
            return render_template('add-plant.html', css_file='add-plant.css')

        elif data["actionData"]["Page"] == "AddPhoto":
            return render_template('add-photo.html', css_file='add-photo.css')

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
            app.logger.info(f"GetTasksPage, user_id: {user_id}")
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
            abort(400)
        return get_plant(data["actionData"]["plant_id"], user_id)

    elif data["action"] == "Photo":
        if "photo_id" not in data["actionData"].keys():
            abort(400)
        return get_photo(data["actionData"]["photo_id"], user_id)

    elif data["action"] == "Note":
        if "note_id" not in data["actionData"].keys():
            abort(400)
        return get_note(data["actionData"]["note_id"], user_id)

    elif data["action"] == "Task":
        if "task_id" not in data["actionData"].keys():
            abort(400)
        return get_task(data["actionData"]["task_id"], user_id)

    elif data["action"] == "PlantIdByPhoto":
        if "photo_id" not in data["actionData"].keys():
            abort(400)
        return get_plant_id_by_photo(data["actionData"]["photo_id"], user_id)

    elif data["action"] == "ChangeMainPhoto":
        if "photo_id" not in data["actionData"].keys() or "plant_id" not in data[
            "actionData"].keys() or "selected" not in data["actionData"]:
            abort(400)
        return change_main_photo(data["actionData"]["plant_id"], data["actionData"]["photo_id"],
                                 data["actionData"]["selected"], user_id)

    elif data["action"] == "ChangePlantPhoto":
        if "photo_id" not in data["actionData"].keys() or "plant_id" not in data["actionData"].keys():
            abort(400)
        return change_plant_photo(data["actionData"]["plant_id"], data["actionData"]["photo_id"], user_id)

    elif data["action"] == "IsMainPhoto":
        if "photo_id" not in data["actionData"].keys() or "plant_id" not in data["actionData"].keys():
            abort(400)
        return is_main_photo(data["actionData"]["plant_id"], data["actionData"]["photo_id"], user_id)

    elif data["action"] == "GetUsername":
        return get_username(user_id)

    elif data["action"] == "GetPlants":
        return get_plants(user_id)

    elif data["action"] == "GetPhotos":
        return get_photos(user_id)

    elif data["action"] == "GetNotes":
        return get_notes(user_id)

    elif data["action"] == "GetTasks":
        return get_tasks(user_id)

    elif data["action"] == "GetTaskTypes":
        return get_task_types()

    elif data["action"] == "GetRepeatTypes":
        return get_repeat_types()

    elif data["action"] == "GetDateTasks":
        if "date" not in data["actionData"].keys():
            abort(400)
        return get_date_tasks(str(data["actionData"]["date"]), user_id)

    elif data["action"] == "GetMonthTasks":
        return get_month_tasks(str(data["actionData"]["date"]), user_id)

    elif data["action"] == "AddPlant":
        return add_plant(data["actionData"], user_id)

    elif data["action"] == "AddNote":
        return add_note(data["actionData"], user_id)

    elif data["action"] == "AddTask":
        return add_task(data["actionData"], user_id)

    elif data["action"] == "UpdatePlant":
        return update_plant(data["actionData"], user_id)

    elif data["action"] == "UpdateTask":
        if "task_id" not in data["actionData"].keys() or "task_id" not in data[
            "actionData"].keys() or "task_name" not in data["actionData"].keys() or "task_description" not in data[
            "actionData"].keys() or "task_type_id" not in data["actionData"].keys() or "repeat_type_id" not in data[
            "actionData"].keys():
            abort(400)
        return update_task(data["actionData"]["task_id"], data["actionData"]["task_name"],
                           data["actionData"]["task_description"], data["actionData"]["task_date"],
                           data["actionData"]["task_type_id"], data["actionData"]["repeat_type_id"], user_id)

    elif data["action"] == "UpdateNote":
        if "note_id" not in data["actionData"].keys() or "name" not in data["actionData"].keys() or "description" not in \
                data["actionData"].keys() or "plant_id" not in data["actionData"].keys():
            abort(400)
        return update_note(data["actionData"]["note_id"], data["actionData"]["name"], data["actionData"]["description"],
                           data["actionData"]["plant_id"], user_id)

    elif data["action"] == "AddPhoto":
        return add_photo(data["actionData"], user_id)

    elif data["action"] == "DeletePhoto":
        return delete_photo(data["actionData"], user_id)

    elif data["action"] == "DeleteNote":
        return delete_note(data["actionData"], user_id)

    elif data["action"] == "DeleteTask":
        return delete_task(data["actionData"], user_id)

    elif data["action"] == "DeletePlant":
        return delete_plant(data["actionData"], user_id)

    else:
        abort(400)


@app.route('/register', methods=['POST'])
def register():
    try:
        verify_jwt_in_request()
    except Exception:  # Если пользователь не авторизован
        data = request.json
        if not username_regex.match(data["username"]) or not password_regex.match(
                data["password"]) or not email_regex.match(data["email"]) or not username_regex.match(data["login"]) or \
                data["password"] != data["confirm_password"]:
            return jsonify({"status": "Incorrect data"}), 400

        if is_login_exist(data["login"]):
            return jsonify({"status": "Login is already used"}), 409

        if is_email_exist(data["email"]):
            return jsonify({"status": "Email is already used"}), 409

        salt = bcrypt.gensalt()
        code = random.randint(100000, 999999)
        user = User(username=data["username"], login=data["login"],
                    password_hash=bcrypt.hashpw(data["password"].encode(), salt).decode('utf-8'), email=data["email"], code=code)
        if sendmail.send_activation_email(user.email, code):
            db.session.add(user)
            db.session.commit()
            app.logger.info(f"User registered, user_id {user.user_id}")
            return jsonify({"status": "success"}), 200

        app.logger.critical("Sendmail error")
        return jsonify({"status": "Server Error"}), 500

    # Если пользователь уже авторизован
    return redirect(url_for('start_page'))


@app.route('/auth/send-recover-code', methods=['POST'])
def send_recover_code():
    data = request.json
    if "email" not in data.keys():
        abort(400)
    email = data["email"]
    if r.get(f"last_recover_request:{email}"):
        raise TooFrequentRequest

    app.logger.info(f"Send recover code attempt, email: {data['email']}")
    email = data["email"]
    user = User.query.filter_by(email=email).first()
    r.setex(f"last_recover_request:{email}", 180, datetime.now().isoformat())
    if not user:
        abort(404)

    code = random.randint(100000, 999999)
    user.code = code
    if sendmail.send_recover_email(email, code):
        scheduler.add_job(expire_usercode, 'date', [user.user_id], run_date=datetime.now() + timedelta(minutes=3))
        app.logger.info(f"Task added: refresh recover code for email: {email}")
    else:
        app.logger.critical(f"recover email was not sent, email: {email}")
        raise EmailNotSent
    db.session.commit()
    return jsonify({"status": "success"}), 200


def expire_usercode(user_id):
    with app.app_context():
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            app.logger.critical(f"User to expire usercode not found, user_id: {user_id}")
            raise UserNotFound

        app.logger.info(f"Code was expired for user_id = {user_id}")
        user.code = None
        db.session.commit()


@app.route('/auth/recover-password', methods=['POST'])
def recover_password():
    data = request.json
    if "email" not in data.keys() or "code" not in data.keys() or "new_password" not in data.keys():
        abort(400)
    app.logger.info(f"Recover password attempt, email: {data['email']}")
    email = data["email"]
    try:
        code = int(data["code"])
    except ValueError:
        abort(400)

    new_password = data["new_password"]

    if not email or not code or not new_password:
        abort(400)

    user = User.query.filter_by(email=email).first()
    if not user:
        abort(404)
    if user.code != code:
        abort(403)
    salt = bcrypt.gensalt()
    user.password_hash = bcrypt.hashpw(data["new_password"].encode(), salt).decode('utf-8')
    db.session.commit()
    return jsonify({"status": "success"}), 200


@app.route('/auth/confirm_email', methods=['GET'])
def confirm_email():
    try:
        code = request.args.get('code')
        email = request.args.get('email')
        if not code or not email:
            return jsonify({"status": "No email or code"}), 400
        code = int(code)
    except ValueError:
        app.logger.info("Incorrect code format")
        return jsonify({"status": "Неверный формат email или кода"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        app.logger.info(f"User not found: email - {email}")
        abort(404)
    if user.code != code:
        app.logger.info(f"Wrong code activation attempt for email: {email}")
        return jsonify({"status": "Код неверный"}), 400
    else:
        user.code = 0
        user.isActivated = True
        db.session.commit()
        app.logger.info(f"Email confirmed: {email}")
    return redirect(url_for('log_in_page'))


@app.route('/auth/login', methods=['POST'])
def log_in():
    try:
        verify_jwt_in_request()
    except Exception:
        data = request.json
        login = data["login"]
        password_bytes = data["password"].encode()
        user = User.query.filter_by(login=login).first()
        if not user:
            abort(403)

        if not user.isActivated:
            return jsonify({"status": "Активируйте аккаунт"}), 406

        password_hash = user.password_hash.encode()
        if not bcrypt.checkpw(password_bytes, password_hash):
            abort(403)

        access_token = create_access_token(identity=login)
        refresh_token = create_refresh_token(identity=login)

        response = jsonify({"status": "success"})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        app.logger.info(f"User logged in, user_id: {get_user_id_by_login(login)}")
        return response

    return redirect(url_for('start_page'))


@app.route('/auth/refresh', methods=['POST', 'GET'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    app.logger.info(f"Access Cookie refreshed, user_id: {get_user_id_by_login(current_user)}")
    new_access_token = create_access_token(identity=current_user)
    response = make_response(jsonify({"status": "Token has been refreshed"}))
    set_access_cookies(response, new_access_token)
    return response


@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def log_out():
    current_user = get_jwt_identity()
    app.logger.info(f"Logged Out, user_id: {get_user_id_by_login(current_user)}")
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response


@app.errorhandler(DBAPIError)
def handle_db_driver_error(e):
    app.logger.error(f"db driver error: {e}", exc_info=True)
    db.session.rollback()
    return jsonify("Internal server error"), 500


@app.errorhandler(IntegrityError)
def handle_db_integrity_error(e):
    app.logger.error(f"db integrity error: {e}", exc_info=True)
    db.session.rollback()
    return jsonify("Internal server error"), 500


@app.errorhandler(OperationalError)
def handle_db_operational_error(e):
    app.logger.error(f"db operational error: {e}", exc_info=True)
    db.session.rollback()
    return jsonify("Internal server error"), 500


@app.errorhandler(SQLAlchemyError)
def handle_general_db_error(e):
    app.logger.error(f"Database error: {e}", exc_info=True)
    db.session.rollback()
    return jsonify({"status": "Internal Server Error"}), 500


@app.errorhandler(400)
def handle_400(e):
    app.logger.error(f"Bad Request: {e}")
    return jsonify({"status": "Bad Request"}), 400


@app.errorhandler(403)
def handle_403(e):
    app.logger.info(f"Forbidden: {e}")
    return jsonify({"status": "Forbidden"}), 403


@app.errorhandler(404)
def handle_404(e):
    app.logger.info(f"Not Found: {e}")
    return jsonify({"status": "Not Found"}), 404


@app.errorhandler(405)
def handle_405(e):
    app.logger.info(f"Method Not Allowed: {e}")
    return jsonify({"status": "Method Not Allowed"}), 405


@app.errorhandler(TooFrequentRequest)
def handle_425(e):
    app.logger.info(f"Too Early: {e}")
    return jsonify({"status": "Попробуйте позднее"}), 425


@app.errorhandler(500)
def handle_500(e):
    app.logger.error(f"Server Error: {e}", exc_info=True)
    return jsonify({"status": "Internal Server Error"}), 500


@app.errorhandler(Exception)
def handle_general_exception(e):
    app.logger.critical(f"Unknown exception: {e}", exc_info=True)
    return jsonify({"status": "Internal Server Error"}), 500


@app.cli.command("list-jobs")
def list_jobs():
    """Показывает все задачи"""
    jobs = scheduler.get_jobs()
    if not jobs:
        print("Нет активных задач")
    for job in jobs:
        print(f"ID: {job.id}, Следующий запуск: {job.next_run_time}")


if __name__ == "__main__":
    scheduler.start()
    app.run()
