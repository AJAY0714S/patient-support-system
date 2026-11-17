"""
Educational Bayesian Network:
Disease -> observed symptoms.
Medical-history evidence adjusts the prior probability of selected conditions.
This is a transparent demonstration model with illustrative parameters, NOT a
clinically validated model. Do not use it to diagnose or make treatment decisions.
"""
import math

SYMPTOMS = {
    "fever":"Fever", "cough":"Cough", "headache":"Headache",
    "sore_throat":"Sore throat", "fatigue":"Fatigue", "body_ache":"Body ache",
    "nausea":"Nausea", "vomiting":"Vomiting", "diarrhea":"Diarrhea",
    "runny_nose":"Runny nose", "shortness_of_breath":"Shortness of breath",
    "chest_pain":"Chest pain"
}

# P(symptom present | condition), illustrative values only.
MODEL = {
    "Common cold": {
        "prior": .28, "likelihood": {"runny_nose":.80,"sore_throat":.65,"cough":.60,"fever":.20,"headache":.25,"fatigue":.35,"body_ache":.20}
    },
    "Influenza-like illness": {
        "prior": .20, "likelihood": {"fever":.85,"cough":.75,"headache":.65,"fatigue":.80,"body_ache":.80,"sore_throat":.45}
    },
    "Gastrointestinal infection": {
        "prior": .13, "likelihood": {"nausea":.70,"vomiting":.65,"diarrhea":.80,"fever":.35,"fatigue":.40,"body_ache":.25}
    },
    "Migraine-like headache": {
        "prior": .12, "likelihood": {"headache":.90,"nausea":.55,"vomiting":.30,"fatigue":.35}
    },
    "Asthma-related symptoms": {
        "prior": .10, "likelihood": {"cough":.55,"shortness_of_breath":.85,"chest_pain":.20,"fatigue":.35}
    },
    "Other / undetermined": {
        "prior": .17, "likelihood": {}
    }
}

URGENT = {"chest_pain", "shortness_of_breath"}

def _history_multiplier(condition, history):
    multiplier = 1.0
    if condition == "Asthma-related symptoms" and history.get("asthma"):
        multiplier *= 2.2
    if history.get("diabetes") and condition == "Other / undetermined":
        multiplier *= 1.15
    if history.get("heart_disease") and condition == "Other / undetermined":
        multiplier *= 1.2
    if history.get("age_group") == "senior" and condition == "Other / undetermined":
        multiplier *= 1.15
    return multiplier

def predict(symptoms, history=None):
    history = history or {}
    selected = [s for s in symptoms if s in SYMPTOMS]
    scores = {}
    for condition, spec in MODEL.items():
        score = spec["prior"] * _history_multiplier(condition, history)
        likelihoods = spec["likelihood"]
        for symptom in selected:
            p = likelihoods.get(symptom, 0.12)
            # Bernoulli evidence for present symptoms; clamp to avoid zero.
            score *= max(p, 0.015)
        scores[condition] = score
    total = sum(scores.values()) or 1.0
    ranked = sorted(
        [{"condition": name, "probability": round(value / total * 100, 1)}
         for name, value in scores.items()],
        key=lambda item: item["probability"], reverse=True
    )
    urgent = bool(set(selected) & URGENT)
    return {
        "predictions": ranked,
        "urgent_warning": urgent,
        "warning": (
            "Chest pain or difficulty breathing can be urgent. Seek emergency medical care now; "
            "do not rely on this tool."
            if urgent else
            "This educational estimate is not a diagnosis. Consult a qualified healthcare professional."
        ),
        "model_note": "Illustrative Bayesian Network parameters; not clinically validated."
    }
