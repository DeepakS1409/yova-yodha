from machine_data import create_training_data
from machine_health import get_numeric_machine_risks
from order_scheduler import generate_schedule


machines = {
    "M1": {
        "production": 20,
        "energy": 30,
        "risk": 5
    },
    "M2": {
        "production": 50,
        "energy": 90,
        "risk": 10
    },
    "M3": {
        "production": 25,
        "energy": 35,
        "risk": 7
    }
}


# Get ML-predicted breakdown risks
machine_risks = get_numeric_machine_risks()

print("FactoryMind AI - ML Scheduler Test")
print("----------------------------------")

print("\nMachine Risks:")

for machine, risk in machine_risks.items():
    print(f"{machine}: {risk}%")

# Production order
order_quantity = 300
deadline_hours = 8

# Simulated grid conditions
grid_profile = [
    "Low",
    "Low",
    "Medium",
    "High",
    "High",
    "Medium",
    "Low",
    "Low"
]

# Generate AI schedule
result = generate_schedule(
    machines=machines,
    order_quantity=order_quantity,
    deadline_hours=deadline_hours,
    grid_profile=grid_profile,
    machine_risks=machine_risks
)

print("\nAI Production Schedule")
print("----------------------")

for item in result["schedule"]:

    print(
        f"Hour {item['hour']} | "
        f"Grid: {item['grid_demand']} | "
        f"Machines: {item['machines']} | "
        f"Production: {item['production']} | "
        f"Energy: {item['energy']} | "
        f"ML Risk: {item['ml_risk']}%"
    )

    print(
        f"  Reason: {item['reason']}"
    )

print("\nFinal Result")
print("------------")
print(
    f"Completed: {result['completed']}"
)
print(
    f"Total Production: {result['total_production']}"
)
print(
    f"Total Energy: {result['total_energy']}"
)
print(
    f"Remaining: {result['remaining']}"
)