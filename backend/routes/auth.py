from flask import Blueprint, request, jsonify
from backend.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    db = get_db()
    if db.users.find_one({"email": email}):
        return jsonify({"msg": "User already exists"}), 409

    hashed_password = generate_password_hash(password)
    user_id = db.users.insert_one({
        "email": email,
        "password": hashed_password,
        "name": name,
        "created_at": datetime.datetime.utcnow()
    }).inserted_id

    return jsonify({"msg": "User created successfully", "user_id": str(user_id)}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    db = get_db()
    user = db.users.find_one({"email": email})

    if not user or not check_password_hash(user['password'], password):
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({"access_token": access_token, "name": user.get('name')}), 200
