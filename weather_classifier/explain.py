"""
explain.py - what Naive Bayes learned about the weather, beyond what pxlab
already provides (tree rules and decision paths).

    plot_class_curves: the bell curve Naive Bayes keeps for every input and
        weather type. Where the curves sit apart, the input tells the
        weather types apart.
    reading_evidence: for one reading, how much each input favours the
        predicted weather over the runner-up.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pxlab.common import save_figure
from pxlab.tabular.data import label_for

COLOURS = {"sunny": "#E1A33B", "cloudy": "#8C8C8C", "rainy": "#3B6FB6"}


def plot_class_curves(pipeline, spec, filename):
    """
    One panel per input with Naive Bayes's bell curve for each weather
    type: centred on the type's average, as wide as its spread.

    Inputs:
        pipeline: the fitted Naive Bayes pipeline (inputs not scaled).
        spec: the project SPEC.
        filename: the image file name.
    Returns:
        The saved path.
    """
    model = pipeline.named_steps["model"]
    names = list(pipeline.named_steps["preprocess"].get_feature_names_out())
    figure, axes = plt.subplots(1, len(names), figsize=(3.4 * len(names), 3.4))
    for axis, column in zip(axes, names):
        index = names.index(column)
        means = model.theta_[:, index]
        spreads = np.sqrt(model.var_[:, index])
        x = np.linspace((means - 3 * spreads).min(), (means + 3 * spreads).max(), 300)
        for class_index, condition in enumerate(model.classes_):
            curve = np.exp(-((x - means[class_index]) ** 2) / (2 * spreads[class_index] ** 2))
            curve /= spreads[class_index] * np.sqrt(2 * np.pi)
            axis.plot(x, curve, color=COLOURS.get(condition), label=condition, linewidth=2)
            axis.fill_between(x, curve, color=COLOURS.get(condition), alpha=0.12)
        axis.set_title(label_for(spec, column), fontsize=10)
        axis.set_yticks([])
    axes[0].legend()
    figure.suptitle("What Naive Bayes learned: one bell curve per input and weather type")
    return save_figure(figure, filename)


def reading_evidence(pipeline, reading, spec):
    """
    How much each input favours the predicted weather over the runner-up:

        evidence = log P(value | predicted) - log P(value | runner-up)

    Naive Bayes adds these up (plus the prior) to decide.

    Inputs:
        pipeline: the fitted Naive Bayes pipeline.
        reading: a one-row DataFrame with the raw input columns.
        spec: the project SPEC.
    Returns:
        (predicted, runner_up, Series readable input name -> evidence).
    """
    model = pipeline.named_steps["model"]
    values = pipeline.named_steps["preprocess"].transform(reading)[0]
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    order = np.argsort(pipeline.predict_proba(reading)[0])[::-1]
    first, second = order[0], order[1]
    log_density = -0.5 * np.log(2 * np.pi * model.var_) - (values - model.theta_) ** 2 / (2 * model.var_)
    evidence = pd.Series(log_density[first] - log_density[second], index=[label_for(spec, n) for n in names])
    evidence = evidence.reindex(evidence.abs().sort_values(ascending=False).index)
    return model.classes_[first], model.classes_[second], evidence
