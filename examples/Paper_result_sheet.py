# -*- coding: utf-8 -*-
# Copyright 2026 O. Hofstaetter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

import os
import sys
from openbalance import Session
from openbalance.io.readers.open_balance import OpenBalanceReader
from openbalance.processing.filters import apply_lowpass_filter
from openbalance.visualization.plots import plot_cop_path
from openbalance.io.writers.pdf_report import generate_balance_report
from openbalance.processing.kinematics import calculate_cop, aggregate_openbalance_quadrants, calculate_wdi, calculate_path_length, calculate_sway_areas

def read_metadata(filepath):
    """Hilfsfunktion, um die questions.txt einzulesen."""
    meta = {}
    if os.path.exists(filepath):
        # Versuche zuerst UTF-8, bei Fehler Fallback auf Windows (cp1252)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='cp1252') as f:
                lines = f.readlines()

        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip()
    return meta

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Pfad aus Argumenten lesen (falls per subprocess übergeben)
    if len(sys.argv) > 1:
        DATEN_DIR = sys.argv[1]
    else:
        # Fallback: Standard-Ordner "Messdaten" im Skript-Verzeichnis
        DATEN_DIR = os.path.join(BASE_DIR, "Messdaten\Data_20260817-114544_Muster")

    print(f"Verarbeite Messdaten aus: {DATEN_DIR}")
    
    print(f"--- Starte OpenBalance Auswertung ---")

    # Session initialisieren
    questions_path = os.path.join(DATEN_DIR, "questions.txt")
    patient_meta = read_metadata(questions_path)
    session = Session(patient_metadata=patient_meta)

    reader = OpenBalanceReader()

    # =========================================================================
    # OPENBALANCE SENSOR KOORDINATEN (F1 bis F16 in exakter Reihenfolge)
    # Zentren: X =  11.5 | Y_Heel = -7.0 | Y_Forefoot = +10.7
    # =========================================================================
    dx, dy = 4.0, 4.0

    sensor_coords = [
        (-11.5 - dx, -7.0 - dy),  # F1
        (-11.5 + dx, -7.0 - dy),  # F2
        (-11.5 + dx, -7.0 + dy),  # F3
        (-11.5 + dx, 10.7 - dy),  # F4
        (-11.5 + dx, 10.7 + dy),  # F5
        (-11.5 - dx, 10.7 + dy),  # F6
        (-11.5 - dx, 10.7 - dy),  # F7
        (-11.5 - dx, -7.0 + dy),  # F8
        ( 11.5 - dx, -7.0 - dy),  # F9
        ( 11.5 + dx, -7.0 - dy),  # F10
        ( 11.5 + dx, -7.0 + dy),  # F11
        ( 11.5 + dx, 10.7 - dy),  # F12
        ( 11.5 + dx, 10.7 + dy),  # F13
        ( 11.5 - dx, 10.7 + dy),  # F14
        ( 11.5 - dx, 10.7 - dy),  # F15
        ( 11.5 - dx, -7.0 + dy)   # F16
    ]

    # Schleife  ber alle 8 Messungen
    for i in range(1, 9):
        file_path = os.path.join(DATEN_DIR, f"M{i}.txt")
        
        if os.path.exists(file_path):
            print(f"[OK] Lese M{i}.txt...")
            trial = reader.read(file_path, sample_rate=100)
            trial.condition = f"M{i}"
            
            apply_lowpass_filter(trial, cutoff_freq=13.0)
            calculate_cop(trial, sensor_coords)
            # --- NEU: Parameter Berechnen ---
            # 1. WDI
            quads = aggregate_openbalance_quadrants(trial)
            calculate_wdi(trial, quads['LF'], quads['RF'], quads['LH'], quads['RH'])
            
            # 2. Pfadl nge
            calculate_path_length(trial)
            
            # 3. ROM
            calculate_sway_areas(trial)
            
            session.add_trial(trial)
        else:
            print(f"[FEHLT] Datei nicht gefunden: M{i}.txt")

    if not session.trials:
        print("\nABBRUCH: Keine Messungen gefunden!")
        exit()

    # 3. Plots erzeugen (mit globaler Achsenskalierung)
    temp_plot_dir = os.path.join(BASE_DIR, "temp_plots")
    os.makedirs(temp_plot_dir, exist_ok=True)

    # --- A) Globale Skalierung berechnen ---
    import numpy as np # (Falls oben noch nicht importiert)
    all_cop_x, all_cop_y = [], []
    
    for t in session.trials:
        if 'COP_x' in t.parameters:
            all_cop_x.extend(t.parameters['COP_x'])
            all_cop_y.extend(t.parameters['COP_y'])

    if all_cop_x and all_cop_y:
        # Finde absolute R nder  ber alle Messungen hinweg
        x_min, x_max = np.nanmin(all_cop_x), np.nanmax(all_cop_x)
        y_min, y_max = np.nanmin(all_cop_y), np.nanmax(all_cop_y)

        # Bestimme das Zentrum und die gr  te Spannweite, 
        # damit der Plot perfekt quadratisch bleibt!
        x_center = (x_max + x_min) / 2.0
        y_center = (y_max + y_min) / 2.0
        max_range = max(x_max - x_min, y_max - y_min) / 2.0
        
        padding = 1.0 # 1 cm Rand als Puffer
        
        global_limits = (
            x_center - max_range - padding, 
            x_center + max_range + padding, 
            y_center - max_range - padding, 
            y_center + max_range + padding
        )
    else:
        global_limits = None

    # --- B) Bilder mit festen Limits speichern ---
    for trial in session.trials:
        save_path = os.path.join(temp_plot_dir, f"plot_{trial.condition}.png")
        
        #  bergabe der errechneten Grenzen!
        plot_cop_path(trial, save_path, axis_limits=global_limits) 
        trial.parameters['plot_path'] = save_path

    # PDF generieren
    output_pdf = os.path.join(BASE_DIR, "Ergebnisbericht2.pdf")
    generate_balance_report(session, output_pdf)
    print(f"\nFERTIG! PDF erstellt: {output_pdf}")

