def calculate_plan_metrics(machines, selected_machines):
    """
    Calculate production and energy for a machine combination.
    """

    production = 0
    energy = 0
    risk = 0

    for machine_name in selected_machines:

        machine = machines[machine_name]

        production += machine["production"]
        energy += machine["energy"]
        risk += machine["risk"]

    return {
        "production": production,
        "energy": energy,
        "risk": risk,
        "machine_count": len(selected_machines)
    }


def calculate_savings(current_energy, ai_energy):
    """
    Calculate energy savings percentage.
    """

    if current_energy == 0:
        return 0

    savings = (
        (current_energy - ai_energy)
        / current_energy
    ) * 100

    return round(savings, 2)