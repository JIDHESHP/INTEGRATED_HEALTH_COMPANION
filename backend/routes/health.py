from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db import get_db
from backend.services.risk_model import calculate_risk_score
import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/log', methods=['POST'])
@jwt_required()
def log_health_data():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Helper to clean input
    def clean_input(val):
        if val is None: return None
        if isinstance(val, str):
            val = val.strip()
            if val == '': return None
            # Allow generic casting
            try:
                return int(val)
            except ValueError:
                return 'invalid'
        return int(val)

    # Validate inputs
    try:
        heart_rate = clean_input(data.get('heart_rate'))
        bp_systolic = clean_input(data.get('bp_systolic'))
        bp_diastolic = clean_input(data.get('bp_diastolic'))
        blood_sugar = clean_input(data.get('blood_sugar'))

        if heart_rate == 'invalid': return jsonify({"msg": "Heart rate must be a number"}), 400
        if bp_systolic == 'invalid': return jsonify({"msg": "Systolic BP must be a number"}), 400
        if bp_diastolic == 'invalid': return jsonify({"msg": "Diastolic BP must be a number"}), 400
        if blood_sugar == 'invalid': return jsonify({"msg": "Blood sugar must be a number"}), 400

        if heart_rate is not None and (heart_rate < 30 or heart_rate > 220):
            return jsonify({"msg": "Heart rate must be between 30-220 BPM"}), 400
        if bp_systolic is not None and (bp_systolic < 70 or bp_systolic > 250):
            return jsonify({"msg": "Systolic BP must be between 70-250 mmHg"}), 400
        if bp_diastolic is not None and (bp_diastolic < 40 or bp_diastolic > 150):
            return jsonify({"msg": "Diastolic BP must be between 40-150 mmHg"}), 400
        if blood_sugar is not None and (blood_sugar < 50 or blood_sugar > 500):
            return jsonify({"msg": "Blood sugar must be between 50-500 mg/dL"}), 400

    except (ValueError, TypeError) as e:
        print(f"Validation Error: {e}")
        return jsonify({"msg": "Invalid input formatting."}), 400
    
    # Expected: heart_rate, bp_systolic, bp_diastolic, blood_sugar
    entry = {
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "heart_rate": heart_rate,
        "bp_systolic": bp_systolic,
        "bp_diastolic": bp_diastolic,
        "blood_sugar": blood_sugar
    }
    
    db = get_db()
    
    try:
        db.health_logs.insert_one(entry)
    except Exception as e:
         print(f"Mongo Insert Error: {e}")
         return jsonify({"msg": "Database insert error"}), 500
    
    # Update latest vitals - explicit Find/Update/Insert to avoid upsert Check/Write errors
    try:
        existing_latest = db.latest_vitals.find_one({"user_id": user_id})
        latest_entry_data = {
            **entry,
            "updated_at": datetime.datetime.utcnow()
        }
        
        if existing_latest:
            # Update
            db.latest_vitals.update_one(
                {"_id": existing_latest["_id"]},
                {"$set": latest_entry_data}
            )
        else:
            # Insert
            db.latest_vitals.insert_one(latest_entry_data)
            
    except Exception as e:
        print(f"Error updating latest_vitals: {e}")
        # We don't block the request if this fails, but we assume the log was inserted.
    
    # Check for abnormalities using user-defined thresholds
    alerts = []
    try:
        user_thresholds = db.alert_thresholds.find_one({"user_id": user_id})
        
        if user_thresholds:
            if heart_rate and user_thresholds.get('heart_rate_enabled'):
                hr_max = user_thresholds.get('heart_rate_max', 100)
                hr_min = user_thresholds.get('heart_rate_min', 60)
                if int(heart_rate) > hr_max or int(heart_rate) < hr_min:
                    alerts.append(f"Heart Rate Alert: {heart_rate} BPM (Range: {hr_min}-{hr_max})")
            
            if bp_systolic and user_thresholds.get('bp_enabled'):
                bp_max = user_thresholds.get('bp_systolic_max', 140)
                if int(bp_systolic) > bp_max:
                    alerts.append(f"Blood Pressure Alert: {bp_systolic}/{bp_diastolic} mmHg")
            
            if blood_sugar and user_thresholds.get('blood_sugar_enabled'):
                sugar_max = user_thresholds.get('blood_sugar_max', 140)
                sugar_min = user_thresholds.get('blood_sugar_min', 70)
                if int(blood_sugar) > sugar_max or int(blood_sugar) < sugar_min:
                    alerts.append(f"Blood Sugar Alert: {blood_sugar} mg/dL")
        else:
            # Default thresholds
            if heart_rate and (int(heart_rate) > 100 or int(heart_rate) < 60):
                alerts.append("Abnormal Heart Rate")
            if blood_sugar and int(blood_sugar) > 140:
                alerts.append("High Blood Sugar")
            
        if alerts:
            db.alerts.insert_one({
                "user_id": user_id,
                "timestamp": datetime.datetime.utcnow(),
                "alerts": alerts,
                "read": False,
                "severity": "warning" if len(alerts) == 1 else "critical"
            })
    except Exception as e:
        print(f"Alert Processing Error: {e}")
        
    return jsonify({"msg": "Logged successfully", "alerts": alerts}), 201

@health_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    user_id = get_jwt_identity()
    db = get_db()
    logs = list(db.health_logs.find({"user_id": user_id}).sort("timestamp", -1).limit(50))
    for log in logs:
        log['_id'] = str(log['_id'])
        if 'timestamp' in log and isinstance(log['timestamp'], datetime.datetime):
            log['timestamp'] = log['timestamp'].isoformat()
    return jsonify(logs), 200

@health_bp.route('/latest', methods=['GET'])
@jwt_required()
def get_latest_vitals():
    """Get the latest vitals for the user"""
    user_id = get_jwt_identity()
    db = get_db()
    latest = db.latest_vitals.find_one({"user_id": user_id})
    if latest:
        latest['_id'] = str(latest['_id'])
        if 'timestamp' in latest and isinstance(latest['timestamp'], datetime.datetime):
            latest['timestamp'] = latest['timestamp'].isoformat()
        if 'updated_at' in latest and isinstance(latest['updated_at'], datetime.datetime):
            latest['updated_at'] = latest['updated_at'].isoformat()
    return jsonify(latest or {}), 200

@health_bp.route('/risk', methods=['GET'])
@jwt_required()
def get_risk_score():
    user_id = get_jwt_identity()
    db = get_db()
    
    # Get Profile
    profile = db.profiles.find_one({"user_id": user_id})
    
    # Get Latest Log
    latest_log = db.health_logs.find_one(
        {"user_id": user_id},
        sort=[("timestamp", -1)]
    )
    
    if not latest_log:
        # Try latest vitals
        latest_log = db.latest_vitals.find_one({"user_id": user_id})
    
    result = calculate_risk_score(profile, latest_log)
    
    if len(result) == 2:
        # Old format
        score, factors = result
        trend_indicators = []
        risk_probabilities = {}
        derived_metrics = {}
    else:
        score, factors, trend_indicators, risk_probabilities, derived_metrics = result
    
    risk_level = "Low"
    if score > 60: risk_level = "High"
    elif score > 30: risk_level = "Moderate"
    
    return jsonify({
        "score": score,
        "level": risk_level,
        "factors": factors,
        "trend_indicators": trend_indicators,
        "risk_probabilities": risk_probabilities,
        "derived_metrics": derived_metrics
    }), 200
