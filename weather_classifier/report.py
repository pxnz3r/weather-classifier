"""
report.py - which saved tables and figures make up the results. The app's
Results tab and docs/results.md both read this list, so they always match.
"""

FOLDER = "weather"


def results_sections():
    """
    The results, grouped into sections.

    Returns:
        A list of (section name, items) for pxlab's show_results_tabs() and
        write_results_doc().
    """
    return [
        (
            "Models",
            [
                (
                    "table",
                    "Scores on the unseen test days (macro averages over the three types)",
                    f"{FOLDER}/model_comparison.csv",
                ),
                ("figure", f"{FOLDER}/confusion_matrices.png"),
            ],
        ),
        (
            "Inputs",
            [
                (
                    "table",
                    "The brief's three inputs against all five (test-set macro F1)",
                    f"{FOLDER}/input_comparison.csv",
                ),
                ("figure", f"{FOLDER}/permutation_importance.png"),
                (
                    "table",
                    "Permutation importance (drop in macro F1 when the input is shuffled)",
                    f"{FOLDER}/permutation_importance.csv",
                ),
            ],
        ),
        ("Naive Bayes", [("figure", f"{FOLDER}/class_curves.png")]),
        ("Mistakes", [("table", "Test days Naive Bayes got wrong", f"{FOLDER}/wrong_predictions.csv")]),
        (
            "Data",
            [
                ("table", "Data quality", f"{FOLDER}/data_quality.csv"),
                ("figure", f"{FOLDER}/target.png"),
                ("figure", f"{FOLDER}/pairs.png"),
                ("figure", f"{FOLDER}/correlations.png"),
            ],
        ),
    ]
