import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

plt.close('all')

# Start and end dates
start_date = date(2025, 1, 29)
last_date = date(2025, 2, 24)
marker_times = [
    datetime(2025, 2, 1, 12, 0, 0),
    datetime(2025, 2, 4, 12, 0, 0),
    datetime(2025, 2, 7, 12, 0, 0),
    datetime(2025, 2, 10, 12, 0, 0)
]
days_to_plot = (last_date - start_date).days + 1

# Data path
loadpath = "/Users/martynastasiak/Desktop/Data/Fem_exp/"
known_tags = [196447011, 19645674, 19645246186, 19644148217, 19647144222]

# Empty DataFrame to store all data
all_data = []

# Loop over all days, load data, and append it to all_data
for j in range(days_to_plot):
    day = start_date + timedelta(days=j)
    try:
        daily_data = pd.read_csv(loadpath + str(day) + "_events.csv")
    except FileNotFoundError:
        print(f"Missing data file for {day}")
        continue

    daily_data['Start_Time'] = pd.to_datetime(daily_data['Start_Time'])
    daily_data['Date'] = daily_data['Start_Time'].dt.date

    # Assign each entry to a 12-hour time slot
    daily_data['Time_Slot'] = np.where(
        daily_data['Start_Time'].dt.hour < 12, "Day", "Night"
    )

    # Only known tags
    daily_data = daily_data[daily_data['Animal'].isin(known_tags)]

    all_data.append(daily_data)

# Combine all collected data
if all_data:
    data = pd.concat(all_data, ignore_index=True)
else:
    raise ValueError("No data found for the given date range.")

# Group by 'Date', 'Animal', and 'Time_Slot' to calculate the 12-hour average pellet consumption
avg_pellets = data.groupby(['Date', 'Animal', 'Time_Slot'])['Pellets'].sum().reset_index()

# List of all dates
all_dates = pd.date_range(start=start_date, end=last_date).date

# Combinations of (Date, Animal, Time_Slot)
time_slots = ["Day", "Night"]
full_index = pd.MultiIndex.from_product([all_dates, known_tags, time_slots], names=['Date', 'Animal', 'Time_Slot'])
avg_pellets = avg_pellets.set_index(['Date', 'Animal', 'Time_Slot']).reindex(full_index).reset_index()
avg_pellets['Pellets'] = avg_pellets['Pellets'].astype(float)

# Convert 'Date' and 'Time_Slot' into a combined datetime object for plotting
avg_pellets['Datetime'] = avg_pellets.apply(lambda row: datetime.combine(row['Date'], datetime.min.time()) + timedelta(hours=6 if row['Time_Slot'] == "Day" else 18), axis=1)

# Animal labels
animal_labels = {
    196447011: 'A1', 19645674: 'A2', 19645246186: 'A3', 
    19644148217: 'A4', 19647144222: 'A5'
}

# Line plot
fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.tab10(range(len(known_tags)))

for i, animal in enumerate(known_tags):
    animal_data = avg_pellets[avg_pellets['Animal'] == animal]

    # Convert datetime for plotting
    dates = animal_data['Datetime']
    avg_values = animal_data['Pellets']

    # Line plot
    ax.plot(dates, avg_values, color=colors[i], linestyle='-', alpha=0.5, label=animal_labels[animal])

# Formatting
ax.set_xlabel('Day')
ax.set_ylabel('Pellet Consumption (N)')
ax.set_title('Pellet Consumption in 12-hour Blocks')

# X-axis
day_numbers = range(1, len(all_dates) + 1)
ax.set_xticks(all_dates)
ax.set_xticklabels([str(i) for i in day_numbers])
plt.xticks(rotation=45)

# Adding vertical lines for the marker times
for marker_time in marker_times:
    ax.axvline(marker_time, color='black', linestyle='dashed')

ax.legend()
plt.tight_layout()
plt.show()