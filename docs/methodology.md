# Methodology

## Question

From temperature, humidity and wind, can a Decision Tree or Naive Bayes tell a sunny, cloudy or rainy day, and does it still work on later days it never saw?

## Data

Open-Meteo's historical archive (ERA5 reanalysis) for central London, hourly from 2010 to 2024. One reading per day is kept, at noon, so "sunny" means sunny in daylight.

The WMO weather code of each reading is grouped:

| Type | Weather codes |
| --- | --- |
| Sunny | clear sky, mainly clear |
| Cloudy | partly cloudy, overcast |
| Rainy | drizzle, rain, rain showers, thunderstorm |

Fog and snow (29 noons in 15 years) fit none of the three and are dropped, leaving 5,450 days.

| Input | Why |
| --- | --- |
| Temperature, relative humidity, wind speed | the brief's three inputs |
| Air pressure | low pressure systems bring cloud and rain |
| Pressure change since 6 am | falling pressure signals rain coming |

Open-Meteo works the weather code out from cloud cover and rainfall, so those are not inputs: the model would be reading the answer.

## Steps

1. **Checks**: missing values, duplicates, the type split, correlations and a pair plot of the inputs.
2. **Split by time**: the first 80% of days (2010 to January 2022) train, the last 20% (January 2022 to December 2024) test. Shuffling would let the model learn from days right next to the test days.
3. **Models**, each in a scikit-learn Pipeline:
   - Decision Tree, tuned over depth (3 to 8), minimum days per leaf (10 to 60) and class weights.
   - Gaussian Naive Bayes, with learned or equal priors.
   - Random Forest, 300 trees, a benchmark beyond the course.
   - Always cloudy, the baseline.
4. **Tuning**: time-ordered 5-fold cross-validation (each fold trains on earlier days and validates on the days after), scored by macro F1: the F1 of each type averaged, so the rarer sunny and rainy days count as much as cloudy ones.
5. **Test scores**: accuracy and macro precision, recall and F1 on the unseen days. Confusion matrices.
6. **Inputs**: the two main models trained again on the brief's three inputs only.
7. **Explanations**: Naive Bayes's bell curve per input and type; the tree's full rules; permutation importance on the test days, 10 shuffles per input.
8. **In-depth analysis** (`pxlab.tabular.study`): 1,000-round bootstrap 95% intervals for the headline test scores, next to a baseline that ignores the inputs; McNemar's test of the best model against each other model; learning curves; and an error analysis that compares the inputs of right and wrong answers, lists the classes the model mixes up and shows how accuracy depends on the model's confidence. Each finding is one sentence in `outputs/weather/key_findings.csv`.

## Limits

- **One city.** Rules learned for London's climate won't carry to a dry or tropical place.
- **Reanalysis, not a weather station.** ERA5 blends observations into a weather model on a roughly 30 km grid. Its weather code is a model estimate, not what an observer saw.
- **Noon only.** A day that rained in the morning and cleared by noon counts as sunny or cloudy.
- **The inputs can't see clouds.** Sunny and overcast days with the same air are indistinguishable here, which caps every model near a macro F1 of 0.5. Satellite images or cloud cover would lift it, but then the task becomes reading the answer.
- **Naive Bayes's assumption is badly broken.** Humidity and temperature move together (warm afternoons are drier), so treating them as independent double-counts their evidence.
