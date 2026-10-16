# Copyright 2026 O. Hofstaetter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def plot_cop_path(trial, save_path, axis_limits=None):
    """
    Creates a 2D plot of the COP path including Hull, Ellipse, and Circle.
    """
    if 'COP_x' not in trial.parameters:
        return

    x = trial.parameters['COP_x']
    y = trial.parameters['COP_y']
    x_mean, y_mean = np.nanmean(x), np.nanmean(y)

    plt.figure(figsize=(5, 5))
    ax = plt.gca()
    
    # 1. COP Path (lightblue)
    ax.plot(x, y, linewidth=0.5, color='lightblue', label='COP Path')
    ax.plot(x_mean, y_mean, 'ro', markersize=6) 
    ax.plot([0, x_mean], [0, y_mean], 'r-', linewidth=2)
    
    # 2. Convex Hull (Black)
    if trial.parameters.get('Hull_Object') is not None:
        hull = trial.parameters['Hull_Object']
        points = trial.parameters['Hull_Points']
        for simplex in hull.simplices:
            ax.plot(points[simplex, 0], points[simplex, 1], 'k-', linewidth=1.5)
            
    # 3. Prediction Ellipse (Purple)
    if 'Ellipse_Eigenvalues' in trial.parameters:
        eigval = trial.parameters['Ellipse_Eigenvalues']
        eigvec = trial.parameters['Ellipse_Eigenvectors']
        chi2_val = trial.parameters['Ellipse_Chi2']
        
        width = 2 * np.sqrt(eigval[0] * chi2_val)
        height = 2 * np.sqrt(eigval[1] * chi2_val)
        angle = np.degrees(np.arctan2(eigvec[1, 0], eigvec[0, 0]))
        
        ellipse = patches.Ellipse((x_mean, y_mean), width, height, angle=angle,
                                  fill=False, color='purple', linestyle='-.', linewidth=2)
        ax.add_patch(ellipse)

    # 4. Confidence Circle (Green)
    if 'Circle_Radius' in trial.parameters:
        circle = patches.Circle((x_mean, y_mean), trial.parameters['Circle_Radius'],
                                fill=False, color='green', linestyle='--', linewidth=2)
        ax.add_patch(circle)

    # Formatting
    plt.title(f"COP Path - {trial.condition}", pad=15)
    plt.xlabel("Medio-Lateral (cm)")
    plt.ylabel("Anterior-Posterior (cm)")
    plt.axhline(y=0, color='k', linewidth=0.5, linestyle='--')
    plt.axvline(x=0, color='k', linewidth=0.5, linestyle='--')
    plt.grid(True, linestyle=':', alpha=0.6)
    
    ax.set_aspect('equal', adjustable='box')
    if axis_limits:
        plt.xlim(axis_limits[0], axis_limits[1])
        plt.ylim(axis_limits[2], axis_limits[3])
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()