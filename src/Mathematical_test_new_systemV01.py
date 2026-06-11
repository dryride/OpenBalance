"""
OpenBalance - Core Mathematical Framework for Multi-Cell Posturography
Developed by O. Hofstätter (Mid Sweden University / FH Technikum Wien)

This module implements the two-stage, cascading Center of Pressure (COP) 
calculation and the Weight Distribution Index (WDI) based on force-weighted 
averages and coordinate transformations.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from statistics import mean
"""
@author: hofstaet

Sensor arrangement:
    6   5|14   13
         |
    7   4|15   12
    8   3|16   11
    1   2|9    10
"""

# Read the test File
def read_single(filename):
    """
    Liest Messdaten ein, bereinigt sie und gibt 16 NumPy-Arrays zurück.
    
    :param filename: Pfad zur Datei
    :return: F1 ... F16 als NumPy-Arrays
    """
    
    valid_rows = []
    
    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            
            if not line:
                continue
            
            columns = line.split(",")
            
            if len(columns) == 16:
                try:
                    values = [float(v) for v in columns]
                    valid_rows.append(values)
                except ValueError:
                    print(f"Zeile {line_number} verworfen (ungültige Zahlen)")
    
    # In NumPy-Array umwandeln
    data = np.array(valid_rows)
    
    # Spalten aufteilen
    return tuple(data[:, i] for i in range(16))    

def COFT(F1,F2,F3,F4,a,b,c,d):
    """ COP
    x=(F1*x1+F2*x2+F3*x3+F4*x4)/(F1+F2+F3+F4)
    y=(F1*y1+F2*y2+F3*y3+F4*y4)/(F1+F2+F3+F4)
    """ 
    x1=-b/2
    x2=-a/2
    x3=a/2
    x4=b/2
    y1=-c/2
    y2=c/2
    y3=c/2
    y4=-c/2
    x = (F1*x1+F2*x2+F3*x3+F4*x4)/(F1+F2+F3+F4)
    y = (F1*y1+F2*y2+F3*y3+F4*y4)/(F1+F2+F3+F4)
    return x,y,a,b,c,d

def COF(x,y):
    x_mean = mean(x)
    y_mean = mean(y)
    return x_mean, y_mean

def dbs_COFT_VersionC(F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13,F14,F15,F16):
    # Formula to get Coordinates for every tile.
    """
    Sensor arrangement:
    6   5|14   13
         |
    7   4|15   12
    8   3|16   11
    1   2|9    10
    """
    x_m=-10
    x_p=10
    yh_m=-5.5
    yh_p=5.5
    yf_m=-9.25
    yf_p=9.25
    x_lh = (F1*x_m+F2*x_p+F3*x_p+F8*x_m)/(F1+F2+F3+F8)
    y_lh = (F1*yh_m+F2*yh_m+F3*yh_p+F4*yh_p)/(F1+F2+F3+F8)
    x_lf = (F7*x_m+F4*x_p+F5*x_p+F6*x_m)/(F4+F5+F6+F7)
    y_lf = (F7*yf_m+F4*yf_m+F5*yf_p+F6*yf_p)/(F4+F5+F6+F7)
    x_rh = (F9*x_m+F10*x_p+F11*x_p+F16*x_m)/(F9+F10+F11+F16)
    y_rh = (F9*yh_m+F10*yh_m+F11*yh_p+F16*yh_p)/(F9+F10+F11+F16)
    x_rf = (F15*x_m+F12*x_p+F13*x_p+F14*x_m)/(F12+F13+F14+F15)
    y_rf = (F15*yf_m+F12*yf_m+F13*yf_p+F14*yf_p)/(F12+F13+F14+F15)
    Fa = np.asarray([sum(i) for i in zip(F1,F2,F3,F8)])
    Fb = np.asarray([sum(i) for i in zip(F4,F5,F6,F7)])
    Fc = np.asarray([sum(i) for i in zip(F9,F10,F11,F16)])
    Fd = np.asarray([sum(i) for i in zip(F12,F13,F14,F15)])
    #x = (Fa*x_lh-115+Fb*x_lf-115+Fc*x_rh+115+Fd*x_rf+115)/(Fa+Fb+Fc+Fd)
    #y = (Fa*y_lh-70+Fb*y_lf+107+Fc*y_rh-70+Fd*y_rf+107)/(Fa+Fb+Fc+Fd)
    # Korrekte punktweise Berechnung mit NumPy-Arrays
    x = (Fa * (x_lh - 11.5) + Fb * (x_lf - 11.5) + Fc * (x_rh + 11.5) + Fd * (x_rf + 11.5)) / (Fa + Fb + Fc + Fd)
    y = (Fa * (y_lh - 7.0) + Fb * (y_lf + 10.7) + Fc * (y_rh - 7.0) + Fd * (y_rf + 10.7)) / (Fa + Fb + Fc + Fd)
    return x,y,x_lh,y_lh,x_lf,y_lf,x_rh,y_rh,x_rf,y_rf

def dbs_COFT_VersionF(F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13,F14,F15,F16):
    # COP calculation without this Information
    b_dbs = 23.0
    c_dbs = 17.7
    a_dbs = b_dbs
    d_dbs = (a_dbs - b_dbs)/2
    
    Fa = np.asarray([sum(i) for i in zip(F1,F2,F3,F8)])
    Fb = np.asarray([sum(i) for i in zip(F4,F5,F6,F7)])
    Fc = np.asarray([sum(i) for i in zip(F9,F10,F11,F16)])
    Fd = np.asarray([sum(i) for i in zip(F12,F13,F14,F15)])

    x,y,a,b,c,d = COFT(Fa,Fb,Fd,Fc,a_dbs,b_dbs,c_dbs,d_dbs)
    return x,y,a,b,c,d,Fa,Fb,Fd,Fc

import matplotlib.pyplot as plt

def plot_forces(F1, F2, F3, F4, F5, F6, F7, F8,F9, F10, F11, F12, F13, F14, F15, F16):
    forces = [F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16]
    plt.figure()
    for i, F in enumerate(forces):
        plt.plot(F, label=f"F{i+1}", linewidth=1)
    plt.xlabel("Messpunkt")
    plt.ylabel("Kraft")
    plt.title("Kräfteverlauf F1–F16")
    plt.legend()
    plt.grid()
    plt.show()


def plot_forces_interactive(F1, F2, F3, F4, F5, F6, F7, F8,
                           F9, F10, F11, F12, F13, F14, F15, F16):

    forces = [F1, F2, F3, F4, F5, F6, F7, F8,
              F9, F10, F11, F12, F13, F14, F15, F16]

    labels = [f"F{i+1}" for i in range(16)]

    fig, ax = plt.subplots()
    plt.subplots_adjust(left=0.25)

    lines = []

    # Linien zeichnen + Farben automatisch speichern
    for i, F in enumerate(forces):
        line, = ax.plot(F, label=labels[i], linewidth=1)
        lines.append(line)

    ax.set_xlabel("Messpunkt")
    ax.set_ylabel("Kraft")
    ax.set_title("Interaktiver Kräfteverlauf")
    ax.grid()

    ax.legend(loc="upper right", fontsize=8, ncol=2)

    # Checkboxen
    rax = plt.axes([0.02, 0.2, 0.15, 0.6])
    visibility = [True] * 16

    check = CheckButtons(rax, labels, visibility)

    def toggle(label):
        index = labels.index(label)
        lines[index].set_visible(not lines[index].get_visible())
        plt.draw()

    check.on_clicked(toggle)

    plt.show()


samplefreq = 100

F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13,F14,F15,F16 = read_single("M4.txt")
plot_forces_interactive(F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16)
# Konvert Sensor Stream from testsetup to the load cell positions
nF1=F10
nF2=F9
nF3=F11
nF4=F13
nF5=F15
nF6=F16
nF7=F14
nF8=F12
nF9=F2
nF10=F1
nF11=F3
nF12=F5
nF13=F7
nF14=F8
nF15=F6
nF16=F4


plot_forces(nF1, nF2, nF3, nF4, nF5, nF6, nF7, nF8, nF9, nF10, nF11, nF12, nF13, nF14, nF15, nF16)
x,y,a,b,c,d,Fa,Fb,Fd,Fc = dbs_COFT_VersionF(nF1, nF2, nF3, nF4, nF5, nF6, nF7, nF8, nF9, nF10, nF11, nF12, nF13, nF14, nF15, nF16)
plt.plot(x,y,linewidth=0.5)
x_mean = mean(x)
y_mean = mean(y)
plt.plot(x_mean,y_mean,'gx',mew=3,ms=10)


# 1. Gesamtkraft pro Zeitschritt berechnen
F_total = Fa + Fb + Fc + Fd

# 2. Prozentuale Verteilung berechnen (punktweise über das Array)
WD_hl = (Fa / F_total) * 100
WD_hr = (Fc / F_total) * 100
WD_fl = (Fb / F_total) * 100
WD_fr = (Fd / F_total) * 100

# 3. Den Weight Distribution Index (WDI) berechnen
wdi_per_timestep = np.sqrt(
    ((WD_hl - 25)**2 + (WD_hr - 25)**2 + (WD_fl - 25)**2 + (WD_fr - 25)**2) / 4
)

# 4. Klinischer Endwert: Der Mittelwert über die gesamte Messdauer
final_wdi = np.mean(wdi_per_timestep)
print(f"Weight Distribution Index (WDI): {final_wdi:.2f}")

plt.text(-17, 15, ("WD: " + str(round(mean(WD_fl),2)) + "%"), fontsize=12, color="black", weight="bold")
plt.text(-17, -10, ("WD: " + str(round(mean(WD_hl),2)) + "%"), fontsize=12, color="black", weight="bold")
plt.text(6, 15, ("WD: " + str(round(mean(WD_fr),2)) + "%"), fontsize=12, color="black", weight="bold")
plt.text(6, -10, ("WD: " + str(round(mean(WD_hr),2)) + "%"), fontsize=12, color="black", weight="bold")

plt.text(4.5, 18, ("FOREFOOT"), fontsize=16, color="black", weight="bold")
plt.text(-18.5, 18, ("FOREFOOT"), fontsize=16, color="black", weight="bold")
plt.text(-14.5, -3, ("HEEL"), fontsize=16, color="black", weight="bold")
plt.text(9, -3, ("HEEL"), fontsize=16, color="black", weight="bold")


x,y,x_lh,y_lh,x_lf,y_lf,x_rh,y_rh,x_rf,y_rf = dbs_COFT_VersionC(nF1, nF2, nF3, nF4, nF5, nF6, nF7, nF8, nF9, nF10, nF11, nF12, nF13, nF14, nF15, nF16)
plt.plot(x_lh-11.5,y_lh-7,linewidth=0.5)
plt.plot(x_lf-11.5,y_lf+10.7,linewidth=0.5)
plt.plot(x_rh+11.5,y_rh-7,linewidth=0.5)
plt.plot(x_rf+11.5,y_rf+10.7,linewidth=0.5)
plt.plot([-23,-0.1,-0.1,-23,-23],[-14,-14,-0.1,-0.1,-14],'k') #Left Heel
plt.plot([23,0.1,0.1,23,23],[-14,-14,-0.1,-0.1,-14],'k') #Right Heel
plt.plot([-23,-0.1,-0.1,-23,-23],[21.5,21.5,0.1,0.1,21.5],'k') #Left Forefoot
plt.plot([23,0.1,0.1,23,23],[21.5,21.5,0.1,0.1,21.5],'k') #Right Forefoot
plt.plot([-21.5,-1.5,-1.5,-21.5],[-12.5,-12.5,-1.5,-1.5],'ro') #Left Heel - Marker
plt.plot([21.5,1.5,1.5,21.5],[-12.5,-12.5,-1.5,-1.5],'ro') #Right Heel - Marker
plt.plot([-21.5,-1.5,-1.5,-21.5],[20,20,1.5,1.5],'ro') #Left Forefoot - Marker
plt.plot([21.5,1.5,1.5,21.5],[20,20,1.5,1.5],'ro') #Right Forefoot - Marker
plt.plot(x,y,'y',linewidth=1)

x_mean = mean(x)
y_mean = mean(y)
plt.plot(x_mean,y_mean,'rx',mew=3,ms=10)

plt.show()




