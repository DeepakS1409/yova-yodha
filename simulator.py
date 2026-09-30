import random


class FactorySimulator:

    def __init__(self, machines):
        self.machines = machines

        self.total_production = 0
        self.total_energy = 0
        self.time_elapsed = 0

    def run_step(self, active_machines, duration=1):
        """
        Simulates the factory for a given duration.

        duration:
            Number of simulated hours.
        """

        production = 0
        energy = 0

        for machine_name in active_machines:

            machine = self.machines[machine_name]

            # Small random variation to make
            # simulation more realistic.
            efficiency = random.uniform(0.90, 1.05)

            machine_production = (
                machine["production"]
                * efficiency
                * duration
            )

            machine_energy = (
                machine["energy"]
                * duration
            )

            production += machine_production
            energy += machine_energy

        self.total_production += production
        self.total_energy += energy
        self.time_elapsed += duration

        return {
            "production": round(production, 2),
            "energy": round(energy, 2),
            "time": self.time_elapsed,
            "total_production": round(
                self.total_production,
                2
            ),
            "total_energy": round(
                self.total_energy,
                2
            )
        }

    def reset(self):

        self.total_production = 0
        self.total_energy = 0
        self.time_elapsed = 0