import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta, time
import statistics

plt.close('all')

start_date = date(2025, 1, 28)
marker_times = [4, 7, 10, 13]  # Important days relative to start date
last_date = date(2025, 2, 24)
datetag = str(last_date)
known_tags = [196447011, 19645674, 19645246186, 19644148217, 19647144222]
filtermin = 13
filtermax = 28 
loadpath = "/Users/martynastasiak/Desktop/Data/Fem_exp/"

# Animal labels for legend
animal_labels = {
    196447011: 'A1',
    19645674: 'A2',
    19645246186: 'A3',
    19644148217: 'A4',
    19647144222: 'A5'
}

# Selected calendar dates and corresponding days relative to start_date
dates_to_include = [
    date(2025, 2, 1),
    date(2025, 2, 4),
    date(2025, 2, 7),
    date(2025, 2, 10),
    date(2025, 2, 24)
]
x = [(d - start_date).days for d in dates_to_include]  # Day numbers for x-axis

matrix = []

# Loop over selected dates
for day in dates_to_include:
    try:
        data = pd.read_csv(loadpath + str(day) + "_events.csv")  # Load data for the day
    except FileNotFoundError:
        print(f"No data file found for {day}, skipping.")
        continue

    # Define 12-hour bins
    bin1_start = datetime.combine(day, time(12, 0))  # After 12:00
    bin2_end = datetime.combine(day, time(12, 0))  # Before 12:00

    daily_averages = []
    for tag in known_tags:
        filtered_an = data.loc[data['Animal'] == tag]
        filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
        filtered_minmax = filtered_min.loc[filtered_min['Weight'] < filtermax]

        # First bin: after 12:00
        filtered_time1 = filtered_minmax.loc[
            pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') > bin1_start]
        avg1 = statistics.mean(filtered_time1['Weight']) if not filtered_time1.empty else np.nan

        # Second bin: before 12:00
        filtered_time2 = filtered_minmax.loc[
            pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') < bin2_end]
        avg2 = statistics.mean(filtered_time2['Weight']) if not filtered_time2.empty else np.nan

        # Daily average
        daily_avg = np.nanmean([avg1, avg2])
        daily_averages.append(daily_avg)

    matrix.append(daily_averages)

# Transpose matrix to plot per animal
matrix1 = list(map(list, zip(*matrix)))

# Find index for Day 4 and Day 27
try:
    day4_index = x.index(4)  # Day 4
    day27_index = x.index(27)  # Day 27
except ValueError as e:
    print("Error: Day 4 or Day 27 not found in x-axis days. Please check the input days.")
    raise e

# Extract weights
baseline_weights = [matrix1[i][day4_index] for i in range(len(known_tags))]
final_weights = [matrix1[i][day27_index] for i in range(len(known_tags))]

# Calculate percentage decreases and print them
print("\nPercentage of Weight Decrease from Day 4 to Day 27:\n")
for i, (baseline, final) in enumerate(zip(baseline_weights, final_weights)):
    if np.isnan(baseline) or np.isnan(final):
        print(f"{animal_labels[known_tags[i]]}: Data missing for calculation.")
    else:
        percentage_decrease = ((baseline - final) / baseline) * 100
        print(f"{animal_labels[known_tags[i]]}: {percentage_decrease:.2f}% weight decrease")