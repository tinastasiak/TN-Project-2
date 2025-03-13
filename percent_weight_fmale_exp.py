import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statistics
from datetime import datetime, date, timedelta, time

plt.close('all')

start_date = date(2025, 1, 29)
marker_times = [datetime(2025, 2, 1, 12, 0, 0), datetime(2025, 2, 4, 12, 0, 0),
                datetime(2025, 2, 7, 12, 0, 0), datetime(2025, 2, 10, 12, 0, 0)]
last_date = date(2025, 2, 24)
datetag = str(last_date)

known_tags = [196447011, 19645674, 19645246186, 19644148217, 19647144222]
filtermin = 13
filtermax = 28
loadpath = "/Users/martynastasiak/Desktop/Data/Fem_exp/"

# Animal labels
animal_labels = {
    196447011: 'A1',
    19645674: 'A2',
    19645246186: 'A3',
    19644148217: 'A4',
    19647144222: 'A5'
}

# Dates
dates_to_include = [
    date(2025, 2, 1), 
    date(2025, 2, 4),
    date(2025, 2, 7),
    date(2025, 2, 24)
]

day_mapping = {
    date(2025, 2, 1): 4,
    date(2025, 2, 4): 7,
    date(2025, 2, 7): 10,
    date(2025, 2, 24): 27
}

matrix = []
x = []

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
            pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') > bin1_start]
        avg1 = statistics.mean(filtered_time1['Weight']) if not filtered_time1.empty else np.nan

        # Weights before 12:00
        filtered_time2 = filtered_minmax.loc[
            pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') < bin2_end]
        avg2 = statistics.mean(filtered_time2['Weight']) if not filtered_time2.empty else np.nan

        # Daily average of both
        daily_avg = np.nanmean([avg1, avg2])
        daily_averages.append(daily_avg)

    matrix.append(daily_averages)
    x.append(day_mapping[day])


# Transpose matrix
matrix1 = list(map(list, zip(*matrix)))
day_indices = {day: idx for idx, day in enumerate(x)}

try:
    # Extract weights for specific days
    day4_weights = [matrix1[i][day_indices[4]] for i in range(len(known_tags))]
    day7_weights = [matrix1[i][day_indices[7]] for i in range(len(known_tags))]
    day10_weights = [matrix1[i][day_indices[10]] for i in range(len(known_tags))]
    day27_weights = [matrix1[i][day_indices[27]] for i in range(len(known_tags))]

    # Calculate percentage change from Day 4 (baseline)
    percent_change_day7 = [((base - d7) / base) * 100 for base, d7 in zip(day4_weights, day7_weights)]
    percent_change_day10 = [((base - d10) / base) * 100 for base, d10 in zip(day4_weights, day10_weights)]
    percent_change_day27 = [((base - d27) / base) * 100 for base, d27 in zip(day4_weights, day27_weights)]

    print("\nPercentage weight change from baseline (Day 4):")
    for i, tag in enumerate(known_tags):
        print(f"Animal {animal_labels[tag]}: "
              f"Day 7 = {percent_change_day7[i]:.2f}%, "
              f"Day 10 = {percent_change_day10[i]:.2f}%, "
              f"Day 27 = {percent_change_day27[i]:.2f}%")

    print("\nThreshold checks (>5% and >10% weight loss):")
    for day, pct_list in zip(["Day 7", "Day 10", "Day 27"], [percent_change_day7, percent_change_day10, percent_change_day27]):
        above_5 = sum(1 for p in pct_list if p > 5)
        above_10 = sum(1 for p in pct_list if p > 10)
        print(f"{day}: {above_5} animals lost >5%, {above_10} animals lost >10%")

except KeyError as e:
    print(f"Error: {e}. Make sure Day 4, Day 7, Day 10, and Day 27 are present in the x-axis days.")