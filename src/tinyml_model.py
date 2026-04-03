import numpy as np
from sklearn.linear_model import LogisticRegression
import time
import psutil
import os

# 📊 Simulation dataset (présence + RFID)
np.random.seed(42)

X = np.random.rand(1000, 2)  # [mouvement, RFID]
y = (X[:, 0] + X[:, 1] > 1).astype(int)  # 1 = accès suspect

# 🧠 Modèle TinyML simple
model = LogisticRegression()
model.fit(X, y)

# 📈 Benchmark
process = psutil.Process(os.getpid())

start_time = time.time()

predictions = model.predict(X)

end_time = time.time()

cpu = psutil.cpu_percent()
memory = process.memory_info().rss / (1024 * 1024)

# 🔋 Simulation énergie
energy = cpu * (end_time - start_time) * 0.1

print("===== TINYML RESULT =====")
print(f"Temps: {end_time - start_time:.4f}s")
print(f"CPU: {cpu}%")
print(f"RAM: {memory:.2f} MB")
print(f"Energie estimée: {energy:.4f} J")
print(f"Détections: {sum(predictions)}")