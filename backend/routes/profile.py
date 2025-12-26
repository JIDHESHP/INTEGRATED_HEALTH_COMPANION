from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db import get_db
from bson.objectid import ObjectId

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    db = get_db()
    profile = db.profiles.find_one({"user_id": user_id})
    
    if profile:
        profile['_id'] = str(profile['_id'])
        # Ensure full_name is available or fallback to 'User'
        if 'name' in profile and not profile.get('full_name'):
             profile['full_name'] = profile['name']
        return jsonify(profile), 200
    return jsonify({}), 200

@profile_bp.route('/', methods=['POST', 'PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    db = get_db()
    
    # Calculate BMI if height and weight are present
    if 'height' in data and 'weight' in data:
        try:
            height_m = float(data['height']) / 100
            weight = float(data['weight'])
            data['bmi'] = round(weight / (height_m ** 2), 2)
        except:
            pass
            
    # Simple rule-based exercise recommendation
    exercises = []
    if data.get('activity_level') == 'sedentary':
        exercises = ["Walking 30 mins", "Stretching"]
    elif data.get('activity_level') == 'moderate':
        exercises = ["Jogging", "Cycling", "Basic Gym"]
    else:
        exercises = ["HIIT", "Strength Training", "Running"]
        
    data['recommended_exercises'] = exercises

    # Explicitly handle full name
    if 'full_name' in data:
        data['full_name'] = data['full_name'].strip()
        data['name'] = data['full_name'] # Sync with older 'name' field if exists

    db.profiles.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True
    )
    
    return jsonify({"msg": "Profile updated successfully", "bmi": data.get('bmi'), "recommendations": exercises}), 200
