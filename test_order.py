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


# Grid demand for each hour
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


result = generate_schedule(
    machines,
    order_quantity=300,
    deadline_hours=8,
    grid_profile=grid_profile
)


print("\nORDER STATUS")
print("--------------------")

print(
    "Completed:",
    result["completed"]
)

print(
    "Total Production:",
    result["total_production"]
)

print(
    "Total Energy:",
    result["total_energy"]
)

print(
    "Remaining:",
    result["remaining"]
)


print("\nHOURLY AI SCHEDULE")
print("--------------------")


for hour in result["schedule"]:

    print(
        f"\nHour {hour['hour']}"
    )

    print(
        f"Grid Demand: "
        f"{hour['grid_demand']}"
    )

    print(
        f"Machines: "
        f"{' + '.join(hour['machines'])}"
    )

    print(
        f"Production: "
        f"{hour['production']}"
    )

    print(
        f"Energy: "
        f"{hour['energy']} kWh"
    )

    print(
        f"Required/Hour: "
        f"{hour['required_per_hour']}"
    )

    print(
        f"Remaining: "
        f"{hour['remaining']}"
    )

    print(
        f"AI Reason: "
        f"{hour['reason']}"
    )