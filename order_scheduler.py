import itertools


def generate_all_combinations(machines):
    machine_names = list(machines.keys())
    combinations = []

    for r in range(1, len(machine_names) + 1):
        for combo in itertools.combinations(machine_names, r):

            production = sum(
                machines[m]["production"] for m in combo
            )

            energy = sum(
                machines[m]["energy"] for m in combo
            )

            base_risk = sum(
                machines[m]["risk"] for m in combo
            )

            combinations.append({
                "machines": combo,
                "production": production,
                "energy": energy,
                "risk": base_risk
            })

    return combinations


def calculate_machine_risk(plan, machine_risks):
    """
    Calculate average ML-predicted breakdown risk
    for the machines used in this plan.
    """

    if not machine_risks:
        return 0

    risks = [
        machine_risks.get(machine, 0)
        for machine in plan["machines"]
    ]

    if not risks:
        return 0

    return sum(risks) / len(risks)


def calculate_score(
    plan,
    required_per_hour,
    grid_demand,
    urgency,
    machine_risks=None
):

    if machine_risks is None:
        machine_risks = {}

    # Grid-aware energy weighting
    if grid_demand == "High":
        energy_weight = 3.0
    elif grid_demand == "Medium":
        energy_weight = 1.5
    else:
        energy_weight = 0.5

    # Production surplus
    surplus = max(
        0,
        plan["production"] - required_per_hour
    )

    # ML predicted breakdown risk
    ml_risk = calculate_machine_risk(
        plan,
        machine_risks
    )

    energy_score = (
        plan["energy"] * energy_weight
    )

    surplus_penalty = (
        surplus * 0.5
    )

    existing_risk_penalty = (
        plan["risk"] * 2
    )

    # New ML risk penalty
    ml_risk_penalty = (
        ml_risk * 1.5
    )

    # Deadline urgency
    urgency_bonus = (
        plan["production"] * urgency
    )

    total_score = (
        energy_score
        + surplus_penalty
        + existing_risk_penalty
        + ml_risk_penalty
        - urgency_bonus
    )

    return total_score


def generate_reason(
    selected_plan,
    required_per_hour,
    grid_demand,
    remaining_hours,
    machine_risks=None
):

    if machine_risks is None:
        machine_risks = {}

    selected_machines = selected_plan["machines"]

    selected_risks = [
        machine_risks.get(machine, 0)
        for machine in selected_machines
    ]

    average_ml_risk = (
        sum(selected_risks) / len(selected_risks)
        if selected_risks
        else 0
    )

    # High ML risk explanation
    if average_ml_risk >= 60:
        return (
            f"AI detected elevated machine breakdown risk "
            f"({average_ml_risk:.1f}%). "
            f"Scheduler selected a lower-risk production plan."
        )

    # High grid demand
    if grid_demand == "High":
        return (
            "High grid demand detected. "
            "AI prioritised energy-efficient machines "
            "while considering machine health risk."
        )

    # Deadline pressure
    if remaining_hours <= 2:
        return (
            "Deadline is close. AI prioritised sufficient "
            "production while considering machine risk."
        )

    # Medium grid demand
    if grid_demand == "Medium":
        return (
            "Medium grid demand. AI balanced production, "
            "energy consumption and machine breakdown risk."
        )

    # Extra production
    if selected_plan["production"] > required_per_hour + 5:
        return (
            "AI selected additional production capacity "
            "to maintain deadline safety."
        )

    return (
        "AI selected an energy-efficient and "
        "lower-risk production plan."
    )


def generate_schedule(
    machines,
    order_quantity,
    deadline_hours,
    grid_profile,
    machine_risks=None
):

    if machine_risks is None:
        machine_risks = {}

    combinations = generate_all_combinations(
        machines
    )

    remaining = order_quantity

    total_production = 0
    total_energy = 0

    schedule = []

    for hour in range(
        1,
        deadline_hours + 1
    ):

        if remaining <= 0:
            break

        remaining_hours = (
            deadline_hours - hour + 1
        )

        required_per_hour = (
            remaining / remaining_hours
        )

        grid_demand = grid_profile[
            hour - 1
        ]

        urgency = (
            1 / remaining_hours
        )

        valid_plans = []

        for plan in combinations:

            if (
                plan["production"]
                < required_per_hour
            ):
                continue

            score = calculate_score(
                plan,
                required_per_hour,
                grid_demand,
                urgency,
                machine_risks
            )

            plan_copy = plan.copy()

            plan_copy["ml_risk"] = round(
                calculate_machine_risk(
                    plan,
                    machine_risks
                ),
                2
            )

            plan_copy["score"] = score

            valid_plans.append(
                plan_copy
            )

        if not valid_plans:

            return {
                "completed": False,
                "schedule": schedule,
                "total_production": total_production,
                "total_energy": total_energy,
                "remaining": remaining,
                "reason": (
                    "Insufficient production capacity."
                )
            }

        # Lowest score = best plan
        valid_plans.sort(
            key=lambda x: x["score"]
        )

        best_plan = valid_plans[0]

        production = min(
            best_plan["production"],
            remaining
        )

        energy = best_plan["energy"]

        remaining -= production

        total_production += production
        total_energy += energy

        reason = generate_reason(
            best_plan,
            required_per_hour,
            grid_demand,
            remaining_hours,
            machine_risks
        )

        schedule.append({
            "hour": hour,
            "grid_demand": grid_demand,
            "machines": best_plan["machines"],
            "production": production,
            "energy": energy,
            "risk": best_plan["risk"],
            "ml_risk": best_plan["ml_risk"],
            "score": round(
                best_plan["score"],
                2
            ),
            "required_per_hour": round(
                required_per_hour,
                2
            ),
            "reason": reason,
            "remaining": max(
                0,
                remaining
            )
        })

    return {
        "completed": remaining <= 0,
        "schedule": schedule,
        "total_production": total_production,
        "total_energy": total_energy,
        "remaining": max(
            0,
            remaining
        )
    }