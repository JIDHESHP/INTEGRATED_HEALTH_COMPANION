from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db import get_db
from backend.services.risk_model import calculate_risk_score
import datetime

insights_bp = Blueprint('insights', __name__)

def generate_ai_insights(profile, latest_log, risk_data):
    """
    Generate AI-powered health insights based on user data
    """
    insights = {
        "summary": "",
        "risk_explanation": "",
        "improvement_suggestions": [],
        "preventive_care": []
    }
    
    if not latest_log:
        insights["summary"] = "No health data available. Please log your vitals to receive personalized insights."
        return insights
    
    # Generate personalized summary
    summary_parts = []
    if latest_log.get('heart_rate'):
        hr = int(latest_log.get('heart_rate', 70))
        if 60 <= hr <= 100:
            summary_parts.append(f"Your heart rate of {hr} BPM is within the normal range.")
        elif hr > 100:
            summary_parts.append(f"Your heart rate of {hr} BPM is elevated. Consider stress management and regular exercise.")
        else:
            summary_parts.append(f"Your heart rate of {hr} BPM is below normal. Consult with a healthcare provider.")
    
    if latest_log.get('bp_systolic') and latest_log.get('bp_diastolic'):
        sys = int(latest_log.get('bp_systolic', 120))
        dia = int(latest_log.get('bp_diastolic', 80))
        if sys < 120 and dia < 80:
            summary_parts.append(f"Your blood pressure ({sys}/{dia} mmHg) is optimal.")
        elif sys < 130 and dia < 80:
            summary_parts.append(f"Your blood pressure ({sys}/{dia} mmHg) is elevated. Monitor regularly.")
        else:
            summary_parts.append(f"Your blood pressure ({sys}/{dia} mmHg) is high. Lifestyle changes and medical consultation recommended.")
    
    if latest_log.get('blood_sugar'):
        sugar = int(latest_log.get('blood_sugar', 100))
        if 70 <= sugar <= 100:
            summary_parts.append(f"Your blood sugar of {sugar} mg/dL is in the normal fasting range.")
        elif 100 < sugar <= 140:
            summary_parts.append(f"Your blood sugar of {sugar} mg/dL is slightly elevated. Monitor your diet.")
        elif sugar > 140:
            summary_parts.append(f"Your blood sugar of {sugar} mg/dL is high. Consider dietary changes and medical consultation.")
        else:
            summary_parts.append(f"Your blood sugar of {sugar} mg/dL is low. Ensure regular meals.")
    
    insights["summary"] = " ".join(summary_parts) if summary_parts else "Based on your health data, here's your personalized summary."
    
    # Risk explanation
    risk_level = risk_data.get('level', 'Low')
    risk_score = risk_data.get('score', 0)
    factors = risk_data.get('factors', [])
    
    if risk_level == "High":
        insights["risk_explanation"] = f"Your current health risk score is {risk_score}/100, indicating a HIGH risk level. "
        insights["risk_explanation"] += "Primary contributing factors include: " + ", ".join(factors[:3]) + ". "
        insights["risk_explanation"] += "Immediate attention and lifestyle modifications are recommended."
    elif risk_level == "Moderate":
        insights["risk_explanation"] = f"Your current health risk score is {risk_score}/100, indicating a MODERATE risk level. "
        insights["risk_explanation"] += "Key factors: " + ", ".join(factors[:2]) + ". "
        insights["risk_explanation"] += "Proactive measures can help reduce your risk."
    else:
        insights["risk_explanation"] = f"Your current health risk score is {risk_score}/100, indicating a LOW risk level. "
        insights["risk_explanation"] += "Continue maintaining healthy habits and regular monitoring."
    
    # Improvement suggestions
    suggestions = []
    
    if risk_data.get('risk_probabilities', {}).get('hypertension', 0) > 0.3:
        suggestions.append("Reduce sodium intake to less than 2,300mg per day")
        suggestions.append("Engage in at least 150 minutes of moderate exercise weekly")
        suggestions.append("Practice stress-reduction techniques like meditation or yoga")
    
    if risk_data.get('risk_probabilities', {}).get('diabetes', 0) > 0.3:
        suggestions.append("Follow a balanced diet with controlled carbohydrate intake")
        suggestions.append("Monitor blood sugar levels regularly")
        suggestions.append("Maintain a healthy weight through diet and exercise")
    
    if risk_data.get('risk_probabilities', {}).get('metabolic', 0) > 0.3:
        suggestions.append("Aim for gradual weight loss of 5-10% of body weight")
        suggestions.append("Increase daily physical activity")
        suggestions.append("Focus on whole foods and reduce processed foods")
    
    if risk_data.get('risk_probabilities', {}).get('cardiac', 0) > 0.3:
        suggestions.append("Avoid smoking and limit alcohol consumption")
        suggestions.append("Maintain a heart-healthy diet (Mediterranean or DASH diet)")
        suggestions.append("Get regular cardiovascular exercise")
    
    # General suggestions
    if not suggestions:
        suggestions.append("Maintain regular health check-ups")
        suggestions.append("Stay hydrated and get adequate sleep (7-9 hours)")
        suggestions.append("Continue monitoring your vitals regularly")
    
    insights["improvement_suggestions"] = suggestions[:5]  # Limit to 5 suggestions
    
    # Preventive care recommendations
    preventive = []
    
    if profile:
        age = profile.get('age', 0)
        if age > 50:
            preventive.append("Annual comprehensive health screening")
            preventive.append("Colonoscopy (if not done in last 10 years)")
            preventive.append("Bone density scan")
        elif age > 40:
            preventive.append("Annual physical examination")
            preventive.append("Cholesterol and lipid panel")
            preventive.append("Diabetes screening")
        else:
            preventive.append("Regular health check-ups every 2-3 years")
            preventive.append("Dental check-ups twice yearly")
            preventive.append("Eye examination every 2 years")
    
    # Add specific preventive care based on risk factors
    if 'High Blood Pressure' in factors or 'Hypertension' in str(factors):
        preventive.append("Regular blood pressure monitoring at home")
        preventive.append("ECG/EKG if recommended by physician")
    
    if 'High Blood Sugar' in factors or 'Diabetes' in str(factors):
        preventive.append("HbA1c test every 3-6 months")
        preventive.append("Annual eye examination for diabetic retinopathy")
        preventive.append("Foot examination for diabetic neuropathy")
    
    if not preventive:
        preventive.append("Annual wellness visit")
        preventive.append("Age-appropriate cancer screenings")
        preventive.append("Immunization updates")
    
    insights["preventive_care"] = preventive[:5]  # Limit to 5 recommendations
    
    return insights

@insights_bp.route('/', methods=['GET'])
@jwt_required()
def get_insights():
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
        latest_log = db.latest_vitals.find_one({"user_id": user_id})
    
    # Get Risk Score
    result = calculate_risk_score(profile, latest_log)
    if len(result) == 2:
        score, factors = result
        risk_data = {
            "score": score,
            "level": "Low" if score <= 30 else ("Moderate" if score <= 60 else "High"),
            "factors": factors,
            "risk_probabilities": {},
            "trend_indicators": []
        }
    else:
        score, factors, trend_indicators, risk_probabilities, derived_metrics = result
        risk_data = {
            "score": score,
            "level": "Low" if score <= 30 else ("Moderate" if score <= 60 else "High"),
            "factors": factors,
            "risk_probabilities": risk_probabilities,
            "trend_indicators": trend_indicators,
            "derived_metrics": derived_metrics
        }
    
    # Generate AI Insights
    insights = generate_ai_insights(profile, latest_log, risk_data)
    
    return jsonify({
        "insights": insights,
        "risk_data": risk_data,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }), 200

