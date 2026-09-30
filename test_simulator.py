from simulator import FactorySimulator


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


factory = FactorySimulator(machines)


result = factory.run_step(
    ["M1", "M3"],
    duration=1
)


print(result)