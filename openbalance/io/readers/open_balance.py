# Copyright 2026 O. Hofstätter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Reader für das 16-Zellen OpenBalance System.
"""

import numpy as np
from openbalance.io.readers.base import BaseReader
from openbalance.core.trial import Trial

class OpenBalanceReader(BaseReader):
    
    def read(self, filepath: str, sample_rate=100.0) -> Trial:
        valid_rows = []
        
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line: 
                    continue
                
                columns = line.split(",")
                if len(columns) == 16:
                    try:
                        valid_rows.append([float(v) for v in columns])
                    except ValueError:
                        pass
                        
        data = np.array(valid_rows)
        if data.size == 0:
            raise ValueError(f"Keine gültigen 16-spaltigen Daten in {filepath} gefunden.")
        
        # Sensor-Matrix-Mapping (Konvertierung des Sensor-Streams aus deinem Originalskript)
        mapped_data = np.column_stack((
            data[:, 9],  data[:, 8],  data[:, 10], data[:, 12],
            data[:, 14], data[:, 15], data[:, 13], data[:, 11],
            data[:, 1],  data[:, 0],  data[:, 2],  data[:, 4],
            data[:, 6],  data[:, 7],  data[:, 5],  data[:, 3]
        ))
        
        channel_names = [f"F{i}" for i in range(1, 17)]
        
        return Trial(
            raw_data=mapped_data, 
            sample_rate=sample_rate, 
            channel_names=channel_names
        )