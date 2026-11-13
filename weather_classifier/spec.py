"""
spec.py - the weather dataset and the models trained on it.

The pxlab engine reads this dictionary: which column to predict, which
columns are inputs, readable names, and the models with the settings that
grid search tries.

The brief names humidity, temperature and wind. Air pressure and how it
changed over the morning are added because forecasters lean on them; the
study also trains on the brief's three inputs alone to show what they add.
"""

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

from pxlab.common import RANDOM_STATE

BRIEF_INPUTS = ["temperature", "humidity", "wind_speed"]
EXTRA_INPUTS = ["pressure", "pressure_change"]

WEATHER_SPEC = {
    "name": "London weather at noon",
    "folder": "weather",
    "task": "classification",
    "target": "condition",
    "positive_class": None,
    "numeric": BRIEF_INPUTS + EXTRA_INPUTS,
    "categorical": [],
    "labels": {
        "temperature": "Temperature (°C)",
        "humidity": "Relative humidity (%)",
        "wind_speed": "Wind speed (km/h)",
        "pressure": "Air pressure (hPa)",
        "pressure_change": "Pressure change since 6 am (hPa)",
        "condition": "Weather",
    },
    "help": {
        "humidity": "How close the air is to holding all the water vapour it can, at this temperature.",
        "pressure": "Sea-level air pressure. Low pressure usually brings cloud and rain.",
        "pressure_change": "Noon pressure minus 6 am pressure. Falling pressure is a classic sign of rain coming.",
    },
    # Rows are in date order: the test set is the last fifth, so every test
    # day comes after every training day.
    "time_order": True,
    "test_size": 0.2,
    "scoring": "f1_macro",
    "models": {
        "Decision Tree": {
            "estimator": DecisionTreeClassifier(random_state=RANDOM_STATE),
            "grid": {
                "max_depth": [3, 4, 5, 6, 8],
                "min_samples_leaf": [10, 30, 60],
                "class_weight": [None, "balanced"],
            },
            "scale": False,
            "role": "Main",
        },
        "Naive Bayes": {
            # Gaussian Naive Bayes: a bell curve per input and class. Equal
            # priors stop it from answering "cloudy" whenever it is unsure.
            "estimator": GaussianNB(),
            "grid": {"priors": [None, [1 / 3, 1 / 3, 1 / 3]]},
            "scale": False,
            "role": "Main",
        },
        "Random Forest": {
            "estimator": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE, n_jobs=1),
            "grid": {"min_samples_leaf": [5, 20], "class_weight": [None, "balanced"]},
            "scale": False,
            "role": "Benchmark beyond the course",
        },
        "Always cloudy": {
            "estimator": DummyClassifier(strategy="most_frequent"),
            "grid": {},
            "scale": False,
            "role": "Baseline",
        },
    },
}


def brief_only_spec():
    """
    The same SPEC with only the brief's three inputs and the two main
    models, to measure what pressure adds.

    Returns:
        A new SPEC dictionary.
    """
    spec = dict(WEATHER_SPEC)
    spec["numeric"] = list(BRIEF_INPUTS)
    spec["models"] = {name: WEATHER_SPEC["models"][name] for name in ["Decision Tree", "Naive Bayes"]}
    return spec
