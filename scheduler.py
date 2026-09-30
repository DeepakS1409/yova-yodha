import itertools


def calculate_machine_plan(machines, target_production, grid_demand):
    """
    Finds the best machine combination based on:
    - Production target
    - Energy consumption
    - Grid demand
    - Breakdown risk
    """

    machine_names = list(machines.keys())

    best_plan = None
    best_score = float("inf")

    # Try every possible machine combination
    for r in range(1, len(machine_names) + 1):

        combinations = itertools.combinations(
            machine_names,
            r
        )

        for combination in combinations:

            # -----------------------------------------
            # Calculate total production
            # -----------------------------------------

            production = sum(
                machines[machine]["production"]
                for machine in combination
            )

            # -----------------------------------------
            # Calculate total energy
            # -----------------------------------------

            energy = sum(
                machines[machine]["energy"]
                for machine in combination
            )

            # -----------------------------------------
            # Calculate breakdown risk
            # -----------------------------------------

            risk = sum(
                machines[machine]["risk"]
                for machine in combination
            )

            # -----------------------------------------
            # Ignore plans that cannot meet target
            # -----------------------------------------

            if production < target_production:
                continue

            # -----------------------------------------
            # Grid-demand based energy penalty
            # -----------------------------------------

            if grid_demand == "Low":

                energy_weight = 1.0

            elif grid_demand == "Medium":

                energy_weight = 1.5

            else:

                energy_weight = 2.0

            # -----------------------------------------
            # Penalize unnecessary production
            # -----------------------------------------

            extra_production = (
                production - target_production
            )

            # -----------------------------------------
            # Final AI score
            # -----------------------------------------

            score = (
                energy * energy_weight
                + risk * 2
                + extra_production * 0.5
            )

            # -----------------------------------------
            # Select best plan
            # -----------------------------------------

            if score < best_score:

                best_score = score

                best_plan = {
                    "machines": combination,
                    "production": production,
                    "energy": energy,
                    "risk": risk,
                    "score": round(best_score, 2)
                }

    return best_plan