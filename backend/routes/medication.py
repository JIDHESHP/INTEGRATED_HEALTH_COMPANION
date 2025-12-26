from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db import get_db
from bson.objectid import ObjectId
import datetime

medication_bp = Blueprint('medication', __name__)

@medication_bp.route('/', methods=['POST'])
@jwt_required()
def add_medication():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Expected: name, dosage, frequency, time
    medication = {
        "user_id": user_id,
        "name": data.get('name'),
        "dosage": data.get('dosage'),
        "frequency": data.get('frequency'),
        "time": data.get('time'),
        "created_at": datetime.datetime.utcnow(),
        "active": True
    }
    
    db = get_db()
    db.medications.insert_one(medication)
    
    return jsonify({"msg": "Medication added successfully"}), 201

@medication_bp.route('/', methods=['GET'])
@jwt_required()
def get_medications():
    user_id = get_jwt_identity()
    db = get_db()
    meds = list(db.medications.find({"user_id": user_id}))
    for med in meds:
        med['_id'] = str(med['_id'])
    return jsonify(meds), 200

@medication_bp.route('/<med_id>', methods=['DELETE'])
@jwt_required()
def delete_medication(med_id):
    user_id = get_jwt_identity()
    db = get_db()
    db.medications.delete_one({"_id": ObjectId(med_id), "user_id": user_id})
    return jsonify({"msg": "Medication deleted"}), 200
