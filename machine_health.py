from ai_model import predict_breakdown_risk, risk_label

machine_health = {
    "M1": {
        "temperature": 61,
        "vibration": 1.5,
        "operating_hours": 240,
        "previous_failures": 0,
    },
    "M2": {
        "temperature": 75,
        "vibration": 3.2,
        "operating_hours": 680,
        "previous_failures": 2,
    },
    "M3": {
        "temperature": 64,
        "vibration": 1.8,
        "operating_hours": 350,
        "previous_failures": 1,
    },
}


def get_machine_risks():
    results = {}

    for machine_name, health in machine_health.items():
        risk = predict_breakdown_risk(
            temperature=health["temperature"],
            vibration=health["vibration"],
            operating_hours=health["operating_hours"],
            previous_failures=health["previous_failures"],
        )

        results[machine_name] = {
            "risk": risk,
            "label": risk_label(risk),
        }

    return results


def get_numeric_machine_risks():
    results = get_machine_risks()

    return {
        machine: data["risk"]
        for machine, data in results.items()
    }


if __name__ == "__main__":
    print("FactoryMind AI - Machine Health Monitor")
    print("---------------------------------------")

    results = get_machine_risks()

    for machine, data in results.items():
        health = machine_health[machine]

        print(
            f"{machine}: "
            f"{data['risk']}% risk "
            f"({data['label']})"
        )

        print(
            f"  Temperature: {health['temperature']}°C | "
            f"Vibration: {health['vibration']} | "
            f"Operating Hours: {health['operating_hours']} | "
            f"Previous Failures: {health['previous_failures']}"
        )
