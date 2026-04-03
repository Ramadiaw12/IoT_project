import numpy as np
import time
import psutil
import os
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# 📊 Dataset simulé (présence + RFID)
np.random.seed(42)
X = np.random.rand(1000, 2)
y = (X[:, 0] + X[:, 1] > 1).astype(int)

process = psutil.Process(os.getpid())

def measure_model(model, name):
    start = time.time()
    model.fit(X, y)
    predictions = model.predict(X)
    end = time.time()

    cpu = psutil.cpu_percent()
    ram = process.memory_info().rss / (1024 * 1024)
    accuracy = accuracy_score(y, predictions)

    energy = cpu * (end - start) * 0.1
    mah = energy * 0.05

    print(f"\n=== {name} ===")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Temps: {end - start:.4f}s")
    print(f"CPU: {cpu}%")
    print(f"RAM: {ram:.2f} MB")
    print(f"Energie: {energy:.4f} J")
    print(f"mAh: {mah:.4f}")

# 🧠 Modèle 1 : Threshold
class ThresholdModel:
    def fit(self, X, y):
        pass
    def predict(self, X):
        return (X[:, 0] + X[:, 1] > 1).astype(int)

# 🧠 Modèle 2 : Logistic Regression
model_lr = LogisticRegression()

# 🧠 Modèle 3 : Decision Tree léger
model_dt = DecisionTreeClassifier(max_depth=3)

# 🚀 Exécution
measure_model(ThresholdModel(), "Threshold")
measure_model(model_lr, "Logistic Regression")
measure_model(model_dt, "Decision Tree")