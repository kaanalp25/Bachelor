import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import holidays
from scipy.ndimage import gaussian_filter1d

# Erstelle notwendige Verzeichnisse, falls sie nicht existieren
input_file_path = 'data/Transformator_Alle.csv'
os.makedirs('data', exist_ok=True)  # Datenverzeichnis für die Eingabedatei
os.makedirs('plots', exist_ok=True)  # Plotverzeichnis für die Ausgabegrafik

# Lade und verarbeite den Datensatz
df = pd.read_csv(input_file_path, delimiter=';', decimal=',')

# Bereinige Datum und Uhrzeit, kombiniere sie und konvertiere in datetime-Objekt
df['Datum'] = df['Datum'].str.strip()
df['Uhrzeit'] = df['Uhrzeit'].str.strip()
df['Datum_Uhrzeit'] = pd.to_datetime(df['Datum'] + ' ' + df['Uhrzeit'], format='%d.%m.%y %H:%M', errors='coerce')

# Identifiziere und zeige Zeilen mit ungültigen Datum_Uhrzeit-Werten (NaT)
nat_rows = df[df['Datum_Uhrzeit'].isna()]
if not nat_rows.empty:
    print("Zeilen mit NaT-Werten in 'Datum_Uhrzeit':")
    print(nat_rows[['Datum', 'Uhrzeit']])

# Entferne Zeilen mit ungültigen NaT-Werten
df = df.dropna(subset=['Datum_Uhrzeit'])
df.set_index('Datum_Uhrzeit', inplace=True)

# Konvertiere zu numerischen Werten und berechne neue Spalten
df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']] = df[['P L Sum', 'S L Sum', 'U L1', 'I L1', 'U L2', 'I L2', 'U L3', 'I L3']].apply(pd.to_numeric, errors='coerce')
df['cos_phi'] = df['P L Sum'] / df['S L Sum']
df['Wirkleistung'] = (df['U L1'] * df['I L1'] + df['U L2'] * df['I L2'] + df['U L3'] * df['I L3']) * df['cos_phi']
df['Wirkleistung'] = df['Wirkleistung'] / 1000  # Umrechnung in kW

# Kategorisiere nach Zeitraum (Winter, Sommer, Übergang)
df['time_period'] = df.index.to_series().apply(lambda dt: 'winter' if dt.month == 11 or dt.month <= 3 else 'sommer' if 5 <= dt.month <= 9 else 'übergang')

# Einfügen von Wochentagen und Uhrzeit als separate Spalte
df['day_of_week'] = df.index.dayofweek
df['time'] = df.index.time

# Einrichtung deutscher Feiertage 
de_holidays = holidays.Germany(prov='NW')

# Funktion zur Anpassung für Feiertage
def adjust_for_holidays(row):
    try:
        if row.name.date() in de_holidays or (row.name.date().month == 12 and row.name.date().day in [24, 31] and row.name.weekday() != 6):
            return 6 if row.name.date().weekday() != 6 else row['day_of_week']  # Behandle als Sonntag, es sei denn, es ist bereits Sonntag
        elif row.name.date().month == 12 and row.name.date().day in [24, 31]:
            return 5  # Behandle als Samstag
        return row['day_of_week']
    except Exception as e:
        print(f"Fehler bei der Verarbeitung der Zeile: {row.name}, Ausnahme: {e}")
        raise e

# Anwendung auf Feiertagsanpassung
df['day_of_week'] = df.apply(adjust_for_holidays, axis=1)

# Aufteilen der Daten in Arbeitstage, Samstag und Sonntag
workdays = df[df['day_of_week'] < 5]
saturday = df[df['day_of_week'] == 5]
sunday = df[df['day_of_week'] == 6]

# Funktion zum Erstellen und Anzeigen von Plots
def create_and_show_plots(workdays, saturday, sunday, sigma=2):
    plt.figure(figsize=(18, 12))

    # Erstelle Plots für Arbeitstage, Samstag und Sonntag
    plt.subplot(3, 3, 1)
    plot_wirkleistung(workdays, 'Wirkleistung Arbeitstage (Mo-Fr)', sigma)

    plt.subplot(3, 3, 2)
    plot_wirkleistung(saturday, 'Wirkleistung Samstag', sigma)

    plt.subplot(3, 3, 3)
    plot_wirkleistung(sunday, 'Wirkleistung Sonntag', sigma)

    # Erstelle Plots für einzelne Wochentage
    weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
    for i, day in enumerate(range(5), 3):
        plt.subplot(3, 3, i+1)
        plot_wirkleistung(df[df['day_of_week'] == day], f'Wirkleistung {weekdays[day]}', sigma)

    plt.tight_layout()
    plt.show()

# Funktion zur Darstellung der Wirkleistung mit Glättung
def plot_wirkleistung(data, title, sigma=2):
    # Filtern der Daten nach Zeitraum und andere Vorbereitungen
    data_winter = data[data['time_period'] == 'winter']
    data_summer = data[data['time_period'] == 'sommer']
    data_transition = data[data['time_period'] == 'übergang']
    # Erstelle eine Liste von Zeitmarken im 15-Minuten-Intervall
    time_range = pd.date_range(start='00:00', end='23:45', freq='15min').time
    time_indices = np.arange(len(time_range))

    # Mapping der Zeitstempel auf die X-Achsen-Indizes
    time_to_index = {time: index for index, time in enumerate(time_range)}

    if not data_winter.empty:
        # Gruppiere und berechne den Durchschnitt für die Wirkleistung, glätte die Daten
        winter_resampled = data_winter.groupby(data_winter.index.time)['Wirkleistung'].mean().reindex(time_range, fill_value=0)
        smoothed_winter = gaussian_filter1d(winter_resampled, sigma=sigma)
        plt.plot(time_indices, smoothed_winter, label='Winter', color='black')

    if not data_summer.empty:
        summer_resampled = data_summer.groupby(data_summer.index.time)['Wirkleistung'].mean().reindex(time_range, fill_value=0)
        smoothed_summer = gaussian_filter1d(summer_resampled, sigma=sigma)
        plt.plot(time_indices, smoothed_summer, label='Sommer', color='gray')

    if not data_transition.empty:
        transition_resampled = data_transition.groupby(data_transition.index.time)['Wirkleistung'].mean().reindex(time_range, fill_value=0)
        smoothed_transition = gaussian_filter1d(transition_resampled, sigma=sigma)
        plt.plot(time_indices, smoothed_transition, label='Übergang', color='white', linestyle='--')

    plt.title(title)
    plt.xlabel('Tageszeit')
    plt.ylabel('Wirkleistung [kW]')
    plt.legend()

    # Setze X-Achsen-Ticks und Labels für volle 2-Stunden-Intervalle
    two_hour_ticks = [time_to_index[time] for time in time_range if time.minute == 0 and time.hour % 2 == 0]  # Nur volle 2-Stunden-Intervalle
    plt.xticks(two_hour_ticks, [time.strftime('%H:%M') for time in time_range if time.minute == 0 and time.hour % 2 == 0])

# Generiere und zeige alle Plots an
create_and_show_plots(workdays, saturday, sunday, sigma=2)