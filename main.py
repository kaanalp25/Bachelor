import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Function to determine the season for a given date
def get_season(date):
    if pd.isnull(date):
        return 'Unknown'
    month, day = date.month, date.day
    if (11 <= month <= 12) or (1 <= month <= 3 and day <= 20):
        return 'Winter'
    elif (5 <= month <= 9) or (month == 10 and day <= 14):
        return 'Sommer'
    elif (3 <= month <= 5 and day >= 21) or (9 <= month <= 11 and day >= 15):
        return 'Übergang'
    return 'Unknown'

# Read the CSV data into a pandas DataFrame
df = pd.read_csv('Transformator_Alle.csv', delimiter=';', decimal=',')

# Strip any potential leading/trailing whitespace and convert columns
df['Datum'] = df['Datum'].str.strip()
df['Uhrzeit'] = df['Uhrzeit'].str.strip()
df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']] = df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']].apply(pd.to_numeric, errors='coerce')

# Calculate 'Wirkleistung' and power factor
df['cos_phi'] = df['P L Sum'] / df['S L Sum']
df['Wirkleistung'] = (df['U L1'] * df['I L1'] + df['U L2'] * df['I L2'] + df['U L3'] * df['I L3']) * df['cos_phi']

# Convert 'Datum' and 'Uhrzeit' to datetime and extract the weekday
df['Datetime'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'], format='%d.%m.%y %H:%M', errors='coerce')
df['Weekday'] = df['Datetime'].dt.day_name()

# Determine the season for each row
df['Season'] = df['Datetime'].apply(get_season)

# Group by Weekday and Season for average 'Wirkleistung'
seasonal_avg = df.groupby(['Weekday', 'Season'])['Wirkleistung'].mean().reset_index()

# Save the DataFrame with Wirkleistung, Weekday, and Season
df.to_csv('updated_data_with_wirkleistung_weekday_season.csv', index=False)

# Save the seasonal averages
seasonal_avg.to_csv('seasonal_avg_wirkleistung.csv', index=False)

# Inspect rows where 'Datetime' could not be parsed
print("1")
print(df[pd.isnull(df['Datetime'])])
print(60*"-")

print("2")
print(df[df['Datetime'].isna() & df['Datum'].notna()])

# Plot the 'Wirkleistung' over time
# plt.figure(figsize=(10, 5))
# plt.plot(df['Datetime'], df['Wirkleistung'], label='Wirkleistung', linestyle='-', linewidth=0.1)
# plt.xlabel('Date and Time')
# plt.ylabel('Wirkleistung (Active Power)')
# plt.title('Wirkleistung over Time')
# plt.legend()
# plt.grid(True)
# plt.show()
