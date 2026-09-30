from ai_model import predict_breakdown_risk, risk_label


test_cases = [
    {
        "name": "Healthy Machine",
        "temperature": 60,
        "vibration": 1.4,
        "operating_hours": 150,
        "previous_failures": 0,
    },
    {
        "name": "Moderate Machine",
        "temperature": 70,
        "vibration": 2.6,
        "operating_hours": 560,
        "previous_failures": 2,
    },
    {
        "name": "High-Risk Machine",
        "temperature": 82,
        "vibration": 4.0,
        "operating_hours": 820,
        "previous_failures": 4,
    },
]


print("FactoryMind AI - ML Risk Predictor")
print("-----------------------------------")

for machine in test_cases:
    risk = predict_breakdown_risk(
        machine["temperature"],
        machine["vibration"],
        machine["operating_hours"],
        machine["previous_failures"],
    )

    print(
        f"{machine['name']}: "
        f"{risk}% predicted breakdown risk "
        f"({risk_label(risk)})"
    )
