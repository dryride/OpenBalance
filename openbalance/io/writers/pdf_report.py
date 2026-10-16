# Copyright 2026 O. Hofstaetter (Mid Sweden University / FH Technikum Wien)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

from fpdf import FPDF
import datetime
from openbalance.io.writers.languages import TRANSLATIONS

class BalancePDF(FPDF):
    def __init__(self, lang="en"):
        super().__init__()
        self.lang = lang
        self.t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    def header(self):
        """Draws the report header with the translated title."""
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, self.t["report_title"], 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, self.t["header_confidential"], 0, 1, 'C')
        self.ln(10)

    def footer(self):
        """Draws the footer with page number."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'{self.t["footer_page"]} {self.page_no()}', 0, 0, 'C')

def generate_balance_report(session, output_filename, lang="en"):
    # Sprachpaket laden
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    
    pdf = BalancePDF()
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # 1. Patienten-Metadaten mit übersetzten Labels
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, t["patient_data"], 0, 1)
    
    pdf.set_font('Arial', '', 10)
    meta = session.patient_metadata
    pdf.cell(0, 6, f"{t['name']}: {meta.get('Name', 'N/A')}", 0, 1)
    pdf.cell(0, 6, f"{t['age']}: {meta.get('Age', 'N/A')}", 0, 1)
    pdf.cell(0, 6, f"{t['date']}: {datetime.date.today().strftime('%d.%m.%Y')}", 0, 1)
    pdf.ln(10)
    
    # 2. Bilder mit übersetzten Werten
    y_start = pdf.get_y()
    x_positions = [15, 110]
    
    for idx, trial in enumerate(session.trials):
        idx_on_page = idx % 4 
        col = idx_on_page % 2
        row = idx_on_page // 2
        
        if idx > 0 and idx_on_page == 0:
            pdf.add_page()
            y_start = 30
            
        x = x_positions[col]
        y = y_start + (row * 95)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.text(x, y, f"{t['measurement']} {trial.condition}")
        
        if 'plot_path' in trial.parameters:
            pdf.image(trial.parameters['plot_path'], x=x, y=y+1, w=75)
            
        # Parameter aus dem Trial abholen
        path_len = trial.parameters.get('Path_Length', 0.0)
        wdi = trial.parameters.get('WDI', 0.0)
        a_hull = trial.parameters.get('Area_Hull', 0.0)
        a_ell = trial.parameters.get('Area_Ellipse', 0.0)
        a_circ = trial.parameters.get('Area_Circle', 0.0)
        a_diff = trial.parameters.get('Area_Diff', 0.0)
        a_ratio = trial.parameters.get('Area_Ratio', 0.0)
        
        # --- ZWEISPALTIGES PARAMETER-LAYOUT ---
        pdf.set_font('Arial', '', 7) # Schriftgröße deutlich verkleinert
        
        text_y = y + 79      # Start-Höhe unter dem Bild
        line_h = 3.5         # Zeilenabstand (kompakt)
        col2_offset = 38     # X-Abstand für die zweite Spalte (halbe Bildbreite)
        
        # SPALTE 1: Basis-Werte und deine neuen Parameter
        pdf.text(x, text_y, f"{t['pl_short']}: {path_len:.2f} {t['unit_cm']}")
        pdf.text(x, text_y + line_h, f"{t['wdi_short']}: {wdi:.2f} %")
        
        pdf.set_font('Arial', 'B', 7) # Deine neuen Parameter fett hervorheben
        pdf.text(x, text_y + 2*line_h, f"{t['oea_short']}: {a_diff:.2f} {t['unit_cm2']}")
        pdf.text(x, text_y + 3*line_h, f"{t['oer_short']}: {a_ratio:.2f}")
        
        # SPALTE 2: Der Flächen-Vergleich (Kursiv für Area-Modelle)
        pdf.set_font('Arial', 'I', 7) 
        col2_x = x + col2_offset
        
        pdf.text(col2_x, text_y, f"{t['cha_short']}: {a_hull:.2f} {t['unit_cm2']}")
        pdf.text(col2_x, text_y + line_h, f"{t['pea_short']}: {a_ell:.2f} {t['unit_cm2']}")
        pdf.text(col2_x, text_y + 2*line_h, f"{t['cca_short']}: {a_circ:.2f} {t['unit_cm2']}")
        
    pdf.output(output_filename)