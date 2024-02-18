import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Ensure the 'data' directory exists
input_file_path = 'data/Transformator_Alle.csv'
os.makedirs('data', exist_ok=True)

# Load and preprocess the dataset
df = pd.read_csv(input_file_path, delimiter=';', decimal=',')
df['Datum'] = df['Datum'].str.strip()
df['Uhrzeit'] = df['Uhrzeit'].str.strip()
df['Datum_Uhrzeit'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'], format='%d.%m.%y %H:%M', errors='coerce')
df.set_index('Datum_Uhrzeit', inplace=True)

# Numeric conversion and 'Wirkleistung' calculation
df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']] = df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']].apply(pd.to_numeric, errors='coerce')
df['cos_phi'] = df['P L Sum'] / df['S L Sum']
df['Wirkleistung'] = (df['U L1'] * df['I L1'] + df['U L2'] * df['I L2'] + df['U L3'] * df['I L3']) * df['cos_phi']
df['Wirkleistung'] = df['Wirkleistung'] / 1000

# Group data by day of week and resample to 15-minute intervals
df['day_of_week'] = df.index.dayofweek
df['time'] = df.index.time

# Split data into workdays, Saturday, and Sunday
workdays = df[df['day_of_week'] < 5]
saturday = df[df['day_of_week'] == 5]
sunday = df[df['day_of_week'] == 6]

# Resample data for each group
workdays_resampled = workdays.groupby('time')['Wirkleistung'].mean()
saturday_resampled = saturday.groupby('time')['Wirkleistung'].mean()
sunday_resampled = sunday.groupby('time')['Wirkleistung'].mean()

# Function to map time to a continuous numerical range
def map_time_to_range(time_series, start):
    # Map each time to a numerical value starting from 'start'
    time_to_num = {time: i + start for i, time in enumerate(sorted(set(time_series)))}
    return time_series.map(time_to_num), len(time_to_num)

# Map times for workdays, Saturday, and Sunday to numerical ranges
workdays_mapped, workdays_len = map_time_to_range(workdays_resampled.index, 0)
saturday_mapped, saturday_len = map_time_to_range(saturday_resampled.index, workdays_len)
sunday_mapped, sunday_len = map_time_to_range(sunday_resampled.index, workdays_len + saturday_len)

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(workdays_mapped, workdays_resampled, label='Workdays (Mon-Fri)', color='blue')
plt.plot(saturday_mapped, saturday_resampled, label='Saturday', color='green')
plt.plot(sunday_mapped, sunday_resampled, label='Sunday', color='red')

# Customize x-axis ticks and labels
plt.xticks([0, workdays_len/2, workdays_len, workdays_len + saturday_len/2, workdays_len + saturday_len], ['Workdays Start', 'Workdays Mid', 'Saturday Start', 'Saturday Mid', 'Sunday'])

plt.title('Average Wirkleistung in 15-minute Intervals')
plt.ylabel('Wirkleistung [kW]')
plt.legend()
plt.tight_layout()
plt.show()
