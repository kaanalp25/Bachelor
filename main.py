import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Stelle sicher, dass das Verzeichnis 'data' existiert
input_file_path = 'data/Transformator_Alle.csv'  # Definiere den Eingabedateipfad
output_file_path = 'data/Transformator_Alle_Updated.csv'  # Definiere den Ausgabedateipfad
os.makedirs('data', exist_ok=True)

# Laden und verarbeiten vom Datensatz
df = pd.read_csv(input_file_path, delimiter=';', decimal=',')
df['Datum'] = df['Datum'].str.strip()
df['Uhrzeit'] = df['Uhrzeit'].str.strip()
df['Datum_Uhrzeit'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'], format='%d.%m.%y %H:%M', errors='coerce')
df.set_index('Datum_Uhrzeit', inplace=True)

# Numerische Umwandlung und Berechnung der 'Wirkleistung'
df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']] = df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']].apply(pd.to_numeric, errors='coerce')
df['cos_phi'] = df['P L Sum'] / df['S L Sum']
df['Wirkleistung'] = (df['U L1'] * df['I L1'] + df['U L2'] * df['I L2'] + df['U L3'] * df['I L3']) * df['cos_phi']
df['Wirkleistung'] = df['Wirkleistung'] / 1000  # Umrechnung in kW

# Funktion zur Kategorisierung des Zeitraums
def categorize_time_period(row):
    date = row.name.date()  # Extrahiere das Datum aus dem Index
    if date.month == 11 or date.month <= 3:
        return 'winter'
    elif 5 <= date.month <= 9:
        return 'sommer'
    else:
        return 'übergang'

# Anwenden der Zeitraum-Kategorisierung
df['time_period'] = df.apply(categorize_time_period, axis=1)

# Daten nach Wochentag gruppieren und auf 15-Minuten-Intervalle umstellen
df['day_of_week'] = df.index.dayofweek
df['time'] = df.index.time

# Daten in Arbeitstage, Samstag und Sonntag aufteilen
workdays = df[df['day_of_week'] < 5]
saturday = df[df['day_of_week'] == 5]
sunday = df[df['day_of_week'] == 6]

# Daten für jede Gruppe neu sampeln
workdays_resampled = workdays.groupby('time')['Wirkleistung'].mean()
saturday_resampled = saturday.groupby('time')['Wirkleistung'].mean()
sunday_resampled = sunday.groupby('time')['Wirkleistung'].mean()

# Funktion zur Abbildung von Zeit auf einen kontinuierlichen numerischen Bereich
def map_time_to_range(time_series, start):
    time_to_num = {time: i + start for i, time in enumerate(sorted(set(time_series)))}
    return time_series.map(time_to_num), len(time_to_num)

# Zeiten für Arbeitstage, Samstag und Sonntag auf numerische Bereiche abbilden
workdays_mapped, workdays_len = map_time_to_range(workdays_resampled.index, 0)
saturday_mapped, saturday_len = map_time_to_range(saturday_resampled.index, workdays_len)
sunday_mapped, sunday_len = map_time_to_range(sunday_resampled.index, workdays_len + saturday_len)

# Diagramm erstellen
plt.figure(figsize=(12, 6))
plt.plot(workdays_mapped, workdays_resampled, label='Arbeitstage (Mo-Fr)', color='blue')
plt.plot(saturday_mapped + workdays_len, saturday_resampled, label='Samstag', color='green')  # Kontinuität angepasst
plt.plot(sunday_mapped + workdays_len + saturday_len, sunday_resampled, label='Sonntag', color='red')  # Kontinuität angepasst

# Anpassen der X-Achsen-Beschriftungen und -Ticks
# Ticks am Anfang jedes Zeitraums setzen: Arbeitstage, Samstag, Sonntag
ticks = [0, workdays_len, workdays_len + saturday_len]
labels = ['Arbeitstage', 'Samstag', 'Sonntag']
plt.xticks(ticks, labels)

plt.title('Durchschnittliche Wirkleistung in 15-Minuten-Intervallen')
plt.ylabel('Wirkleistung [kW]')
plt.legend()
plt.tight_layout()
plt.show()

# Speichern des aktualisierten DataFrames in eine Excel-Datei
df.reset_index().to_excel(output_file_path, index=False)  # Index zurücksetzen, um 'Datum_Uhrzeit' als Spalte zu behalten
