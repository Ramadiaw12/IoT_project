import psutil
import time
import pandas as pd
import numpy as np

# 1. Charger le dataset
df = pd.read_csv('benign.csv', nrows=10000)

# 2. Afficher les colonnes (optionnel)
print("Colonnes disponibles :", df.columns.tolist())

# 3. Choisir une colonne pour la présence
presence_col = 'HH_L5_magnitude'  # à modifier si besoin

# Calculer un seuil basé sur les données (par exemple, moyenne + écart-type)
seuil = df[presence_col].mean() + df[presence_col].std()
print(f"Seuil pour {presence_col} = {seuil:.4f}")

def get_presence(row):
    # Retourne 1 si la valeur dépasse le seuil, 0 sinon
    return 1 if row[presence_col] > seuil else 0

# 4. Fonction de collecte simulée
def collect_row(row):
    presence = get_presence(row)
    # Générer un RFID à partir de l'index (ou d'une colonne existante)
    rfid = f"RFID_{row.name % 100}"   # simulation simple
    time.sleep(0.01)                  # temps de traitement simulé

# 5. Mesure des ressources
process = psutil.Process()
cpu_percent_list = []
mem_list = []
start_time = time.time()

for index, row in df.iterrows():
    cpu_percent = process.cpu_percent(interval=0.1)
    mem_info = process.memory_info()
    
    collect_row(row)
    
    cpu_percent_list.append(cpu_percent)
    mem_list.append(mem_info.rss / 1024 / 1024)  # MB

    if index % 100 == 0:
        print(f"Ligne {index}: CPU={cpu_percent}%, RAM={mem_info.rss/1024/1024:.2f}MB")

end_time = time.time()
duration = end_time - start_time

# 6. Analyse simple
print(f"\n--- Résultats ---")
print(f"Durée totale: {duration:.2f}s")
print(f"CPU moyen: {sum(cpu_percent_list)/len(cpu_percent_list):.2f}%")
print(f"RAM max: {max(mem_list):.2f}MB")