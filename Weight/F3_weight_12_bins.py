import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from IPython.display import display
from datetime import datetime, date, timedelta, time
import matplotlib.dates as mdates
import statistics

plt.close('all')

start_date = date(2025, 1, 29) 
marker_times = [datetime(2025, 2, 1, 12, 0, 0), datetime(2025, 2, 4, 12, 0, 0), 
                datetime(2025, 2, 7, 12, 0, 0), datetime(2025, 2, 10, 12, 0, 0)] # Important dates
last_date = date(2025, 2, 24)
all_dates = pd.date_range(start=start_date, end=last_date).date
datetag = str(last_date)
known_tags = [196447011, 19645674, 19645246186, 19644148217, 19647144222]
filtermin = 13
filtermax = 28
d = last_date - start_date
days_to_plot = d.days

loadpath = "/Users/martynastasiak/Desktop/Data/Fem_exp/"
data = pd.read_csv(loadpath + '/' + datetag + "_events.csv")
display(data.head(5))

# Animal labels for the legend
animal_labels = {
    196447011: 'A1', 
    19645674: 'A2', 
    19645246186: 'A3', 
    19644148217: 'A4', 
    19647144222: 'A5'
}

# Daily averages of known animals
matrix = []
x = []
for j in range(days_to_plot):
    day = last_date - timedelta(days=j) 
    data = pd.read_csv(loadpath + str(day) + "_events.csv")
    # Plot filtered weights of known animals and gather averages
    bin1_offset = time(18, 0)
    bin1_centre = datetime.combine(day, bin1_offset)
    bin1_start_offset = time(12, 0)
    bin1_start = datetime.combine(day, bin1_start_offset)
    x.append(bin1_centre)
    bin2_offset = time(6, 0)
    bin2_centre = datetime.combine(day, bin2_offset)
    x.append(bin2_centre)
    
    averages1 = []
    averages2 = []
    for i in range(len(known_tags)):
        filtered_an = data.loc[data['Animal'] == known_tags[i]] 
        filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
        filtered_minmax = filtered_min.loc[filtered_min['Weight'] < filtermax]
        filtered_time = filtered_minmax.loc[pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') > bin1_start]
        if filtered_time.empty:
            print('empty bin')
            averages1.append(np.nan)
        else:
            averages1.append(statistics.mean(filtered_time['Weight']))
        filtered_time = filtered_minmax.loc[pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') < bin1_start]
        if filtered_time.empty:
            print('empty bin')
            averages2.append(np.nan)
        else:
            averages2.append(statistics.mean(filtered_time['Weight']))
    matrix.append(averages1)
    matrix.append(averages2)

matrix1 = list(map(list, zip(*matrix)))

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot each animal
colors = plt.cm.tab10(range(len(known_tags)))

for i, animal in enumerate(known_tags):
    ax.plot(x, matrix1[i], label=animal_labels[animal], color=colors[i])

# Add vertical lines for marker times
for marker_time in marker_times:
    ax.axvline(marker_time, color='black', linestyle='dashed')

# Formatting the plot
ax.set_title(f"Mean Weight in 12 Hour Blocks ")
ax.set_ylabel("Weight (g)")
ax.set_xlabel("Day")

# X-axis
day_numbers = range(1, len(all_dates) + 1)
ax.set_xticks(all_dates)
ax.set_xticklabels([str(i) for i in day_numbers])
plt.xticks(rotation=45)

#Y axis 
ax.set_ylim(13, 24)

plt.legend(loc='lower right')

plt.tight_layout()
plt.show()