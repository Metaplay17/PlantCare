from extensions import app
from flask import jsonify, request, redirect, url_for, make_response, abort
from utils import is_login_exist, is_email_exist, get_user_id_by_login
from constants import username_regex, email_regex, password_regex
from models import User
from extensions import db
from datetime import datetime
import bcrypt
import sendmail
import random
from redis_conf import r
from custom_exceptions import *

from flask_jwt_extended import (
    JWTManager, create_access_token,
    create_refresh_token, set_refresh_cookies, set_access_cookies,
    jwt_required, get_jwt_identity, get_jwt,
    unset_jwt_cookies, verify_jwt_in_request,
)

from app import scheduler

jwt = JWTManager(app)


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
    data = request.json()
    if "email" not in data.keys():
        abort(400)
    email = data["email"]
    if r.get(f"last_recover_request:{email}"):
        raise TooFrequentRequest

    app.logger.info(f"Send recover code attempt, email: {data['email']}")
    email = data["email"]
    user = User.query.filter_by(email=email)
    r.setex(f"last_recover_request:{email}", 180, datetime.now().isoformat())
    if not user:
        abort(404)

    code = random.randint(100000, 999999)
    user.code = code
    if sendmail.send_recover_email(email, code):
        scheduler.add_job(expire_usercode(user.user_id), 'date', run_date=datetime.now() + datetime.timedelta(minutes=3))
    else:
        app.logger.critical(f"recover email was not sent, email: {email}")
        raise EmailNotSent


def expire_usercode(user_id):
    user = User.query.filter_by(user_id=user_id)
    if not user:
        app.logger.critical(f"User to expire usercode not found, user_id: {user_id}")
        raise UserNotFound

    user.usercode = None


@app.route('/auth/recover-password', methods=['POST'])
def recover_password():
    data = request.json()
    if "email" not in data.keys() or "code" not in data.keys() or "new_password" not in data.keys():
        abort(400)
    app.logger.info(f"Recover password attempt, email: {data['email']}")
    email = data["email"]
    code = data["code"]
    new_password = data["new_password"]

    if not email or not code or not new_password:
        abort(400)

    user = User.query.filter_by(email=email)
    if not user:
        abort(404)
    if user.code != code:
        abort(403)
    salt = bcrypt.gensalt()
    user.password_hash = bcrypt.hashpw(data["password"].encode(), salt).decode('utf-8')
    db.session.commit()


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
