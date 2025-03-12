import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from IPython.display import display
from datetime import datetime, date, timedelta, time
import statistics

plt.close('all')

start_date = date(2025, 1, 28)  # Reference start date
marker_times = [
    datetime(2025, 2, 1, 12, 0, 0),
    datetime(2025, 2, 4, 12, 0, 0),
    datetime(2025, 2, 7, 12, 0, 0),
    datetime(2025, 2, 10, 12, 0, 0)
]  # Important dates
last_date = date(2025, 2, 24)
datetag = str(last_date)
known_tags = [196447011, 19645674, 19645246186, 19644148217, 19647144222]
filtermin = 13  # Lower weight filter (g)
filtermax = 28  # Upper weight filter (g)

loadpath = "/Users/martynastasiak/Desktop/Data/Fem_exp/"
data = pd.read_csv(loadpath + '/' + datetag + "_events.csv")
display(data.head(5))

# Animal labels for legend
animal_labels = {
    196447011: 'A1',
    19645674: 'A2',
    19645246186: 'A3',
    19644148217: 'A4',
    19647144222: 'A5'
}

dates_to_include = [
    date(2025, 2, 1),
    date(2025, 2, 4),
    date(2025, 2, 7),
    date(2025, 2, 10),
    date(2025, 2, 24)
]

matrix = []
x = []

# Loop over selected dates
for day in dates_to_include:
    try:
        data = pd.read_csv(loadpath + str(day) + "_events.csv")
    except FileNotFoundError:
        print(f"No data file found for {day}, skipping.")
        continue

    # Define 12-hour bins
    bin1_start = datetime.combine(day, time(12, 0))
    bin2_end = datetime.combine(day, time(12, 0)) 

    daily_averages = []
    for tag in known_tags:
        filtered_an = data.loc[data['Animal'] == tag]
        filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
        filtered_minmax = filtered_min.loc[filtered_min['Weight'] < filtermax]

        # Weights after 12:00
        filtered_time1 = filtered_minmax.loc[
            pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') > bin1_start
        ]
        avg1 = statistics.mean(filtered_time1['Weight']) if not filtered_time1.empty else np.nan

        # Weights before 12:00
        filtered_time2 = filtered_minmax.loc[
            pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') < bin2_end
        ]
        avg2 = statistics.mean(filtered_time2['Weight']) if not filtered_time2.empty else np.nan

        # Daily average
        daily_avg = np.nanmean([avg1, avg2])
        daily_averages.append(daily_avg)

    matrix.append(daily_averages)
    x.append((day - start_date).days)


# Each row an animal
matrix1 = list(map(list, zip(*matrix)))
fig, ax = plt.subplots(figsize=(12, 6))

# Colours for each animal
colors = plt.cm.tab10(range(len(known_tags)))

# Plot weights
for i, animal in enumerate(known_tags):
    ax.plot(x, matrix1[i], label=animal_labels[animal], color=colors[i], marker='o', linestyle='-')

# Marker times
marker_days = [(m.date() - start_date).days for m in marker_times]
for marker_day in marker_days:
    ax.axvline(marker_day, color='black', linestyle='dashed')

# Format
ax.set_title("Mean Weight per One-day Window")
ax.set_ylabel("Weight (g)")
ax.set_xlabel("Day")

# X-axis
ax.set_xticks(x)
ax.set_xticklabels([str(day) for day in x])

# Add legend
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()