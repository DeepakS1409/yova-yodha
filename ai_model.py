import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from machine_data import create_training_data


FEATURES = [
    "temperature",
    "vibration",
    "operating_hours",
    "previous_failures",
]


def train_risk_model():
    data = create_training_data()

    X = data[FEATURES]
    y = data["breakdown"]

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_depth=5,
        min_samples_leaf=2,
    )

    model.fit(X, y)

    return model


def predict_breakdown_risk(
    temperature,
    vibration,
    operating_hours,
    previous_failures,
):
    """Return predicted breakdown probability as a percentage."""

    model = train_risk_model()

    sample = pd.DataFrame(
        [[
            temperature,
            vibration,
            operating_hours,
            previous_failures,
        ]],
        columns=FEATURES,
    )

    probability = model.predict_proba(sample)[0][1]

    return round(float(probability) * 100, 2)


def risk_label(risk):
    if risk < 30:
        return "Low"
    elif risk < 60:
        return "Medium"
    else:
        return "High"
