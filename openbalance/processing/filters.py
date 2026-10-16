# Copyright 2026 O. Hofstätter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Modul zur Signalfilterung von Posturographie-Daten.
"""

import numpy as np
import scipy.signal

def apply_lowpass_filter(trial, cutoff_freq=13.0, order=2):
    """
    Wendet einen Butterworth-Tiefpassfilter auf die Rohdaten eines Trials an.
    Das Ergebnis wird im Attribut 'filtered_data' des Trials gespeichert.
    
    :param trial: Das Trial-Objekt, das die raw_data und sample_rate enthält.
    :param cutoff_freq: Die Grenzfrequenz in Hz (Standard: 13 Hz laut Literatur).
    :param order: Die Ordnung des Filters.
    :return: Das veränderte Trial-Objekt (für Chaining).
    """
    if trial.raw_data is None or len(trial.raw_data) == 0:
        raise ValueError("Das Trial enthält keine Rohdaten zum Filtern.")
        
    fs = trial.sample_rate
    nyq = 0.5 * fs
    normal_cutoff = cutoff_freq / nyq
    
    # Filterkoeffizienten berechnen
    b, a = scipy.signal.butter(order, normal_cutoff, btype='low', analog=False)
    
    # filtfilt wendet den Filter vorwärts und rückwärts an (Phasenverschiebung = 0)
    # axis=0 bedeutet, dass entlang der Zeitachse (Spalten) gefiltert wird
    trial.filtered_data = scipy.signal.filtfilt(b, a, trial.raw_data, axis=0)
    
    return trial