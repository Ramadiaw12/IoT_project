import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1. CHARGER LES DONNÉES
# =========================
df = pd.read_csv("output/results.csv")

print("[INFO] Données chargées pour le dashboard")

# =========================
# 2. CRÉER LES GRAPHIQUES
# =========================

# Graph CPU
plt.figure()
plt.plot(df["cpu"])
plt.title("Utilisation CPU (%)")
plt.xlabel("Itérations")
plt.ylabel("CPU %")
plt.grid()
plt.savefig("output/cpu.png")

# Graph RAM
plt.figure()
plt.plot(df["ram"])
plt.title("Utilisation RAM (Mo)")
plt.xlabel("Itérations")
plt.ylabel("RAM (Mo)")
plt.grid()
plt.savefig("output/ram.png")

# Graph Présence
plt.figure()
plt.plot(df["presence"])
plt.title("Détection de présence (0/1)")
plt.xlabel("Itérations")
plt.ylabel("Présence")
plt.grid()
plt.savefig("output/presence.png")

# =========================
# 3. AFFICHAGE GLOBAL
# =========================
plt.show()