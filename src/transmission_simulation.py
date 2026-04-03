import numpy as np

data = np.random.randint(0, 2, 1000)  # 0 = rien, 1 = événement

# 📡 1. Continue
continuous = len(data)

# 📡 2. Périodique (toutes les 10 lignes)
periodic = len(data[::10])

# 📡 3. Event-driven
event_driven = np.sum(data)

print("===== TRANSMISSION =====")
print(f"Continue: {continuous} envois")
print(f"Périodique: {periodic} envois")
print(f"Event-driven: {event_driven} envois")