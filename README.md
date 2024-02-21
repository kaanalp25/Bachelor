Für die Aktualisierung der `README.md` Datei auf Deutsch, basierend auf dem bereitgestellten Code und der vorhandenen Beschreibung, könnten Sie folgenden Inhalt verwenden. Die Aktualisierung beinhaltet Informationen zur Verwendung der Gauss'schen Glättung zur Reduzierung von Rauschen in den Plots sowie die Hinzufügung der Abhängigkeit von `scipy` für die Gauss'sche Filterfunktion.

---

# Bachelorarbeit

## Beschreibung

Diese Bachelorarbeit beschäftigt sich mit der Analyse und Visualisierung elektrischer Messdaten. Durch den Einsatz von Datenverarbeitung und statistischen Methoden werden Einsichten in die Leistungsverbrauchsmuster gewonnen. Speziell wird die Gauss'sche Glättung angewendet, um das Rauschen in den Visualisierungen der Wirkleistung zu reduzieren und die Trends klarer hervorzuheben.

## Erste Schritte

### Voraussetzungen

- Python 3.8+
- Pandas
- Matplotlib
- Numpy
- Scipy

### Installation

Zur Nutzung dieses Projekts müssen zunächst die benötigten Bibliotheken installiert werden. Dies kann durch Ausführen des folgenden Befehls im Terminal erreicht werden:

```bash
pip install pandas matplotlib numpy scipy
```

* Dieses Repository klonen oder die Zip-Datei herunterladen.

### Ausführen des Programms

Nach der Installation der Abhängigkeiten kann das Hauptskript über die Befehlszeile ausgeführt werden:

```bash
python main.py
```

## Funktionen und Nutzung

- **Datenverarbeitung**: Einlesen und Vorverarbeiten von elektrischen Messdaten.
- **Berechnung der Wirkleistung**: Die Wirkleistung wird aus den gegebenen elektrischen Messwerten berechnet.
- **Saisonale Analyse**: Datenpunkte werden basierend auf dem Datum in Saisons eingeteilt, und saisonale Durchschnittswerte der Wirkleistung werden berechnet.
- **Glättung der Daten**: Anwendung der Gauss'schen Glättung, um das Rauschen in den Plots zu reduzieren und die Datenvisualisierung zu verbessern.
- **Visualisierung**: Erstellung von Plots zur Darstellung der Wirkleistung über verschiedene Zeiträume mit unterschiedlichen Saisons.

Für Rückfragen und weitere Informationen:

- Kaan Alp Ilgar
- [kaanalp_25@hotmail.de](mailto:kaanalp_25@hotmail.de)

## Lizenz

Dieses Projekt ist unter der [MIT Lizenz](LICENSE.txt) lizenziert. Für mehr Details, siehe die LICENSE-Datei.

## Danksagungen

Ein besonderer Dank geht an die folgenden Ressourcen, die für die Erstellung dieses Projekts unerlässlich waren:

- [Pandas Dokumentation](https://pandas.pydata.org/pandas-docs/stable/)
- [Matplotlib Dokumentation](https://matplotlib.org/stable/contents.html)
- [Scipy Dokumentation](https://docs.scipy.org/doc/scipy/reference/)