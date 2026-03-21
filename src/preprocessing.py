"""
Partie 1 – Sensing Layer
Collecte de données depuis le dataset N-BaIoT (benign.csv)
Mesure de la consommation CPU, mémoire et estimation de l'énergie
Auteur : [Votre nom]
Date : [Date]
"""

import psutil
import time
import pandas as pd
import numpy as np

# =============================================================================
# 1. CHARGEMENT DU DATASET
# =============================================================================
# Lecture du fichier CSV contenant les traces du capteur de mouvement (N-BaIoT)
# nrows=10000 permet de limiter la durée de l'expérience et d'éviter une surcharge mémoire.
df = pd.read_csv('data/benign.csv', nrows=10000)
print(f"[INFO] Dataset chargé : {len(df)} lignes")

# =============================================================================
# 2. CHOIX DE LA COLONNE REPRÉSENTANT LA PRÉSENCE ET CALCUL DU SEUIL
# =============================================================================
# Dans N-BaIoT, la colonne 'HH_L5_magnitude' reflète l'intensité du trafic du capteur.
# Une valeur élevée correspond à une activité (présence).
presence_col = 'HH_L5_magnitude'

# Calcul d'un seuil statistique : moyenne + écart-type.
# Toute valeur supérieure à ce seuil sera considérée comme une détection de présence.
seuil = df[presence_col].mean() + df[presence_col].std()
print(f"[INFO] Seuil de présence calculé : {seuil:.4f}")

# =============================================================================
# 3. FONCTIONS DE SIMULATION DU CAPTEUR
# =============================================================================
def get_presence(row):
    """
    Détermine l'état de présence (1 = présence détectée, 0 = absence)
    à partir de la valeur de la colonne de présence.
    """
    return 1 if row[presence_col] > seuil else 0

def collect_row(row):
    """
    Simule la lecture d'un capteur de présence et d'un lecteur RFID.
    - presence : état binaire calculé par get_presence()
    - rfid : identifiant généré artificiellement à partir de l'index de la ligne
    - time.sleep(0.01) : temps de traitement simulé (10 ms)
    """
    presence = get_presence(row)
    rfid = f"RFID_{row.name % 100}"          # Génère un tag RFID (modulo 100)
    time.sleep(0.01)                         # Simule la latence matérielle
    # On pourrait ici stocker les données dans une file, les envoyer via MQTT, etc.
    return presence, rfid

# =============================================================================
# 4. MESURE DES RESSOURCES SYSTÈME
# =============================================================================
# Objet psutil représentant le processus courant (le script Python)
process = psutil.Process()

# Listes pour enregistrer les mesures à chaque itération
cpu_percent_list = []
mem_list = []

# Enregistrement du temps de début
start_time = time.time()

# =============================================================================
# 5. BOUCLE PRINCIPALE DE COLLECTE
# =============================================================================
for index, row in df.iterrows():
    # Mesure de l'utilisation CPU sur une fenêtre de 0.1 seconde
    cpu_percent = process.cpu_percent(interval=0.1)
    
    # Mesure de la mémoire RSS (Resident Set Size) en octets, convertie en Mo
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / (1024 * 1024)
    
    # Simuler la collecte du capteur
    presence, rfid = collect_row(row)
    
    # Enregistrement des mesures
    cpu_percent_list.append(cpu_percent)
    mem_list.append(mem_mb)
    
    # Affichage périodique (toutes les 100 lignes) pour suivre l'avancement
    if index % 100 == 0:
        print(f"Ligne {index}: CPU={cpu_percent}% | RAM={mem_mb:.2f} Mo | Présence={presence} | RFID={rfid}")

# =============================================================================
# 6. ANALYSE DES RÉSULTATS
# =============================================================================
end_time = time.time()
duration = end_time - start_time

cpu_avg = sum(cpu_percent_list) / len(cpu_percent_list)
mem_max = max(mem_list)

print("\n" + "="*50)
print("RÉSULTATS DE LA COLLECTE")
print("="*50)
print(f"Durée totale : {duration:.2f} secondes")
print(f"CPU moyen    : {cpu_avg:.2f} %")
print(f"Mémoire max  : {mem_max:.2f} Mo")

# =============================================================================
# 7. ESTIMATION DE LA CONSOMMATION ÉNERGÉTIQUE
# =============================================================================
# Paramètres matériels (à adapter selon la plateforme utilisée)
TDP = 15.0          # Thermal Design Power du processeur (Watts)
TENSION = 5.0       # Tension d'alimentation (Volts), typique pour RPi ou batterie

# Énergie en joules = (CPU_moyen/100) * TDP * durée (s)
energie_J = (cpu_avg / 100.0) * TDP * duration

# Conversion en mAh : 1 mAh = 3.6 C sous 1V, donc mAh = (J / V) * (1000/3600)
mAh = energie_J / TENSION * (1000.0 / 3600.0)

print(f"\nEstimation de la consommation énergétique :")
print(f"  - Énergie : {energie_J:.2f} J")
print(f"  - Capacité équivalente : {mAh:.2f} mAh (sous {TENSION:.1f} V)")

# =============================================================================
# 8. REMARQUES FINALES
# =============================================================================
print("\n[INFO] Les valeurs de TDP et de tension doivent être ajustées en fonction")
print("       du matériel réel (ex: RPi3 -> TDP=5W, tension=5V).")