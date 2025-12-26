from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db import get_db
import datetime

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/thresholds', methods=['GET'])
@jwt_required()
def get_thresholds():
    """Get user's alert thresholds"""
    user_id = get_jwt_identity()
    db = get_db()
    thresholds = db.alert_thresholds.find_one({"user_id": user_id})
    
    if not thresholds:
        # Return default thresholds
        defaults = {
            "heart_rate_min": 60,
            "heart_rate_max": 100,
            "heart_rate_enabled": True,
            "bp_systolic_max": 140,
            "bp_diastolic_max": 90,
            "bp_enabled": True,
            "blood_sugar_min": 70,
            "blood_sugar_max": 140,
            "blood_sugar_enabled": True
        }
        return jsonify(defaults), 200
    
    thresholds['_id'] = str(thresholds['_id'])
    return jsonify(thresholds), 200

@alerts_bp.route('/thresholds', methods=['POST', 'PUT'])
@jwt_required()
def update_thresholds():
    """Update user's alert thresholds"""
    user_id = get_jwt_identity()
    data = request.get_json()
    db = get_db()
    
    # Validate thresholds
    if 'heart_rate_min' in data and 'heart_rate_max' in data:
        if int(data['heart_rate_min']) >= int(data['heart_rate_max']):
            return jsonify({"msg": "Heart rate min must be less than max"}), 400
    
    if 'blood_sugar_min' in data and 'blood_sugar_max' in data:
        if int(data['blood_sugar_min']) >= int(data['blood_sugar_max']):
            return jsonify({"msg": "Blood sugar min must be less than max"}), 400
    
    threshold_data = {
        "user_id": user_id,
        "heart_rate_min": data.get('heart_rate_min', 60),
        "heart_rate_max": data.get('heart_rate_max', 100),
        "heart_rate_enabled": data.get('heart_rate_enabled', True),
        "bp_systolic_max": data.get('bp_systolic_max', 140),
        "bp_diastolic_max": data.get('bp_diastolic_max', 90),
        "bp_enabled": data.get('bp_enabled', True),
        "blood_sugar_min": data.get('blood_sugar_min', 70),
        "blood_sugar_max": data.get('blood_sugar_max', 140),
        "blood_sugar_enabled": data.get('blood_sugar_enabled', True),
        "updated_at": datetime.datetime.utcnow()
    }
    
    db.alert_thresholds.update_one(
        {"user_id": user_id},
        {"$set": threshold_data},
        upsert=True
    )
    
    return jsonify({"msg": "Thresholds updated successfully"}), 200

@alerts_bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get user's alerts"""
    user_id = get_jwt_identity()
    db = get_db()
    
    # Get unread alerts
    unread = list(db.alerts.find({
        "user_id": user_id,
        "read": False
    }).sort("timestamp", -1).limit(20))
    
    # Get recent read alerts
    read = list(db.alerts.find({
        "user_id": user_id,
        "read": True
    }).sort("timestamp", -1).limit(10))
    
    for alert in unread + read:
        alert['_id'] = str(alert['_id'])
        if 'timestamp' in alert and isinstance(alert['timestamp'], datetime.datetime):
            alert['timestamp'] = alert['timestamp'].isoformat()
    
    return jsonify({
        "unread": unread,
        "read": read
    }), 200

@alerts_bp.route('/<alert_id>/read', methods=['POST'])
@jwt_required()
def mark_read(alert_id):
    """Mark an alert as read"""
    from bson.objectid import ObjectId
    user_id = get_jwt_identity()
    db = get_db()
    
    db.alerts.update_one(
        {"_id": ObjectId(alert_id), "user_id": user_id},
        {"$set": {"read": True, "read_at": datetime.datetime.utcnow()}}
    )
    
    return jsonify({"msg": "Alert marked as read"}), 200

@alerts_bp.route('/check', methods=['POST'])
@jwt_required()
def check_alerts():
    """Check current vitals against thresholds and generate alerts"""
    user_id = get_jwt_identity()
    db = get_db()
    
    # Get latest vitals
    latest = db.latest_vitals.find_one({"user_id": user_id})
    if not latest:
        return jsonify({"msg": "No vitals data available"}), 400
    
    # Get thresholds
    thresholds = db.alert_thresholds.find_one({"user_id": user_id})
    if not thresholds:
        return jsonify({"msg": "No thresholds set"}), 400
    
    alerts = []
    
    # Check heart rate
    if latest.get('heart_rate') and thresholds.get('heart_rate_enabled'):
        hr = int(latest.get('heart_rate'))
        if hr > thresholds.get('heart_rate_max', 100):
            alerts.append({
                "type": "heart_rate",
                "message": f"Heart Rate Alert: {hr} BPM exceeds maximum threshold ({thresholds.get('heart_rate_max')} BPM)",
                "severity": "warning" if hr < thresholds.get('heart_rate_max', 100) + 20 else "critical"
            })
        elif hr < thresholds.get('heart_rate_min', 60):
            alerts.append({
                "type": "heart_rate",
                "message": f"Heart Rate Alert: {hr} BPM below minimum threshold ({thresholds.get('heart_rate_min')} BPM)",
                "severity": "warning" if hr > thresholds.get('heart_rate_min', 60) - 20 else "critical"
            })
    
    # Check blood pressure
    if latest.get('bp_systolic') and thresholds.get('bp_enabled'):
        sys = int(latest.get('bp_systolic'))
        dia = int(latest.get('bp_diastolic', 80))
        if sys > thresholds.get('bp_systolic_max', 140):
            alerts.append({
                "type": "blood_pressure",
                "message": f"Blood Pressure Alert: {sys}/{dia} mmHg exceeds threshold ({thresholds.get('bp_systolic_max')}/{thresholds.get('bp_diastolic_max', 90)} mmHg)",
                "severity": "warning" if sys < thresholds.get('bp_systolic_max', 140) + 20 else "critical"
            })
    
    # Check blood sugar
    if latest.get('blood_sugar') and thresholds.get('blood_sugar_enabled'):
        sugar = int(latest.get('blood_sugar'))
        if sugar > thresholds.get('blood_sugar_max', 140):
            alerts.append({
                "type": "blood_sugar",
                "message": f"Blood Sugar Alert: {sugar} mg/dL exceeds maximum threshold ({thresholds.get('blood_sugar_max')} mg/dL)",
                "severity": "warning" if sugar < thresholds.get('blood_sugar_max', 140) + 30 else "critical"
            })
        elif sugar < thresholds.get('blood_sugar_min', 70):
            alerts.append({
                "type": "blood_sugar",
                "message": f"Blood Sugar Alert: {sugar} mg/dL below minimum threshold ({thresholds.get('blood_sugar_min')} mg/dL)",
                "severity": "critical"
            })
    
    # Save alerts if any
    if alerts:
        for alert in alerts:
            db.alerts.insert_one({
                "user_id": user_id,
                "timestamp": datetime.datetime.utcnow(),
                "alerts": [alert['message']],
                "read": False,
                "severity": alert['severity'],
                "type": alert['type']
            })
    
    return jsonify({
        "alerts": alerts,
        "count": len(alerts)
    }), 200

@alerts_bp.route('/manual', methods=['POST'])
@jwt_required()
def create_manual_alert():
    """Create a manual custom alert"""
    user_id = get_jwt_identity()
    data = request.get_json()
    db = get_db()
    
    alert_text = data.get('alert_text')
    severity = data.get('severity', 'warning') # warning or critical
    
    if not alert_text:
        return jsonify({"msg": "Alert text is required"}), 400
        
    db.alerts.insert_one({
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "alerts": [alert_text], # Stored as list for consistency with auto alerts
        "read": False,
        "severity": severity,
        "type": "manual"
    })
    
    return jsonify({"msg": "Manual alert created"}), 201
