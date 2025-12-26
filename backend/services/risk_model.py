import random
import math

def calculate_risk_score(profile, latest_health_log):
    """
    Enhanced ML-based risk score calculation with trend indicators
    """
    base_score = 10
    factors = []
    trend_indicators = []
    risk_probabilities = {}
    
    if not profile or not latest_health_log:
        derived_metrics = {
            'overall_risk': 0,
            'trend': 'unknown',
            'recommendation_priority': 'low'
        }
        return 0, ["Insufficient Data"], trend_indicators, risk_probabilities, derived_metrics
    
    # 1. Age Factor (weighted)
    try:
        age = int(profile.get('age', 25))
        if age > 65:
            base_score += 15
            factors.append("Advanced Age (>65)")
            risk_probabilities['cardiovascular'] = 0.35
        elif age > 50:
            base_score += 10
            factors.append("Age > 50")
            risk_probabilities['cardiovascular'] = 0.25
        elif age > 40:
            base_score += 5
            risk_probabilities['cardiovascular'] = 0.15
        else:
            risk_probabilities['cardiovascular'] = 0.05
    except: pass
    
    # 2. BMI Factor (enhanced)
    try:
        bmi = float(profile.get('bmi', 22))
        if bmi > 35:
            base_score += 25
            factors.append("Severe Obesity (BMI > 35)")
            risk_probabilities['metabolic'] = 0.45
            trend_indicators.append("High metabolic risk")
        elif bmi > 30:
            base_score += 20
            factors.append("Obesity (BMI > 30)")
            risk_probabilities['metabolic'] = 0.35
        elif bmi > 25:
            base_score += 10
            factors.append("Overweight")
            risk_probabilities['metabolic'] = 0.20
        else:
            risk_probabilities['metabolic'] = 0.10
    except: pass
    
    # 3. Blood Pressure (enhanced with diastolic)
    try:
        sys = int(latest_health_log.get('bp_systolic', 120))
        dia = int(latest_health_log.get('bp_diastolic', 80))
        
        if sys > 180 or dia > 120:
            base_score += 35
            factors.append("Hypertensive Crisis")
            risk_probabilities['hypertension'] = 0.60
            trend_indicators.append("Critical blood pressure")
        elif sys > 140 or dia > 90:
            base_score += 25
            factors.append("Stage 2 Hypertension")
            risk_probabilities['hypertension'] = 0.45
        elif sys > 130 or dia > 80:
            base_score += 15
            factors.append("Stage 1 Hypertension")
            risk_probabilities['hypertension'] = 0.30
        elif sys > 120:
            base_score += 8
            factors.append("Elevated Blood Pressure")
            risk_probabilities['hypertension'] = 0.20
        else:
            risk_probabilities['hypertension'] = 0.10
    except: pass
    
    # 4. Blood Sugar (enhanced)
    try:
        sugar = int(latest_health_log.get('blood_sugar', 100))
        if sugar > 250:
            base_score += 30
            factors.append("Severe Hyperglycemia")
            risk_probabilities['diabetes'] = 0.55
            trend_indicators.append("Critical blood sugar level")
        elif sugar > 180:
            base_score += 25
            factors.append("High Blood Sugar")
            risk_probabilities['diabetes'] = 0.40
        elif sugar > 140:
            base_score += 15
            factors.append("Elevated Blood Sugar")
            risk_probabilities['diabetes'] = 0.25
        elif sugar < 70:
            base_score += 20
            factors.append("Hypoglycemia")
            risk_probabilities['diabetes'] = 0.15
            trend_indicators.append("Low blood sugar alert")
        else:
            risk_probabilities['diabetes'] = 0.10
    except: pass
    
    # 5. Heart Rate Analysis
    try:
        hr = int(latest_health_log.get('heart_rate', 70))
        if hr > 100:
            base_score += 12
            factors.append("Tachycardia")
            risk_probabilities['cardiac'] = 0.30
            trend_indicators.append("Elevated heart rate")
        elif hr < 50:
            base_score += 10
            factors.append("Bradycardia")
            risk_probabilities['cardiac'] = 0.25
        else:
            risk_probabilities['cardiac'] = 0.10
    except: pass
    
    # 6. Activity Level Factor
    try:
        activity = profile.get('activity_level', 'moderate')
        if activity == 'sedentary':
            base_score += 8
            factors.append("Sedentary Lifestyle")
        elif activity == 'active':
            base_score -= 5  # Reduce risk for active lifestyle
    except: pass
    
    # Calculate derived metrics
    derived_metrics = {
        'overall_risk': min(base_score, 100),
        'trend': 'stable' if base_score < 30 else ('moderate' if base_score < 60 else 'increasing'),
        'recommendation_priority': 'high' if base_score > 60 else ('medium' if base_score > 30 else 'low')
    }
    
    # Cap at 100
    total_score = min(base_score, 100)
    
    return total_score, factors, trend_indicators, risk_probabilities, derived_metrics
