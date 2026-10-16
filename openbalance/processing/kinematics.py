# -*- coding: utf-8 -*-
# Copyright 2026 O. Hofstaetter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

import numpy as np
from scipy.spatial import ConvexHull
from scipy.stats import chi2

def calculate_cop(trial, sensor_coordinates: list):
    """
    Berechnet den generischen Center of Pressure (COP) fr alle Kanle.
    """
    if trial.filtered_data is None:
        raise ValueError("Daten mssen gefiltert werden, bevor der COP berechnet wird!")
    
    if len(sensor_coordinates) != trial.filtered_data.shape[1]:
        raise ValueError("Anzahl der Koordinaten muss der Anzahl der Kanle entsprechen!")

    # Gesamtkraft Fz (Summe aller Sensoren pro Zeitschritt)
    F_total = np.sum(trial.filtered_data, axis=1)
    
    # Verhindern von Division durch Null
    F_total[F_total == 0] = np.nan 
    
    cop_x = np.zeros(len(F_total))
    cop_y = np.zeros(len(F_total))
    
    # COP = Summe(Kraft_i * Koordinate_i) / Gesamtkraft
    for i, (x, y) in enumerate(sensor_coordinates):
        force_i = trial.filtered_data[:, i]
        cop_x += force_i * x
        cop_y += force_i * y
        
    cop_x = cop_x / F_total
    cop_y = cop_y / F_total
    
    # Ergebnisse als Numpy-Arrays im Trial speichern
    trial.parameters['COP_x'] = cop_x
    trial.parameters['COP_y'] = cop_y
    
    return trial

def aggregate_openbalance_quadrants(trial):
    """
    Summiert die 16 Zellen des OpenBalance Systems zu 4 Quadranten fr WDI.
    Indizes basieren auf: LF (4-7), RF (12-15), LH (1-3, 8), RH (9-11, 16)
    Achtung: Python Indizes starten bei 0! (F1 = 0, F16 = 15)
    """
    fd = trial.filtered_data
    
    quadrants = {
        'LF': fd[:, 3] + fd[:, 4] + fd[:, 5] + fd[:, 6],
        'RF': fd[:, 11] + fd[:, 12] + fd[:, 13] + fd[:, 14],
        'LH': fd[:, 0] + fd[:, 1] + fd[:, 2] + fd[:, 7],
        'RH': fd[:, 8] + fd[:, 9] + fd[:, 10] + fd[:, 15]
    }
    return quadrants

def calculate_wdi(trial, force_lf, force_rf, force_lh, force_rh):
    """
    Berechnet den Weight Distribution Index (WDI) aus 4 Quadranten.
    """
    F_total = force_lf + force_rf + force_lh + force_rh
    F_total = np.where(F_total == 0, np.nan, F_total)
    
    WD_lf = (force_lf / F_total) * 100
    WD_rf = (force_rf / F_total) * 100
    WD_lh = (force_lh / F_total) * 100
    WD_rh = (force_rh / F_total) * 100
    
    wdi_per_timestep = np.sqrt(
        ((WD_lf - 25)**2 + (WD_rf - 25)**2 + (WD_lh - 25)**2 + (WD_rh - 25)**2) / 4
    )
    
    trial.parameters['WDI'] = np.nanmean(wdi_per_timestep)
    trial.parameters['WD_LF_mean'] = np.nanmean(WD_lf)
    trial.parameters['WD_RF_mean'] = np.nanmean(WD_rf)
    trial.parameters['WD_LH_mean'] = np.nanmean(WD_lh)
    trial.parameters['WD_RH_mean'] = np.nanmean(WD_rh)
    
    return trial

def calculate_path_length(trial):
    """
    Berechnet die Pfadlänge (Path Length / COFTL) des COP-Verlaufs in cm.
    """
    if 'COP_x' not in trial.parameters or 'COP_y' not in trial.parameters:
        raise ValueError("COP muss vor der Pfadlänge berechnet werden!")

    x = trial.parameters['COP_x']
    y = trial.parameters['COP_y']

    # Vektorisierte Berechnung der Distanz (entspricht exakt deiner alten for-Schleife)
    # np.diff(x) berechnet automatisch x[t] - x[t-1] für das gesamte Array
    distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
    
    # nansum ignoriert fehlerhafte (NaN) Werte, falls der Patient kurz nicht auf der Platte stand
    total_length = np.nansum(distances) 

    # Im Trial abspeichern
    trial.parameters['Path_Length'] = total_length
    
    return trial

def calculate_sway_areas(trial, probability=0.95):
    """
    Calculates the sway area using three different established methodologies:
    1. Convex Hull Area
    2. 95% Prediction Ellipse Area (Schubert & Kirchner, 2014)
    3. 95% Confidence Circle Area (Prieto et al., 1996)
    """
    if 'COP_x' not in trial.parameters or 'COP_y' not in trial.parameters:
        raise ValueError("COP must be calculated before computing areas!")

    x = trial.parameters['COP_x']
    y = trial.parameters['COP_y']

    # Remove NaNs
    valid_mask = ~np.isnan(x) & ~np.isnan(y)
    x_valid = x[valid_mask]
    y_valid = y[valid_mask]

    if len(x_valid) < 3:
        trial.parameters['Area_Hull'] = 0.0
        trial.parameters['Area_Ellipse'] = 0.0
        trial.parameters['Area_Circle'] = 0.0
        return trial

    # --- 1. Convex Hull ---
    points = np.column_stack((x_valid, y_valid))
    hull = ConvexHull(points)
    trial.parameters['Area_Hull'] = hull.volume
    trial.parameters['Hull_Object'] = hull
    trial.parameters['Hull_Points'] = points

    # --- 2. Prediction Ellipse (Schubert & Kirchner, 2014) ---
    cov_mat = np.cov(x_valid, y_valid)
    eigenvalues, eigenvectors = np.linalg.eig(cov_mat)
    chisquare = chi2.ppf(probability, df=2) # chi-square value for 2 degrees of freedom
    
    area_ellipse = np.pi * chisquare * np.sqrt(np.abs(np.prod(eigenvalues)))
    
    trial.parameters['Area_Ellipse'] = area_ellipse
    trial.parameters['Ellipse_Eigenvalues'] = eigenvalues
    trial.parameters['Ellipse_Eigenvectors'] = eigenvectors
    trial.parameters['Ellipse_Chi2'] = chisquare

    # --- 3. Confidence Circle (Prieto et al., 1996) ---
    x_mean, y_mean = np.mean(x_valid), np.mean(y_valid)
    distances = np.sqrt((x_valid - x_mean)**2 + (y_valid - y_mean)**2)
    
    mdist = np.mean(distances)
    s_rd = np.std(distances, ddof=1)
    
    # 1.645 represents the z-score for a one-sided 95% confidence limit
    r_cc = mdist + 1.645 * s_rd  
    area_circle = np.pi * (r_cc ** 2)
    
    trial.parameters['Area_Circle'] = area_circle
    trial.parameters['Circle_Radius'] = r_cc

    # --- NEU: Outlier Excursion Parameter ---
    area_hull = trial.parameters['Area_Hull']
    area_ellipse = trial.parameters['Area_Ellipse']
    
    # 1. Absolute Flächendifferenz
    trial.parameters['Area_Diff'] = area_hull - area_ellipse
    
    # 2. Dimensionsloses Flächenverhältnis (Verhindert Division durch Null)
    if area_ellipse > 0:
        trial.parameters['Area_Ratio'] = area_hull / area_ellipse
    else:
        trial.parameters['Area_Ratio'] = 0.0

    return trial