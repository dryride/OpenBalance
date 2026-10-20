# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from openbalance.io.readers.base import BaseReader
from openbalance.core.trial import Trial

class AmtiCsvReader(BaseReader):
    """
    A custom reader for AMTI measurement data in .csv format.
    Reads Fx, Fy, Fz, Mx, My, Mz, COPx and COPy.
    """
    
    def read(self, filepath: str, sample_rate: float = 1000.0) -> Trial:
        """
        Reads an AMTI CSV file and returns a Trial object, 
        which is compatible with the openbalance library.
        """
        try:
            # Nutzt genau deine erfolgreich getestete, robuste Pandas-Variante
            df = pd.read_csv(filepath, sep=';', decimal=',')
            data = df.to_numpy(dtype=float)
        except Exception as e:
            raise ValueError(f"Error reading the file {filepath} with pandas: {e}")
            
        if data.shape[1] < 8:
            raise ValueError(f"Could not find enough columns in {filepath} (expected at least 8).")

        # Die Kanal-Namen in exakt der Reihenfolge der AMTI-Daten
        channel_names = ['F_x', 'F_y', 'F_z', 'M_x', 'M_y', 'M_z', 'COP_x', 'COP_y']
        
        # Saubere Initialisierung wie im OpenBalanceReader
        trial = Trial(
            raw_data=data[:, :8],
            sample_rate=sample_rate,
            channel_names=channel_names
        )
        
        trial.condition = "Unknown"
        trial.duration = len(data) / sample_rate
        
        # Fallback: Falls einige deiner Skripte die Werte zwingend im 'parameters'-Dict 
        # erwarten (und die Trial-Basisklasse dies nicht automatisch mappt), setzen wir es manuell.
        if not hasattr(trial, 'parameters'):
            trial.parameters = {}
        for i, name in enumerate(channel_names):
            trial.parameters[name] = data[:, i]
        
        return trial
