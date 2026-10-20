# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

class AmtiCsvReader:
    """
    A custom reader for AMTI measurement data in .csv format.
    Reads Fx, Fy, Fz, Mx, My, Mz, COPx and COPy.
    """
    
    def __init__(self):
        pass

    def read(self, filepath, sample_rate=1000):
        """
        Reads an AMTI CSV file and returns a Trial object, 
        which is compatible with the openbalance library.
        """
        class Trial:
            def __init__(self):
                self.parameters = {}
                self.sample_rate = sample_rate
                self.condition = "Unknown"
        
        trial = Trial()
        
        try:
            # Uses exactly your successfully tested, robust variant
            data = pd.read_csv(filepath, sep=';', decimal=',').to_numpy(dtype=float)
        except Exception as e:
            raise ValueError(f"Error reading the file {filepath} with pandas: {e}")
            
        if data.shape[1] < 8:
            raise ValueError(f"Could not find enough columns in {filepath} (expected at least 8).")

        trial.parameters['F_x'] = data[:, 0]
        trial.parameters['F_y'] = data[:, 1]
        trial.parameters['F_z'] = data[:, 2]
        trial.parameters['M_x'] = data[:, 3]
        trial.parameters['M_y'] = data[:, 4]
        trial.parameters['M_z'] = data[:, 5]
        
        # IMPORTANT: The keys 'COP_x' and 'COP_y' are strictly 
        # required in the rest of the OpenBalance pipeline!
        trial.parameters['COP_x'] = data[:, 6]
        trial.parameters['COP_y'] = data[:, 7]
        
        return trial
