# Copyright 2026 O. Hofstätter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Reader für Tymo Posturographie-Daten im JSON-Format.
"""

import json
import numpy as np
from openbalance.io.readers.base import BaseReader
from openbalance.core.trial import Trial

class TymoReader(BaseReader):
    
    def read(self, filepath: str, sample_rate=100.0) -> Trial:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Die ersten drei Zeichen löschen, um ungültige BOM/Header-Zeichen zu entfernen
            content = file.read()[3:]
            js = json.loads(content)
            
        f1, f2, f3, f4 = [], [], [], []
        for line in js['rawInputMeasurement1']:
            f1.append(line['z'])
            f2.append(line['x'])
            f3.append(line['y'])
            f4.append(line['w'])
            
        raw_data = np.column_stack((f1, f2, f3, f4))
        
        metadata = {
            "dob": js.get('birthdate'),
            "sex": js.get('sex'),
            "date": js.get('date')
        }
        
        # Tymo Layout: left forefoot, right forefoot, left heel, right heel
        channel_names = ["LF", "RF", "LH", "RH"]
        
        return Trial(
            raw_data=raw_data, 
            sample_rate=sample_rate, 
            channel_names=channel_names, 
            metadata=metadata
        )