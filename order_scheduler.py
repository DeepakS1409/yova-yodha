import itertools


def generate_all_combinations(machines):

    machine_names = list(machines.keys())
    combinations = []

    for r in range(1, len(machine_names) + 1):

        for combo in itertools.combinations(machine_names, r):

            production = sum(
                machines[m]["production"]
                for m in combo
            )

            energy = sum(
                machines[m]["energy"]
                for m in combo
            )

            risk = sum(
                machines[m]["risk"]
                for m in combo
            )

            combinations.append({
                "machines": combo,
                "production": production,
                "energy": energy,
                "risk": risk
            })

    return combinations


def calculate_score(
    plan,
    required_per_hour,
    grid_demand,
    urgency
):

    if grid_demand == "High":
        energy_weight = 3.0

    elif grid_demand == "Medium":
        energy_weight = 1.5

    else:
        energy_weight = 0.5

    surplus = max(
        0,
        plan["production"] - required_per_hour
    )

    energy_score = (
        plan["energy"] * energy_weight
    )

    surplus_penalty = (
        surplus * 0.5
    )

    risk_penalty = (
        plan["risk"] * 2
    )

    urgency_bonus = (
        plan["production"] * urgency
    )

    return (
        energy_score
        + surplus_penalty
        + risk_penalty
        - urgency_bonus
    )


def generate_reason(
    selected_plan,
    required_per_hour,
    grid_demand,
    remaining_hours
):

    production = selected_plan["production"]
    energy = selected_plan["energy"]

    if production > required_per_hour + 5:

        if grid_demand == "High":
            return (
                "High grid demand, but additional "
                "production capacity is required "
                "to stay within the deadline."
            )

        return (
            "Selected extra capacity to maintain "
            "deadline safety."
        )

    if grid_demand == "High":

        return (
            "High grid demand detected. "
            "AI selected the lowest-energy plan "
            "that can satisfy the required production."
        )

    if remaining_hours <= 2:

        return (
            "Deadline is close. "
            "AI prioritised sufficient production "
            "to complete the remaining order."
        )

    if grid_demand == "Medium":

        return (
            "Medium grid demand. "
            "AI balanced production and energy use."
        )

    return (
        "Low grid demand. "
        "AI selected an energy-efficient "
        "production plan."
    )


def generate_schedule(
    machines,
    order_quantity,
    deadline_hours,
    grid_profile
):

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
                urgency
            )

            plan_copy = plan.copy()

            plan_copy["score"] = score

            valid_plans.append(
                plan_copy
            )

        if not valid_plans:

            return {
                "completed": False,
                "schedule": schedule,
                "total_production":
                    total_production,
                "total_energy":
                    total_energy,
                "remaining":
                    remaining,
                "reason":
                    "Insufficient production capacity."
            }

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
            remaining_hours
        )

        schedule.append({

            "hour": hour,

            "grid_demand":
                grid_demand,

            "machines":
                best_plan["machines"],

            "production":
                production,

            "energy":
                energy,

            "risk":
                best_plan["risk"],

            "score":
                round(
                    best_plan["score"],
                    2
                ),

            "required_per_hour":
                round(
                    required_per_hour,
                    2
                ),

            "reason":
                reason,

            "remaining":
                max(
                    0,
                    remaining
                )
        })

    return {

        "completed":
            remaining <= 0,

        "schedule":
            schedule,

        "total_production":
            total_production,

        "total_energy":
            total_energy,

        "remaining":
            max(
                0,
                remaining
            )
    }