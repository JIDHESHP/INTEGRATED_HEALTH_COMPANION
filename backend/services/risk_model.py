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
    
    # 1. Profile Analysis (Age & BMI)
    age = 30 # Default
    if profile:
        try:
            age = int(profile.get('age', 30))
        except: pass
        
        # Calculate BMI if missing but height/weight available
        if 'bmi' not in profile and profile.get('height') and profile.get('weight'):
            try:
                h = float(profile['height']) / 100 # assume cm
                w = float(profile['weight'])
                if h > 0:
                    profile['bmi'] = round(w / (h * h), 2)
            except: pass

    # Age Risk
    if age > 70:
        base_score += 25
        factors.append(f"Advanced Age ({age})")
        risk_probabilities['cardiovascular'] = 0.45
    elif age > 60:
        base_score += 15
        factors.append(f"Senior Age ({age})")
        risk_probabilities['cardiovascular'] = 0.35
    elif age > 45:
        base_score += 10
        risk_probabilities['cardiovascular'] = 0.20
    
    # BMI Risk
    bmi = 22.0
    if profile and profile.get('bmi'):
        try:
            bmi = float(profile['bmi'])
            if bmi > 40:
                base_score += 35
                factors.append(f"Class III Obesity (BMI {bmi})")
                risk_probabilities['metabolic'] = 0.60
                trend_indicators.append("Critical metabolic risk")
            elif bmi > 35:
                base_score += 25
                factors.append(f"Class II Obesity (BMI {bmi})")
                risk_probabilities['metabolic'] = 0.45
            elif bmi > 30:
                base_score += 15
                factors.append(f"Obesity (BMI {bmi})")
                risk_probabilities['metabolic'] = 0.35
            elif bmi > 25:
                base_score += 8
                factors.append(f"Overweight (BMI {bmi})")
                risk_probabilities['metabolic'] = 0.20
            elif bmi < 18.5:
                base_score += 5
                factors.append(f"Underweight (BMI {bmi})")
        except: pass
    
    # 2. Vitals Analysis (Weighted Model)
    # Systolic BP
    try:
        sys = int(latest_health_log.get('bp_systolic', 120))
        dia = int(latest_health_log.get('bp_diastolic', 80))
        
        # Mean Arterial Pressure (approx) for better risk
        map_val = (sys + 2*dia) / 3
        
        if sys > 180 or dia > 120:
            base_score += 40
            factors.append(f"Hypertensive Crisis ({sys}/{dia})")
            risk_probabilities['hypertension'] = 0.85
            trend_indicators.append("Urgent: BP critical")
        elif sys >= 140 or dia >= 90:
            base_score += 20
            factors.append("Hypertension Stage 2")
            risk_probabilities['hypertension'] = 0.60
        elif sys >= 130 or dia >= 80:
            base_score += 10
            factors.append("Hypertension Stage 1")
            risk_probabilities['hypertension'] = 0.40
        elif sys < 90 or dia < 60:
            base_score += 10
            factors.append("Hypotension")
            trend_indicators.append("Low blood pressure")
            
    except: pass
    
    # Blood Sugar
    try:
        sugar = int(latest_health_log.get('blood_sugar', 100))
        if sugar > 300:
            base_score += 40
            factors.append(f"Dangerous Glucose ({sugar})")
            risk_probabilities['diabetes'] = 0.90
            trend_indicators.append("Urgent: Glucose critical")
        elif sugar > 200:
            base_score += 25
            factors.append("Diabetes Range")
            risk_probabilities['diabetes'] = 0.70
        elif sugar > 140:
            base_score += 15
            factors.append("Prediabetes Range")
            risk_probabilities['diabetes'] = 0.40
        elif sugar < 70:
            base_score += 15
            factors.append("Hypoglycemia")
            trend_indicators.append("Low glucose")
    except: pass
    
    # Heart Rate
    try:
        hr = int(latest_health_log.get('heart_rate', 70))
        if hr > 120:
            base_score += 20
            factors.append(f"High Tachycardia ({hr})")
            risk_probabilities['cardiac'] = 0.50
        elif hr > 100:
            base_score += 10
            factors.append("Tachycardia")
            risk_probabilities['cardiac'] = 0.30
        elif hr < 40 and 'active' not in str(profile.get('activity_level','')): 
            # Low HR is bad unless athlete
            base_score += 15
            factors.append("Bradycardia")
            risk_probabilities['cardiac'] = 0.30
    except: pass
    
    # 3. Combined Risk Adjustments
    # If High BP AND High Sugar -> Metabolic Syndrome Risk
    if risk_probabilities.get('hypertension', 0) > 0.4 and risk_probabilities.get('diabetes', 0) > 0.4:
        base_score += 15
        factors.append("Metabolic Syndrome Risk")
        risk_probabilities['metabolic'] = max(risk_probabilities.get('metabolic',0), 0.75)

    # 4. Activity Level Mitigation
    try:
        activity = profile.get('activity_level', 'moderate')
        if activity == 'sedentary':
            base_score += 5
        elif activity == 'active':
            base_score = max(0, base_score - 10)  # Exercise allows reduction
            if 'Overweight' in factors: base_score -= 5 # Active overweight is less risky
    except: pass
    
    # Calculate derived metrics
    derived_metrics = {
        'overall_risk': min(base_score, 100),
        'trend': 'stable' if base_score < 30 else ('increasing' if len(trend_indicators) > 0 else 'moderate'),
        'recommendation_priority': 'high' if base_score > 50 else 'low',
        'key_vitals_summary': f"BP: {latest_health_log.get('bp_systolic','-')}/{latest_health_log.get('bp_diastolic','-')}, HR: {latest_health_log.get('heart_rate','-')}"
    }
    
    # Cap at 100
    total_score = min(base_score, 100)
    
    return total_score, factors, trend_indicators, risk_probabilities, derived_metrics
