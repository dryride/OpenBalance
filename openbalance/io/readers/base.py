# Copyright 2026 O. Hofstätter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""
Abstrakte Basisklasse für alle Messsystem-Reader.
"""

from abc import ABC, abstractmethod
from openbalance.core.trial import Trial

class BaseReader(ABC):
    
    @abstractmethod
    def read(self, filepath: str, sample_rate: float) -> Trial:
        """
        Liest eine Datei ein und gibt ein standardisiertes Trial-Objekt zurück.
        
        :param filepath: Absoluter oder relativer Pfad zur Messdatei.
        :param sample_rate: Die Abtastfrequenz des Systems in Hz.
        :return: Ein instanziiertes Trial-Objekt.
        """
        pass