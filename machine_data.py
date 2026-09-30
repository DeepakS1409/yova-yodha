import pandas as pd


def create_training_data():
    """
    Synthetic machine-history data for FactoryMind AI.

    Higher temperature, vibration, operating hours and previous failures
    generally increase breakdown probability.
    """

    data = [
        # Healthy / low-risk machines
        [55, 1.0, 80, 0, 0],
        [57, 1.1, 120, 0, 0],
        [59, 1.3, 160, 0, 0],
        [60, 1.4, 200, 0, 0],
        [61, 1.5, 240, 0, 0],
        [62, 1.6, 280, 0, 0],
        [63, 1.7, 320, 0, 0],
        [64, 1.8, 350, 1, 0],

        # Early warning / medium-low risk
        [65, 2.0, 380, 0, 0],
        [66, 2.1, 420, 1, 0],
        [67, 2.2, 450, 1, 0],
        [68, 2.3, 480, 1, 0],
        [69, 2.4, 500, 1, 0],
        [70, 2.5, 530, 1, 0],
        [70, 2.6, 560, 2, 0],
        [71, 2.7, 580, 2, 0],

        # Warning / medium-high risk
        [72, 2.8, 600, 2, 0],
        [73, 3.0, 630, 2, 0],
        [74, 3.1, 650, 2, 1],
        [75, 3.2, 680, 2, 1],
        [76, 3.3, 700, 3, 0],
        [77, 3.4, 720, 3, 1],
        [78, 3.5, 740, 3, 1],
        [79, 3.6, 760, 3, 1],

        # High-risk machines
        [80, 3.8, 780, 3, 1],
        [81, 3.9, 800, 3, 1],
        [82, 4.0, 820, 4, 1],
        [83, 4.1, 840, 4, 1],
        [84, 4.2, 860, 4, 1],
        [85, 4.3, 880, 4, 1],
        [86, 4.4, 900, 5, 1],
        [88, 4.6, 950, 5, 1],

        # A few intentionally mixed cases so the model learns uncertainty
        [68, 2.5, 520, 1, 1],
        [72, 2.9, 610, 2, 1],
        [76, 3.2, 690, 2, 0],
        [79, 3.7, 770, 3, 0],
        [74, 3.0, 640, 1, 0],
        [81, 4.0, 830, 4, 0],
    ]

    return pd.DataFrame(
        data,
        columns=[
            "temperature",
            "vibration",
            "operating_hours",
            "previous_failures",
            "breakdown",
        ],
    )
