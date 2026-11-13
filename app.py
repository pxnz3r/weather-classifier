"""
app.py - the weather classifier demo. Run it with:

    streamlit run app.py

Tabs:
    Overview       what the project is and how the two models decide,
    Classify       set a noon reading (or start from a real test day) and see
                   each model's verdict and why,
    How it decides what Naive Bayes learned and every rule of the tree,
    Results        the saved tables and figures from main.py.
It needs the saved models, so run `python main.py` once first.
"""

import os

import pandas as pd
import streamlit as st

from pxlab.app import (
    class_probabilities,
    input_form,
    probability_bar,
    setup_page,
    show_figure,
    show_markdown_file,
    show_results_tabs,
    signed_bars,
)
from pxlab.common import MODELS_FOLDER, OUTPUTS_FOLDER
from pxlab.tabular.explain import decision_path
from pxlab.tabular.train import load_models, models_are_saved
from weather_classifier.explain import reading_evidence
from weather_classifier.report import FOLDER, results_sections
from weather_classifier.spec import WEATHER_SPEC

MODEL_FOLDER = os.path.join(MODELS_FOLDER, FOLDER)
TYPICAL = "Typical noon"
TEST_EXAMPLES = 20


@st.cache_resource
def load_everything():
    """
    Load the saved models and the test days (cached, so this happens once).

    Returns:
        (model_info, models, test table)
    """
    model_info, models = load_models(MODEL_FOLDER)
    test = pd.read_csv(os.path.join(MODEL_FOLDER, "test.csv"))
    return model_info, models, test


def show_classify_page(model_info, models, test):
    """
    The Classify tab: the reading on the left, the verdict and the reasons
    on the right.

    Inputs:
        model_info, models: from load_models().
        test: the saved test days.
    Returns:
        Nothing.
    """
    spec = WEATHER_SPEC
    inputs = list(spec["numeric"])
    # An even spread of test days across the three test years.
    shown = test.iloc[:: max(len(test) // TEST_EXAMPLES, 1)].head(TEST_EXAMPLES)
    left, right = st.columns([3, 2], gap="large")
    with left:
        picker, model_box = st.columns(2)
        test_options = [f"{row.date} (was {row.condition})" for row in shown.itertuples()]
        start = picker.selectbox(
            "Start from",
            [TYPICAL, *test_options],
            help="The typical reading has the training medians. Test days are real noon readings "
            "from 2022 to 2024, after every day the models learned from.",
        )
        model_name = model_box.selectbox("Model", list(models), index=list(models).index("Naive Bayes"))
        if start == TYPICAL:
            start_values = model_info["default_values"]
        else:
            start_values = shown.iloc[test_options.index(start)][inputs].to_dict()
        reading = input_form(spec, model_info, start_values, key_prefix=f"{start}-")

    pipeline = models[model_name]
    chances = class_probabilities(pipeline, reading)
    with right:
        st.subheader(chances.index[0].capitalize(), anchor=False)
        for condition, chance in chances.items():
            st.markdown(f"{condition.capitalize()} **{chance:.0%}**")
            probability_bar(float(chance))
        if model_name == "Naive Bayes":
            predicted, runner_up, evidence = reading_evidence(pipeline, reading, spec)
            st.subheader(f"Why {predicted}, not {runner_up}", anchor=False)
            st.caption(f"Evidence per input: right favours {predicted}, left favours {runner_up}.")
            signed_bars(evidence)
        elif model_name == "Decision Tree":
            st.subheader("The questions the tree asked", anchor=False)
            steps = decision_path(pipeline, reading, spec)
            st.markdown("\n".join(f"{number}. {step}" for number, step in enumerate(steps, start=1)))
        else:
            st.caption("Pick Naive Bayes or the Decision Tree to see why.")


def show_decides_page(model_info):
    """
    The How it decides tab: Naive Bayes's bell curves and the tree's rules.

    Input:
        model_info: from load_models().
    Returns:
        Nothing.
    """
    st.markdown(
        "Naive Bayes keeps one bell curve per input and weather type. For a new reading it checks how high "
        "each curve is at that value, multiplies the heights per type and picks the highest product. "
        "Where the curves overlap, the input can't tell the types apart."
    )
    show_figure(f"{FOLDER}/class_curves.png")
    best = model_info["best_params"]["Decision Tree"]
    st.subheader("The Decision Tree's rules", anchor=False)
    st.markdown(
        f"Cross-validation chose a tree of depth {best['max_depth']} with at least {best['min_samples_leaf']} "
        f"training days per leaf, giving {model_info['tree_leaves']} leaves."
    )
    with open(os.path.join(OUTPUTS_FOLDER, FOLDER, "tree_rules.txt"), encoding="utf-8") as file:
        st.code(file.read(), language=None)


def main():
    """
    Build the page.

    Returns:
        Nothing.
    """
    setup_page("Weather classifier")
    if not models_are_saved(MODEL_FOLDER):
        st.error("No saved models yet. Run `python main.py` first.")
        st.stop()
    model_info, models, test = load_everything()

    overview, classify, decides, results = st.tabs(["Overview", "Classify", "How it decides", "Results"])
    with overview:
        show_markdown_file("app_overview.md")
    with classify:
        show_classify_page(model_info, models, test)
    with decides:
        show_decides_page(model_info)
    with results:
        show_results_tabs(results_sections())


main()
