import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import statistics
from datetime import date, timedelta

plt.close('all')

# Date ranges- without habituation
start_date_exp = date(2025, 1, 31)
last_date_exp = date(2025, 2, 24)
start_date_cntrl = date(2025, 2, 27)
last_date_cntrl = date(2025, 3, 19)
filtermin = 14
filtermax = 28

days_to_plot_exp = (last_date_exp - start_date_exp).days + 1
days_to_plot_cntrl = (last_date_cntrl - start_date_cntrl).days + 1

# Paths
folder_control = "/Users/martynastasiak/Desktop/Data/Fem_cntrl/"
folder_experimental = "/Users/martynastasiak/Desktop/Data/Fem_exp/"

# Animal tags
known_tags_control = [19644207130, 19645782, 19647186244, 19644194143]
known_tags_experimental = [196447011, 19645674, 19645246186, 19644148217, 19647144222]

# Process group data and calculate weight change
def process_group(days_to_plot, start_date, folder, known_tags):
    mean_weights = []
    sem_weights = []
    x_values = []

    # Loop
    for j in range(days_to_plot):
        day = start_date + timedelta(days=j)
        file_path = os.path.join(folder, f"{day}_events.csv")

        if not os.path.exists(file_path):
            continue 

        data = pd.read_csv(file_path)
        
        data = data[data['Pellets'] > 0]
        
        # Weight
        data = data[(data['Weight'] >= filtermin) & (data['Weight'] <= filtermax)]

        x_values.append(j + 1) 

        daily_weights = []
        for tag in known_tags:
            filtered_data = data[data['Animal'] == tag]
            if not filtered_data.empty:
                daily_weights.append(statistics.mean(filtered_data['Weight']))

        if daily_weights:
            mean_weights.append(np.mean(daily_weights))
            sem_weights.append(np.std(daily_weights) / np.sqrt(len(daily_weights))) 
        else:
            mean_weights.append(np.nan)
            sem_weights.append(np.nan)

    return x_values, mean_weights, sem_weights

# Process groups
x_experimental, mean_experimental, sem_experimental = process_group(days_to_plot_exp, start_date_exp, folder_experimental, known_tags_experimental)
x_control, mean_control, sem_control = process_group(days_to_plot_cntrl, start_date_cntrl, folder_control, known_tags_control)

# Calculate Baseline (average weight for the first two days)
baseline_exp = np.mean(mean_experimental[:2]) 
baseline_control = np.mean(mean_control[:2])  

# Calculate weight change as percentage from baseline
def calculate_weight_change(data, baseline):
    return [(val / baseline) * 100 if not np.isnan(val) else np.nan for val in data]

mean_experimental = calculate_weight_change(mean_experimental, baseline_exp)
mean_control = calculate_weight_change(mean_control, baseline_control)

fig, ax = plt.subplots(figsize=(10, 6))

# Plot control
ax.errorbar(x_control, mean_control, yerr=sem_control, label="Control Group", color='red', fmt='o', linestyle='-', capsize=5)

# Plot experimental
ax.errorbar(x_experimental, mean_experimental, yerr=sem_experimental, label="Experimental Group", color='blue', fmt='o', linestyle='-', capsize=5)

# Formatting
ax.set_title("Body Weight Change in Control vs Experimental Groups")
ax.set_ylabel("Body Weight Change (%)")
ax.set_xlabel("Days")
ax.axhline(y=100, color='black', linestyle='dashed', alpha=0.5)
ax.set_ylim(90, 120)
ax.legend(loc='lower right')
plt.xticks(rotation=45)
plt.grid(True)

plt.tight_layout()
plt.show()