# OpenBalance ⚖️🔓
### An Open-Source Framework, Progressive Protocol, and Hardware Ecosystem for Posturography

OpenBalance is an open-source, hardware-agnostic platform designed to standardize and democratize computerized dynamic posturography. By decoupling data evaluation from proprietary hardware lock-in, OpenBalance bridges the gap between commercial clinical systems and custom open hardware.

The framework integrates four key pillars:
1. **Decentralized Multi-Cell Hardware:** A 16-sensor topography enabling natural, unconstrained foot placement without optical tracking.
2. **Interoperable Python Library (`openbalance`):** Standardized preprocessing and parameter extraction across commercial (Kistler, Tetrax, Tymo, AMTI) and custom force plates.
3. **Progressive 8-Stage Protocol:** A systematic difficulty-scaling measurement sequence (stable surface, foam pads, unstable base) to mitigate ceiling effects.
4. **Advanced Kinematics & Outlier Metric (OER):** Simultaneous sway area modeling and the Outlier Excursion Ratio to quantify transient balance excursions.

---

## 🚀 Key Features

* **Multi-Platform Interoperability:** Standardizes raw center of pressure (COP) and ground reaction force data from commercial vendors (Kistler, AMTI, Tetrax, Tymo) and custom hardware into a unified `Trial` object via Python Abstract Base Classes.
* **Unconstrained Foot Placement & Ergonomics:** Platform dimensions (355 × 460 mm) accommodate foot lengths up to EU shoe size 55 with a 10° natural toe-out angle, eliminating artificial stance constraints.
* **Cascading Mathematical Framework:** Two-stage vectorized COP fusion combining localized sub-platform coordinates via deterministic geometric offsets into an unbiased global trajectory (<1% mechanical crosstalk).
* **Outlier Excursion Ratio (OER):** Dimensionless metric ($\text{OER} = \text{CHA} / \text{PEA}_{95\%}$) contrasting the Convex Hull Area against the 95% Prediction Ellipse to isolate and quantify transient corrective excursions beyond core sway.
* **Progressive 8-Stage Assessment Protocol:** Standardized testing protocol scaling from baseline static stance (eyes open/closed) to compliant foam pads and dynamic multi-axial perturbation on an unstable base (Kalotte / wobble board).
* **Decoupled Clinical Metrics & Reporting:** Direct quantification of quadrant asymmetry via the Weight Distribution Index (WDI), zero-phase Butterworth filtering (default 13 Hz), and automated multi-lingual PDF/CSV/JSON export.

---

## 📦 Installation & Quick Start

OpenBalance is distributed via PyPI:

```bash
pip install openbalance
```

```python
import openbalance as ob

# Load raw trial data from supported systems (e.g., Kistler, Tetrax, custom hardware)
trial = ob.load_trial("data/M4.txt", format="openbalance")

# Preprocessing: zero-phase 2nd-order Butterworth low-pass filter (default 13 Hz)
filtered_trial = trial.filter(cutoff_hz=13.0)

# Compute standard and advanced kinematics
cop_trajectory = filtered_trial.calculate_cop()
wdi = filtered_trial.calculate_wdi()
oer = filtered_trial.calculate_oer()  # CHA / PEA_95%

# Generate comprehensive comparison report
filtered_trial.export_pdf_report("report_M4.pdf")
```

---

## 📐 Mathematical Principles

### 1. Cascading Global COP Calculation
For distributed sub-platforms ($i = 1 \dots 4$), localized coordinates ($X_{i,\text{local}}, Y_{i,\text{local}}$) are mapped to the global origin using deterministic geometric offsets ($X_{\text{off},i}, Y_{\text{off},i}$):

$$X_{\text{global}} = \frac{\sum_{i=1}^{4} \left( (X_{i,\text{local}} + X_{\text{off},i}) \cdot F_i \right)}{F_{\text{total}}}$$

### 2. Weight Distribution Index (WDI)
Quantifies postural load asymmetry across the four quadrants (left/right, heel/forefoot) relative to the physiological 25% baseline:

$$\text{WDI} = \sqrt{\frac{\sum_{q} (WD_q - 25)^2}{4}}$$

### 3. Outlier Excursion Ratio (OER) & Area (OEA)
Quantifies transient, high-amplitude corrective movements by contrasting boundary and statistical sway models:

$$\text{OER} = \frac{\text{CHA}}{\text{PEA}_{95\%}}, \quad \text{OEA} = \text{CHA} - \text{PEA}_{95\%}$$

* $\text{OER} \approx 1.0$: Stationary, homogeneous sway pattern.
* $\text{OER} \gg 1.0$: Transient corrective excursions extending beyond core sway.

---

## 🏃 Progressive 8-Stage Protocol

To systematically scale postural difficulty and avoid ceiling effects in healthy or athletic cohorts:

| Stage | Surface Condition | Visual Condition | Instability Base |
| :---: | :--- | :--- | :--- |
| **M1** | Stable Platform | Eyes Open (Baseline) | None |
| **M2** | Stable Platform | Eyes Closed | None |
| **M3** | Compliant Foam Pad | Eyes Open | None |
| **M4** | Compliant Foam Pad | Eyes Closed | None |
| **M5** | Stable Platform | Eyes Open | Hemispherical Base (Kalotte) |
| **M6** | Stable Platform | Eyes Closed | Hemispherical Base (Kalotte) |
| **M7** | Compliant Foam Pad | Eyes Open | Hemispherical Base (Kalotte) |
| **M8** | Compliant Foam Pad | Eyes Closed | Hemispherical Base (Kalotte) |

*Note: Trials are standardized to 30 seconds with 30-s static zero-load baseline offset calibration.*

---

## 🛠️ Repository Structure

```text
OpenBalance/
├── openbalance/         # Core Python library (PyPI package)
│   ├── readers/         # Multi-vendor hardware parsers (Kistler, AMTI, Tetrax, Tymo, OpenBalance)
│   ├── kinematics/      # COP, WDI, Sway Area, OER algorithms
│   └── reporting/       # Multi-lingual PDF & data export engines
├── examples/            # High-level execution scripts & 8-stage protocol pipeline
├── hardware_concept/    # 3D-printable CAD models (STL), blueprints, and Bill of Materials (BOM)
├── data/                # Empirical test datasets (including M1–M8 validation streams)
├── publications/        # Peer-reviewed manuscripts & preprints
└── docs/                # Methodological documentation
```

---

## 🤝 Contributing & Open Science

OpenBalance is an open-science initiative welcoming community contributions:
* Adding hardware readers for additional force plate manufacturers.
* Expanding kinematic metrics (e.g., spectral analysis, nonlinear dynamics).
* Hardware enhancements (PCB designs, microcontroller firmware for 200 Hz streaming).

---

## 📄 Publications & Citation

If you use OpenBalance in your research, please cite our open-access publications:

1. **Hofstätter, O., Bochdansky, T., Sabo, A., & Bäckström, M. (2026).** *Methodological Framework for Multi-Cell Posturography Enabling Unconstrained Foot Placement and Open-Source Balance Assessment.* Sensors, 26(19), 6210. DOI: 10.3390/s26196210
2. **Hofstätter, O., Bochdansky, T., Sabo, A., & Bäckström, M. (2026).** *OpenBalance: An Interoperable Computational Framework, Progressive 8-Stage Protocol, and Outlier Metric for Dynamic Posturography — A Technical Proof-of-Concept.*

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
