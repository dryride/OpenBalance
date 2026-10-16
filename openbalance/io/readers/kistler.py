# Copyright 2026 O. Hofstätter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Reader für Kistler Kraftmessplatten (TSV/CSV Exporte).
"""

import pandas as pd
import numpy as np
from openbalance.io.readers.base import BaseReader
from openbalance.core.trial import Trial

class KistlerReader(BaseReader):
    
    def read(self, filepath: str, sample_rate=100.0) -> Trial:
        kg = 72.0  # Basisgewicht (Sollte im echten Verlauf dynamisiert werden)
        
        # Daten ab Zeile 17 einlesen (Tab-getrennt)
        df = pd.read_csv(filepath, header=17, sep='\t')
        df.drop(index=df.index[0], axis=0, inplace=True)
        
        # Kraftkomponenten konvertieren
        fz1 = np.asarray(df['Fz3'].astype(float)) / 9.81 + kg
        fz2 = np.asarray(df['Fz4'].astype(float)) / 9.81 + kg
        fz3 = np.asarray(df['Fz1'].astype(float)) / 9.81 + kg
        fz4 = np.asarray(df['Fz2'].astype(float)) / 9.81 + kg
        
        raw_data = np.column_stack((fz1, fz2, fz3, fz4))
        channel_names = ["Fz1", "Fz2", "Fz3", "Fz4"]
        
        return Trial(
            raw_data=raw_data, 
            sample_rate=sample_rate, 
            channel_names=channel_names
        )