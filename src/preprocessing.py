import psutil
import time
import pandas as pd

# =========================
# 1. CHARGEMENT DATA
# =========================
df = pd.read_csv('data/benign.csv', nrows=10000)
print(f"[INFO] Dataset chargé : {len(df)} lignes")

presence_col = 'HH_L5_magnitude'
seuil = df[presence_col].mean() + df[presence_col].std()
print(f"[INFO] Seuil de présence calculé : {seuil:.4f}")

# =========================
# 2. FONCTIONS
# =========================
def get_presence(value):
    return 1 if value > seuil else 0

# =========================
# 3. MONITORING
# =========================
process = psutil.Process()

# Initialisation CPU (IMPORTANT)
process.cpu_percent(interval=None)

cpu_list = []
mem_list = []
results = []
presence_count = 0

start_time = time.time()

# =========================
# 4. BOUCLE OPTIMISÉE
# =========================
for index, row in df.iterrows():

    # Mesure CPU sans bloquer
    cpu = process.cpu_percent(interval=None)
    mem = process.memory_info().rss / (1024 * 1024)

    value = row[presence_col]
    presence = get_presence(value)

    if presence == 1:
        presence_count += 1

    rfid = f"RFID_{index % 100}"

    # Sauvegarde
    results.append({
        "cpu": cpu,
        "ram": mem,
        "presence": presence,
        "rfid": rfid
    })

    cpu_list.append(cpu)
    mem_list.append(mem)

    # Affichage
    if index % 50 == 0:
        print(f"Ligne {index}: CPU={cpu:.2f}% | RAM={mem:.2f} Mo | Présence={presence} | RFID={rfid}")

end_time = time.time()

# =========================
# 5. ANALYSE
# =========================
duration = end_time - start_time
cpu_avg = sum(cpu_list) / len(cpu_list)
mem_max = max(mem_list)

print("\n===== RÉSULTATS =====")
print(f"Durée : {duration:.2f}s")
print(f"CPU moyen : {cpu_avg:.2f}%")
print(f"RAM max : {mem_max:.2f} Mo")
print(f"Présences détectées : {presence_count}")

# =========================
# 6. ÉNERGIE
# =========================
TDP = 15.0
TENSION = 5.0

energie = (cpu_avg / 100.0) * TDP * duration
mAh = energie / TENSION * (1000.0 / 3600.0)

print(f"Énergie : {energie:.2f} J")
print(f"mAh : {mAh:.2f}")

# =========================
# 7. EXPORT CSV
# =========================
df_out = pd.DataFrame(results)
df_out.to_csv("output/results.csv", index=False)

print("[INFO] Résultats sauvegardés dans output/results.csv")