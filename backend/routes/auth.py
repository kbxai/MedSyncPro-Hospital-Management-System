from flask import Blueprint, request, jsonify
from models import db,User,Patient
from flask_jwt_extended import create_access_token,get_jwt,verify_jwt_in_request
from functools import wraps
from datetime import timedelta
from datetime import datetime
import hashlib
import re
import os

auth_bp = Blueprint('auth',__name__)

@auth_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter(User.username == username,User.is_blocked == False).first()
    if user and user.check_pass(password):
        access_token = create_access_token(identity=username, additional_claims={'role': user.role},expires_delta=timedelta(hours=24))
        
        display_name = username
        if user.role == 'doctor' and user.doctor:
            display_name = user.doctor.name
        elif user.role == 'patient' and user.patient:
            display_name = user.patient.name
        elif user.role == 'admin':
            display_name = 'Admin'
        
        return jsonify({
            "msg": "Login Success",
            "access_token": access_token,
            "role": user.role,
            "name": display_name 
        }), 200
    
    else:
        return jsonify({"msg":"Invalid Username or password"}),400


@auth_bp.route('/signup',methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    username = data.get('username')

    if not isinstance(username, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", username):
         return jsonify(msg="Username must be a valid email address"), 400

    admin_username = os.getenv('user_name') or 'admin'
    if username.lower() == admin_username.lower():
        return jsonify(msg="This username is reserved"), 400

    user = User.query.filter(User.username == username).first()
    if user:
        return jsonify({"msg":"Username already Exists"}),400
    
    else:
        password = data.get('password')
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        
        if not all([username, password, name, age, gender]):
             return jsonify(msg="All fields are required"), 400
        
        try:
            age = int(age)
            if age < 0 or age > 120:
                raise ValueError
        except ValueError:
            return jsonify(msg="Invalid age"), 400

        if gender not in ['Male', 'Female', 'Other']:
            return jsonify(msg="Invalid gender"), 400

        new_user = User(username=username, role="patient")
        try:
            new_user.validate_password(password)
        except ValueError as e:
            return jsonify(msg=str(e)), 400

        new_user.set_pass(password=password)
        
        try:
            db.session.add(new_user)
            db.session.flush()

            new_pat = Patient(name=name,age=age,gender=gender,user_id=new_user.id)
            db.session.add(new_pat)

            db.session.commit()
            return jsonify({"msg":"Patient registered successfully"}),201
        except Exception:
            db.session.rollback()
            auth_bp.logger.exception("Patient registration failed")
            return jsonify(msg="Database error occurred during registration"), 500


@auth_bp.route('/set-password', methods=['POST'])
def set_password():
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    password = data.get('password')
    if not isinstance(token, str) or not isinstance(password, str):
        return jsonify(msg="Token and password are required"), 400

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    user = User.query.filter_by(password_setup_token_hash=token_hash).first()
    if not user or not user.password_setup_expires_at or user.password_setup_expires_at < datetime.utcnow():
        return jsonify(msg="Setup link is invalid or expired"), 400

    try:
        user.validate_password(password)
    except ValueError as error:
        return jsonify(msg=str(error)), 400

    user.set_pass(password)
    user.password_setup_token_hash = None
    user.password_setup_expires_at = None
    db.session.commit()
    return jsonify(msg="Password set successfully"), 200


def authorization(roles):
    if isinstance(roles, str):
        roles = [roles]

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args,**kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if claims.get("role") in roles:
                return fn(*args,**kwargs)
            
            else:
                return jsonify(msg=f"{' or '.join(roles)} only!"),403
        return decorator
    return wrapper