# -*- coding: utf-8 -*-
import csv
import numpy as np

class AmtiCsvReader:
    """
    Ein benutzerdefinierter Reader für AMTI Messdaten im .csv Format.
    Liest Fx, Fy, Fz, Mx, My, Mz, COPx und COPy ein.
    """
    
    def __init__(self):
        pass

    def read(self, filepath, sample_rate=1000):
        """
        Liest eine AMTI CSV-Datei ein und gibt ein Trial-Objekt zurück, 
        das mit der openbalance Bibliothek kompatibel ist.
        """
        # Wir definieren eine einfache, kompatible Trial-Klasse falls der
        # direkte Import aus openbalance.core.trial nicht möglich ist.
        class Trial:
            def __init__(self):
                self.parameters = {}
                self.sample_rate = sample_rate
                self.condition = "Unknown"
        
        trial = Trial()
        
        # Listen für die Extraktion der Daten
        fx, fy, fz = [], [], []
        mx, my, mz = [], [], []
        cop_x, cop_y = [], []
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f, delimiter=';') # Fallback-Delimiter
            
            for line_idx, row in enumerate(reader):
                # Falls die CSV mit Komma getrennt ist, reparieren wir die Row
                if len(row) == 1 and ',' in row[0]:
                    row = row[0].split(',')
                    
                # Überprüfen, ob die Zeile mindestens 8 Spalten hat
                if len(row) >= 8:
                    try:
                        # Versuche, die ersten 8 Spalten in Float zu konvertieren.
                        # Text-Header werden durch den ValueError ignoriert.
                        vals = [float(x.strip()) for x in row[:8]]
                        
                        fx.append(vals[0])
                        fy.append(vals[1])
                        fz.append(vals[2])
                        mx.append(vals[3])
                        my.append(vals[4])
                        mz.append(vals[5])
                        
                        # AMTI speichert COP oft in Metern, openbalance nutzt oft cm oder mm. 
                        # Falls eine Skalierung nötig ist (z.B. * 100), kann das hier gemacht werden.
                        cop_x.append(vals[6])
                        cop_y.append(vals[7])
                        
                    except ValueError:
                        # Überspringe Header-Zeilen (Strings können nicht zu Float konvertiert werden)
                        continue
        
        if not cop_x:
            raise ValueError(f"Konnte keine numerischen Daten in {filepath} finden. Bitte CSV Format prüfen.")

        trial.parameters['F_x'] = np.array(fx)
        trial.parameters['F_y'] = np.array(fy)
        trial.parameters['F_z'] = np.array(fz)
        trial.parameters['M_x'] = np.array(mx)
        trial.parameters['M_y'] = np.array(my)
        trial.parameters['M_z'] = np.array(mz)
        
        # WICHTIG: Die Keys 'COP_x' und 'COP_y' werden in der restlichen 
        # OpenBalance Pipeline zwingend vorausgesetzt!
        trial.parameters['COP_x'] = np.array(cop_x)
        trial.parameters['COP_y'] = np.array(cop_y)
        
        return trial