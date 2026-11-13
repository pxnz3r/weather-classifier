# Results

Produced by `python main.py`. The test set is the most recent fifth of the days (2022-01-06 to 2024-12-31); no test day was used for tuning or model choice. The full rules of the tree are in `outputs/weather/tree_rules.txt`.

## Models

### Scores on the unseen test days (macro averages over the three types)

| Model | Role | CV f1 macro | Accuracy | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| Decision Tree | Main | 0.49 | 0.499 | 0.488 | 0.507 | 0.491 |
| Naive Bayes | Main | 0.458 | 0.472 | 0.491 | 0.525 | 0.476 |
| Random Forest | Benchmark beyond the course | 0.533 | 0.514 | 0.508 | 0.533 | 0.509 |
| Always cloudy | Baseline | 0.237 | 0.526 | 0.175 | 0.333 | 0.23 |

![confusion matrices](../outputs/figures/weather/confusion_matrices.png)

## Inputs

### The brief's three inputs against all five (test-set macro F1)

| Model | Temperature, humidity, wind | Plus pressure and its change |
| --- | --- | --- |
| Decision Tree | 0.452 | 0.491 |
| Naive Bayes | 0.399 | 0.476 |

![permutation importance](../outputs/figures/weather/permutation_importance.png)

### Permutation importance (drop in macro F1 when the input is shuffled)

|  | Decision Tree | Naive Bayes | Random Forest |
| --- | --- | --- | --- |
| Relative humidity (%) | 0.079 | 0.0465 | 0.0876 |
| Air pressure (hPa) | 0.0723 | 0.0503 | 0.0792 |
| Temperature (°C) | 0.0227 | 0.014 | 0.0344 |
| Pressure change since 6 am (hPa) | 0.0032 | 0.0136 | 0.0156 |
| Wind speed (km/h) | 0.0022 | 0.0009 | 0.0069 |

## Naive Bayes

![class curves](../outputs/figures/weather/class_curves.png)

## Mistakes

### Test days Naive Bayes got wrong

| temperature | humidity | wind_speed | pressure | pressure_change | Real | Predicted |
| --- | --- | --- | --- | --- | --- | --- |
| 4.7 | 74 | 28.8 | 1010.8 | 1.3 | sunny | rainy |
| 6.4 | 77 | 11.3 | 1003.2 | 2.6 | sunny | rainy |
| 7.0 | 89 | 11.0 | 1019.6 | 5.0 | cloudy | rainy |
| 2.6 | 81 | 2.3 | 1036.5 | -0.9 | sunny | cloudy |
| 4.7 | 92 | 9.0 | 1026.2 | -1.5 | sunny | cloudy |
| 5.7 | 82 | 4.7 | 1038.9 | 3.1 | sunny | cloudy |
| 4.2 | 76 | 10.5 | 1039.7 | 0.0 | sunny | cloudy |
| 4.9 | 84 | 9.7 | 1037.9 | 0.1 | sunny | cloudy |
| 12.5 | 77 | 35.5 | 1026.2 | -1.1 | cloudy | rainy |
| 8.9 | 80 | 16.2 | 1014.2 | -1.2 | cloudy | rainy |
| 5.6 | 77 | 21.9 | 1010.6 | 3.6 | sunny | rainy |
| 10.6 | 66 | 31.0 | 1005.1 | -0.4 | cloudy | rainy |
| 6.8 | 71 | 4.6 | 1034.1 | 3.3 | cloudy | sunny |
| 8.0 | 82 | 31.3 | 1001.2 | -7.0 | cloudy | rainy |
| 14.5 | 76 | 33.5 | 996.9 | 0.9 | cloudy | rainy |
| 9.7 | 59 | 68.0 | 986.4 | -7.5 | sunny | rainy |
| 10.3 | 65 | 38.2 | 1007.5 | 4.9 | cloudy | rainy |
| 13.6 | 64 | 38.3 | 1014.4 | -3.1 | cloudy | rainy |
| 10.5 | 59 | 31.4 | 1021.9 | -2.8 | rainy | cloudy |
| 9.4 | 58 | 18.6 | 1027.0 | 5.7 | cloudy | sunny |

## Data

### Data quality

| Column | Type | Missing | Distinct values |
| --- | --- | --- | --- |
| temperature | numeric | 0 | 323 |
| humidity | numeric | 0 | 75 |
| wind_speed | numeric | 0 | 405 |
| pressure | numeric | 0 | 582 |
| pressure_change | numeric | 0 | 199 |
| condition | target | 0 | 3 |

![target](../outputs/figures/weather/target.png)

![pairs](../outputs/figures/weather/pairs.png)

![correlations](../outputs/figures/weather/correlations.png)
