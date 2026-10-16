# Copyright 2026 O. Hofstätter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Reader für Tetrax Posturographie-System-Einzelexporte.
"""

import numpy as np
from openbalance.io.readers.base import BaseReader
from openbalance.core.trial import Trial

class TetraxReader(BaseReader):
    
    def _convert_data(self, data_lines):
        """Konvertiert String-Listen mit Komma-Dezimaltrennzeichen in Floats."""
        return [float(item.rstrip().replace(',', '.')) for item in data_lines]

    def read(self, filepath: str, sample_rate=32.0) -> Trial:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file_obj:
            data = file_obj.readlines()
            
        measurement_date = data[13].strip()
        dob = data[9].strip()
        
        metadata = {
            "name": data[0].strip(),
            "surname": data[6].strip(),
            "patient_id": data[8].strip(),
            "date": measurement_date,
            "dob": dob,
            "sex": data[10].strip()
        }
        
        # Extraktion der Kraftdaten-Blöcke (Platten A, B, C, D)
        m1 = self._convert_data(data[28:4124])
        m2 = self._convert_data(data[4125:8221])
        m3 = self._convert_data(data[8222:12318])
        m4 = self._convert_data(data[12319:16415])
        
        raw_data = np.column_stack((m1, m2, m3, m4))
        channel_names = ["A", "B", "C", "D"]
        
        return Trial(
            raw_data=raw_data, 
            sample_rate=sample_rate, 
            channel_names=channel_names, 
            metadata=metadata
        )