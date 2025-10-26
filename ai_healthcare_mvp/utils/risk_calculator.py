# utils/risk_calculator.py

import math
import datetime

def ai_health_risk_score(steps, pain_level, medicine_taken, sleep_hours=None, mood=None):
    """
    AI-based risk scoring function.
    This function intelligently evaluates a patient's condition using multiple parameters.
    """

    # 🩺 Step 1: Normalize data
    steps_score = 0
    if steps <= 1000:
        steps_score = 0.9
    elif steps <= 3000:
        steps_score = 0.7
    elif steps <= 5000:
        steps_score = 0.5
    elif steps <= 8000:
        steps_score = 0.3
    else:
        steps_score = 0.1  # Very active

    # Pain normalization (higher pain = higher risk)
    pain_score = pain_level / 10.0

    # Medicine logic — if not taken, add risk
    med_score = 0.3 if not medicine_taken else 0.1

    # Sleep and mood are optional — AI will adapt
    sleep_score = 0.0
    if sleep_hours is not None:
        if sleep_hours < 5:
            sleep_score = 0.6
        elif sleep_hours < 7:
            sleep_score = 0.3
        else:
            sleep_score = 0.1

    mood_score = 0.0
    if mood:
        mood = mood.lower()
        if mood in ["sad", "tired", "angry"]:
            mood_score = 0.5
        elif mood in ["neutral"]:
            mood_score = 0.3
        elif mood in ["happy", "energetic"]:
            mood_score = 0.1

    # 🧩 Step 2: Weighted AI combination
    # These weights can later be auto-learned by ML
    total_score = (
        0.35 * steps_score +
        0.25 * pain_score +
        0.15 * med_score +
        0.15 * sleep_score +
        0.10 * mood_score
    )

    # 🧠 Step 3: Apply nonlinear scaling (AI feel)
    risk_value = round(math.pow(total_score, 1.2) * 100, 2)

    # 🧾 Step 4: Categorize Risk Level
    if risk_value < 30:
        risk_level = "Low"
        ai_recommendation = "Patient is healthy and active. Maintain routine."
    elif risk_value < 60:
        risk_level = "Moderate"
        ai_recommendation = "Encourage regular walks and proper rest."
    else:
        risk_level = "High"
        ai_recommendation = "Monitor patient closely. Possible inflammation or fatigue."

    return {
        "risk_score": risk_value,
        "risk_level": risk_level,
        "ai_recommendation": ai_recommendation,
        "evaluated_on": datetime.datetime.now().isoformat()
    }

# ✅ Example test (you can remove this when integrating)
if __name__ == "__main__":
    result = ai_health_risk_score(steps=2500, pain_level=6, medicine_taken=False, sleep_hours=5, mood="tired")
    print(result)