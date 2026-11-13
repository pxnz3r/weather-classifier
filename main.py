"""
main.py - run the whole weather classification study with one command:

    python main.py

It:
    1. downloads (once) 15 years of hourly London weather and keeps the
       noon reading of each day,
    2. keeps the last fifth of the days (the most recent) as unseen test days,
    3. tunes a Decision Tree and Naive Bayes with time-ordered 5-fold
       cross-validation, plus a Random Forest benchmark and an "always
       cloudy" baseline,
    4. scores them on the test days and draws confusion matrices,
    5. compares the brief's three inputs with all five,
    6. draws what Naive Bayes learned and writes out the tree's rules,
    7. measures which inputs matter and lists the mistakes,
    8. saves the models for the app and writes docs/results.md.
Figures and tables go to outputs/weather/, models to models/weather/.
"""

import os

import pandas as pd

from pxlab.common import MODELS_FOLDER, save_table, set_plot_style, write_results_doc
from pxlab.tabular.data import (
    check_columns,
    input_summary,
    plot_correlations,
    plot_pairs,
    plot_target,
    quality_report,
    split_data,
)
from pxlab.tabular.evaluate import comparison_table, plot_confusion_matrices, test_scores, wrong_predictions
from pxlab.tabular.explain import permutation_importance_table, plot_permutation_importance, tree_rules
from pxlab.tabular.train import best_model_name, save_models, train_models
from weather_classifier.data import load_weather
from weather_classifier.explain import plot_class_curves
from weather_classifier.report import FOLDER, results_sections
from weather_classifier.spec import WEATHER_SPEC, brief_only_spec


def input_comparison(results, brief_results, test_features, test_target, spec):
    """
    Test macro F1 of the main models with the brief's three inputs and with
    all five.

    Inputs:
        results: models trained on all five inputs.
        brief_results: models trained on the brief's three.
        test_features, test_target: the test days.
        spec: the project SPEC.
    Returns:
        A DataFrame: one row per model.
    """
    rows = []
    for model_name, brief in brief_results.items():
        rows.append(
            {
                "Model": model_name,
                "Temperature, humidity, wind": test_scores(brief["pipeline"], test_features, test_target, spec)["F1"],
                "Plus pressure and its change": test_scores(
                    results[model_name]["pipeline"], test_features, test_target, spec
                )["F1"],
            }
        )
    return pd.DataFrame(rows).round(3)


def main():
    """
    The full study.

    Returns:
        Nothing.
    """
    spec = WEATHER_SPEC
    set_plot_style()
    data = load_weather()
    check_columns(data, spec)
    quality_report(data, spec, f"{FOLDER}/data_quality.csv")
    plot_target(data, spec, f"{FOLDER}/target.png")
    plot_pairs(data.sample(1500, random_state=42), spec, f"{FOLDER}/pairs.png")
    plot_correlations(data, spec, f"{FOLDER}/correlations.png")

    train_features, test_features, train_target, test_target = split_data(data, spec)
    test_dates = data.loc[test_features.index, "date"]
    print(
        f"  Training days {data['date'].iloc[0]} to {data.loc[train_features.index[-1], 'date']}, "
        f"test days {test_dates.iloc[0]} to {test_dates.iloc[-1]}"
    )
    model_folder = os.path.join(MODELS_FOLDER, FOLDER)
    os.makedirs(model_folder, exist_ok=True)
    test_features.assign(date=test_dates, condition=test_target).to_csv(
        os.path.join(model_folder, "test.csv"), index=False
    )

    print("Tuning with time-ordered 5-fold cross-validation:")
    results = train_models(spec, train_features, train_target)
    table = comparison_table(results, test_features, test_target, spec, f"{FOLDER}/model_comparison.csv")
    print(table.to_string(index=False))
    plot_confusion_matrices(results, test_features, test_target, f"{FOLDER}/confusion_matrices.png")

    print("The brief's three inputs only:")
    brief = brief_only_spec()
    brief_results = train_models(brief, train_features[brief["numeric"]], train_target)
    comparison = input_comparison(results, brief_results, test_features, test_target, spec)
    save_table(comparison, f"{FOLDER}/input_comparison.csv")
    print(comparison.to_string(index=False))

    bayes = results["Naive Bayes"]["pipeline"]
    tree = results["Decision Tree"]["pipeline"]
    plot_class_curves(bayes, spec, f"{FOLDER}/class_curves.png")
    tree_rules(tree, spec, max_depth=20, filename=f"{FOLDER}/tree_rules.txt")
    wrong = wrong_predictions(bayes, test_features, test_target, spec)
    save_table(wrong, f"{FOLDER}/wrong_predictions.csv")

    explained = {name: result for name, result in results.items() if result["role"] != "Baseline"}
    importance = permutation_importance_table(
        explained, test_features, test_target, spec, filename=f"{FOLDER}/permutation_importance.csv"
    )
    plot_permutation_importance(importance, filename=f"{FOLDER}/permutation_importance.png")

    model_info = {
        "dataset": "Open-Meteo London, noon readings",
        "classes": sorted(data["condition"].unique()),
        "test_days": [str(test_dates.iloc[0]), str(test_dates.iloc[-1])],
        "best_model": best_model_name(results),
        "test_scores": {
            name: test_scores(r["pipeline"], test_features, test_target, spec) for name, r in results.items()
        },
        "cv_scores": {name: r["cv_score"] for name, r in results.items()},
        "tree_leaves": int(tree.named_steps["model"].get_n_leaves()),
        "tree_depth": int(tree.named_steps["model"].get_depth()),
    }
    model_info.update(input_summary(train_features, spec))
    save_models(results, model_info, folder=model_folder)

    write_results_doc(
        "Results",
        "Produced by `python main.py`. The test set is the most recent fifth of the days "
        f"({test_dates.iloc[0]} to {test_dates.iloc[-1]}); no test day was used for tuning or model choice. "
        f"The full rules of the tree are in `outputs/{FOLDER}/tree_rules.txt`.",
        results_sections(),
    )
    print("  Done. Run: streamlit run app.py")


if __name__ == "__main__":
    main()
