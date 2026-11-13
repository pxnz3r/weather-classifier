<div align="center">

<h1>Weather classifier</h1>

<p>Classifies the weather at noon as sunny, cloudy or rainy from temperature, humidity and wind, with a Decision Tree and Naive Bayes, and tests them on three years they never saw. Built on 15 years of London weather from the Open-Meteo archive, with an interactive demo that explains each verdict.</p>

<p>
<a href="https://github.com/pxnz3r/weather-classifier/actions/workflows/ci.yml"><img src="https://github.com/pxnz3r/weather-classifier/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
<img src="https://img.shields.io/badge/python-3.14-blue" alt="Python 3.14">
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

<p><a href="docs/results.md">Results</a> · <a href="docs/methodology.md">Methodology</a> · <a href="docs/deploy.md">Deploy the demo</a></p>

<img src="outputs/figures/weather/class_curves.png" width="720" alt="What Naive Bayes learned: one bell curve per input and weather type">

</div>

## How it works

1. **Load and check** 15 years of London weather and label each noon as sunny, cloudy or rainy.
2. **Tune** a Decision Tree and Naive Bayes with cross-validation on the earlier years.
3. **Score once** on the last three years, which the models never saw.
4. **Test how sure the scores are** with bootstrap intervals, a paired test against every rival, learning curves and a baseline that ignores the inputs.
5. **Study the mistakes**: which weather gets confused for which, then **try it** in the Streamlit demo.

## Results

Trained on 4,360 noon readings from 2010 to early 2022; tested on the 1,090 days from January 2022 to December 2024. 56% of days are cloudy, 22% rainy and 22% sunny.

| Model | Macro F1 | Accuracy | Sunny recall | Cloudy recall | Rainy recall |
| --- | --- | --- | --- | --- | --- |
| **Decision Tree** (depth 6) | 0.491 | 0.499 | 0.47 | 0.47 | 0.58 |
| **Naive Bayes** (equal priors) | 0.476 | 0.472 | 0.61 | 0.34 | 0.62 |
| Random Forest (benchmark) | 0.509 | 0.514 | 0.56 | 0.47 | 0.57 |
| Always cloudy (baseline) | 0.230 | 0.526 | 0 | 1 | 0 |

- **The air alone only half tells the weather.** Both models beat the baseline clearly on macro F1, and even the forest stays near 0.5. Clouds aren't visible in temperature, humidity and wind.
- **Rain is easiest**: humid air and low pressure. **Sunny and cloudy overlap most**, so most mistakes are between them.
- **Pressure helps.** With only the brief's three inputs, Naive Bayes falls from 0.48 to 0.40 macro F1 and the tree from 0.49 to 0.45. Humidity and pressure matter most; wind barely matters.
- **Accuracy misleads.** "Always cloudy" has the best accuracy and is useless. Macro F1 weighs the three types equally.

Full tables and figures: [docs/results.md](docs/results.md). How it was done: [docs/methodology.md](docs/methodology.md).

## How sure the results are

**Weather at noon is hard to call.** Random Forest's macro F1 is 0.509 (95% interval 0.481 to 0.539) against 0.230 for always predicting cloudy.

**The forest beats Naive Bayes but not the tree.** McNemar's test: p = 0.011 against Naive Bayes, p = 0.323 against the Decision Tree.

**Both trees overfit, and more years would help.** The forest's training F1 is 0.768 against 0.518 on validation, and its validation curve is still rising.

**Cloudy is the problem class.** The most common mix-up is cloudy predicted as sunny: 190 days, a third of all cloudy days.

Every table and figure behind these is in [docs/results.md](docs/results.md).

## Run it

Needs Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py
uv run streamlit run app.py
```

`main.py` downloads the data once into `data/`, then writes figures, tables and the tree's rules to `outputs/`, models to `models/` and the tables to `docs/results.md`. Outputs and models are committed, so the demo works without running it.

## The demo

- **Overview**: what the project is, how both models decide and what was found.
- **Classify**: set a noon reading or start from a real test day, and see each model's chances for the three types: the inputs that tipped Naive Bayes, or the questions the tree asked.
- **How it decides**: Naive Bayes's bell curves and every rule of the tree.
- **Results**: model comparison, the inputs comparison, mistakes, permutation importance and data checks.

## Layout

```
weather_classifier/   spec.py (inputs and models), data.py (download, weather codes to types),
                      explain.py (bell curves, per-reading evidence), report.py
pxlab/                shared engine (vendored): data checks, pipelines, tuning, evaluation, tree rules, app helpers
main.py               the full study
app.py                the Streamlit demo
docs/                 methodology, results, deploy
```

## Data

[Open-Meteo](https://open-meteo.com/) historical weather API (ERA5 reanalysis from the Copernicus Climate Change Service), CC BY 4.0. Hourly readings for central London, 2010 to 2024.

## License

MIT
