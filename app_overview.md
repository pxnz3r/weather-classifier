### What this is

Classifies the weather at noon as **sunny, cloudy or rainy** from temperature, humidity and wind, with a **Decision Tree** and **Naive Bayes**. It learns from 12 years of London weather (2010 to early 2022) and is tested on the three years after that, which it never saw.

The data is Open-Meteo's historical archive: one noon reading per day. Its weather code is grouped into the three types; fog and snow are rare in London and dropped. Air pressure and how it changed since 6 am are added to the brief's three inputs.

### How the two models decide

- **Decision Tree**: a flowchart of yes/no questions such as "is humidity above 80%?". You can follow every step.
- **Naive Bayes**: one bell curve per input and weather type, learned from the training days. For a new reading it multiplies how likely each value is under each type and picks the most likely type.

A **Random Forest** is a benchmark beyond the course, and **Always cloudy** is the floor.

### What to try

- **Classify**: start from a typical noon or a real test day, change the values and see each model's verdict with its reasons.
- **How it decides**: Naive Bayes's bell curves and every rule of the tree.
- **Results**: scores, the inputs comparison, mistakes and which inputs matter.

### What was found

- **The air alone only half tells the weather.** On the unseen days the tree scores a macro F1 of 0.49 and Naive Bayes 0.48, against 0.23 for always answering cloudy. Even the Random Forest only reaches 0.51.
- **Rain is easiest** (about 60% of rainy days caught): humid air and low pressure. **Sunny and cloudy overlap most**: a dry overcast day and a dry clear day have much the same temperature, humidity and wind.
- **Pressure helps.** With only the brief's three inputs Naive Bayes drops from 0.48 to 0.40 and the tree from 0.49 to 0.45. Humidity and pressure matter most; wind barely matters.
- **Accuracy misleads here.** Always answering cloudy is right 53% of the time, more than either model, while never spotting a sunny or rainy day. Macro F1 gives the three types equal weight.

Code and every figure: [github.com/pxnz3r/weather-classifier](https://github.com/pxnz3r/weather-classifier).
