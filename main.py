import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Ensure the 'data' directory exists
input_file_path = 'data/Transformator_Alle.csv'
os.makedirs('data', exist_ok=True)

# Load and process dataset
df = pd.read_csv(input_file_path, delimiter=';', decimal=',')
df['Datum'] = df['Datum'].str.strip()
df['Uhrzeit'] = df['Uhrzeit'].str.strip()
df['Datum_Uhrzeit'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'], format='%d.%m.%y %H:%M', errors='coerce')
df.set_index('Datum_Uhrzeit', inplace=True)

# Convert to numeric and calculate 'Wirkleistung'
df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']] = df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']].apply(pd.to_numeric, errors='coerce')
df['cos_phi'] = df['P L Sum'] / df['S L Sum']
df['Wirkleistung'] = (df['U L1'] * df['I L1'] + df['U L2'] * df['I L2'] + df['U L3'] * df['I L3']) * df['cos_phi']
df['Wirkleistung'] = df['Wirkleistung'] / 1000  # Convert to kW

# Categorize time period
df['time_period'] = df.apply(lambda row: 'winter' if row.name.month == 11 or row.name.month <= 3 else 'sommer' if 5 <= row.name.month <= 9 else 'übergang', axis=1)

# Group by day of the week and time
df['day_of_week'] = df.index.dayofweek
df['time'] = df.index.time

# Split data into workdays, Saturday, and Sunday
workdays = df[df['day_of_week'] < 5]
saturday = df[df['day_of_week'] == 5]
sunday = df[df['day_of_week'] == 6]

# Define a function for plotting
def plot_wirkleistung(data, title, start_index=0):
    # Filter data by time period
    data_winter = data[data['time_period'] == 'winter']
    data_summer = data[data['time_period'] == 'sommer']
    data_transition = data[data['time_period'] == 'übergang']
    
    # Create time index mapping
    time_range = sorted(set(data['time']))
    time_indices = np.arange(len(time_range))
    
    # Resample each time period group and check for non-empty data before plotting
    if not data_winter.empty:
        winter_resampled = data_winter.groupby('time')['Wirkleistung'].mean()
        plt.plot(time_indices[:len(winter_resampled)], winter_resampled, label='Winter', color='black')
    
    if not data_summer.empty:
        summer_resampled = data_summer.groupby('time')['Wirkleistung'].mean()
        plt.plot(time_indices[:len(summer_resampled)], summer_resampled, label='Sommer', color='gray')
    
    if not data_transition.empty:
        transition_resampled = data_transition.groupby('time')['Wirkleistung'].mean()
        plt.plot(time_indices[:len(transition_resampled)], transition_resampled, label='Übergang', color='white', linestyle='--')
    
    plt.title(title)
    plt.xlabel('Tageszeit')
    plt.ylabel('Wirkleistung [kW]')
    plt.legend()

# Plot for each group
plt.figure(figsize=(18, 6))

# Workdays
plt.subplot(1, 3, 1)
plot_wirkleistung(workdays, 'Wirkleistung Arbeitstage (Mo-Fr)')

# Saturday
plt.subplot(1, 3, 2)
plot_wirkleistung(saturday, 'Wirkleistung Samstag')

# Sunday
plt.subplot(1, 3, 3)
plot_wirkleistung(sunday, 'Wirkleistung Sonntag')

plt.tight_layout()
plt.show()

# Save the updated DataFrame to a CSV file
output_file_path = 'data/Transformator_Alle_Updated.csv'  # Adjusted file extension
df.reset_index().to_csv(output_file_path, index=False)
