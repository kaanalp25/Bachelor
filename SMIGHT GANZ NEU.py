import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os
import matplotlib.pyplot as plt
import holidays

# Basispfad und Dateistruktur definieren
base_path = '/Users/kaanalpilgar/Desktop/EVO/Daten Smight & GridCal/Smight/Messreihen 18.02-25.02/Weilerstraße 79/'
file_name_structure = '2024-02-{}_0000W315__Weilerstraße_79__46049_Oberhausen__Germany_{}.csv'
output_file_name = 'final_combined_table.csv'  # Name der finalen Datei

# Start- und Enddatum festlegen
start_date = datetime(2024, 2, 18)
end_date = datetime(2024, 2, 25)

# Liste für gesammelte DataFrames erstellen
all_data_frames = []

# Spalten, die skaliert werden sollen
columns_to_scale = ['L1_active', 'L2_active', 'L3_active', 'L1', 'L2', 'L3']

# Über den festgelegten Zeitraum iterieren
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime('%d')
    try:
        file_name_1 = file_name_structure.format(date_str, 'I')
        file_name_2 = file_name_structure.format(date_str, 'U')
        full_path_1 = os.path.join(base_path, file_name_1)
        full_path_2 = os.path.join(base_path, file_name_2)

        try:
            data1 = pd.read_csv(full_path_1, delimiter=';', encoding='utf-8')
        except UnicodeDecodeError:
            data1 = pd.read_csv(full_path_1, delimiter=';', encoding='latin1')

        data1.columns = data1.columns.str.strip()
        data1['Time'] = pd.to_datetime(data1['Time'])
        data1_grouped = data1.groupby(data1['Time'].dt.floor('Min')).mean()
        data1_grouped = data1_grouped.round(0).astype(int)

        try:
            data2 = pd.read_csv(full_path_2, delimiter=';', encoding='utf-8')
        except UnicodeDecodeError:
            data2 = pd.read_csv(full_path_2, delimiter=';', encoding='latin1')

        data2.columns = data2.columns.str.strip()
        data2['Time'] = pd.to_datetime(data2['Time'])

        combined_data = pd.merge(data1_grouped, data2[['Time', 'Voltage [mV]']], left_index=True, right_on='Time', how='left')
        combined_data = combined_data[['Time'] + [col for col in combined_data.columns if col != 'Time']]
        all_data_frames.append(combined_data)

    except FileNotFoundError as e:
        print(f"Datei für das Datum {current_date.strftime('%Y-%m-%d')} nicht gefunden: {e}")
    except Exception as e:
        print(f"Fehler aufgetreten für das Datum {current_date.strftime('%Y-%m-%d')}: {e}")

    current_date += timedelta(days=1)

final_combined_data = pd.concat(all_data_frames, ignore_index=True)
final_combined_data.drop(columns=['Transformer ID', 'Low Voltage', 'Distributor ID', 'Outlet', 'Time_x', 'Time_y', 'Low Voltage Distributor ID'], errors='ignore', inplace=True)

for column in columns_to_scale:
    final_combined_data[column] /= 100
final_combined_data['Voltage [mV]'] /= 1000

final_combined_data.rename(columns={
    'L1_active': 'L1_active (A)',
    'L2_active': 'L2_active (A)',
    'L3_active': 'L3_active (A)',
    'L1': 'L1 (A)',
    'L2': 'L2 (A)',
    'L3': 'L3 (A)',
    'Voltage [mV]': 'Voltage (V)'
}, inplace=True)

final_combined_data['cos_phi_L1'] = final_combined_data['L1_active (A)'] / final_combined_data['L1 (A)']
final_combined_data['cos_phi_L2'] = final_combined_data['L2_active (A)'] / final_combined_data['L2 (A)']
final_combined_data['cos_phi_L3'] = final_combined_data['L3_active (A)'] / final_combined_data['L3 (A)']

final_combined_data['P_L_Sum (kW)'] = (final_combined_data['Voltage (V)'] * final_combined_data[['L1_active (A)', 'L2_active (A)', 'L3_active (A)']].multiply(final_combined_data[['cos_phi_L1', 'cos_phi_L2', 'cos_phi_L3']].values, axis=1).sum(axis=1)) / 1000
final_combined_data['S_L_Sum (kW)'] = (final_combined_data['Voltage (V)'] * final_combined_data[['L1 (A)', 'L2 (A)', 'L3 (A)']].sum(axis=1)) / 1000
final_combined_data['Q_L_Sum (kW)'] = np.sqrt(np.maximum(final_combined_data['S_L_Sum (kW)']**2 - final_combined_data['P_L_Sum (kW)']**2, 0))

final_combined_data.set_index('Time', inplace=True)
resampled_data = final_combined_data.resample('15min').mean()
resampled_data.reset_index(inplace=True)

# Durchschnitt der Wirkleistung für jede 15-Minuten-Periode über alle Tage berechnen
average_power = resampled_data.groupby(resampled_data['Time'].dt.time)['P_L_Sum (kW)'].mean()

# Wochentage zuordnen
weekdays = {0: 'Montag', 1: 'Dienstag', 2: 'Mittwoch', 3: 'Donnerstag', 4: 'Freitag', 5: 'Samstag', 6: 'Sonntag'}
resampled_data['Wochentag'] = resampled_data['Time'].dt.dayofweek.map(weekdays)

# Feiertage berücksichtigen
de_holidays = holidays.Germany(prov='NW')
resampled_data['is_holiday'] = resampled_data['Time'].dt.date.apply(lambda x: x in de_holidays)

# Glättung mit gleitendem Durchschnitt
smoothed_power = average_power.rolling(window=4, min_periods=1, center=True).mean()

# Daten für den neuen Graphen vorbereiten
time_labels = smoothed_power.index.astype(str)
power_averages = smoothed_power.values

# Definiere den Ausgabepfad für die resampelten Daten und die Plots
output_resampled_path = os.path.join(base_path, 'resampled_' + output_file_name)
plot_path = os.path.join(os.path.dirname(output_resampled_path), 'Power_Averages.png')

# Daten plotten
fig, axes = plt.subplots(2, 1, figsize=(12, 12))

axes[0].plot(resampled_data['Time'], resampled_data['P_L_Sum (kW)'], label='Resampelte Wirkleistung')
axes[0].set_xlabel('Zeit')
axes[0].set_ylabel('Wirkleistung (kW)')
axes[0].set_title('Wirkleistung über Zeit (15-Minuten-Intervalle)')
axes[0].grid(True)
axes[0].legend()

# Unterer Graph ohne Datenpunkte, geglättet
axes[1].plot(time_labels, power_averages, linestyle='-')
axes[1].set_xlabel('Uhrzeit')
axes[1].set_ylabel('Wirkeistung (kW)')
axes[1].set_title('Geglättete durchschnittliche Wirkleistung für jede 15-Minuten-Periode')
axes[1].grid(True)

# Setze x-Achsen-Ticks nur bei vollen Stunden
full_hour_ticks = [t for t in time_labels if t.endswith(':00:00')]
axes[1].set_xticks(full_hour_ticks)
axes[1].set_xticklabels([t[:-3] for t in full_hour_ticks])  # Entferne Sekunden aus der Anzeige
axes[1].tick_params(axis='x', rotation=45)

#Passt das Layout des Plots an
plt.tight_layout()
plt.savefig(plot_path)
plt.show()

# Resampelte Daten speichern
resampled_data.to_csv(output_resampled_path, index=False)
print(f"Resampelte Daten gespeichert in {output_resampled_path}")
print(f"Plot gespeichert in {plot_path}")
