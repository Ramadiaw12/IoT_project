# 🔐 Monitoring des Accès et des Mouvements avec RFID et Détection de Présence

## 📌 Contexte

Dans les bâtiments intelligents (Smart Buildings), la gestion sécurisée des accès et le suivi des mouvements des occupants sont essentiels pour garantir :

- la **sécurité des infrastructures**
- la **traçabilité des accès**
- l’**optimisation de l’occupation des espaces**

Ce projet propose un système de **monitoring des accès et des mouvements** basé sur des données **RFID simulées** et des **capteurs de présence**, permettant d’analyser les flux d’accès et de détecter des comportements anormaux.

## 👥 Équipe du projet

| Nom | Rôle |
|----|----|
| **Ramatoulaye DIAWANE** | Développement |
| **Audes Mariana MOUSSAVOU** | Analyse des données |
| **Awa Aimée BENZEKRY** | Implémentation |
| **Stecy MOMBO AZZILE** | Visualisation / Dashboard |

Dans le cadre d’un projet académique en **Data Engineering / Sécurité des systèmes**.
---
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Machine Learning](https://img.shields.io/badge/Machine-Learning-green)
![Security](https://img.shields.io/badge/Security-RFID-red)
![Status](https://img.shields.io/badge/Status-Research-orange)

# 🎯 Objectifs du projet

Les objectifs principaux sont :

- Simuler un système de **contrôle d'accès RFID**
- Intégrer des **capteurs de présence**
- Analyser les **mouvements des occupants**
- Détecter les **anomalies d'accès**
- Visualiser les données via un **dashboard de monitoring**

---

# 🏗 Architecture du système

Le système repose sur une architecture en plusieurs couches :

RFID Readers + Presence Sensors
│
▼
Data Collection
│
▼
Data Processing
(Python)
│
▼
Anomaly Detection (Machine Learning)
│
▼
Monitoring Dashboard


---

# 📊 Dataset

Le dataset utilisé simule un environnement de **bâtiment intelligent** avec des événements d’accès RFID et des données de capteurs de présence.

### Structure des données

| Colonne | Description |
|------|------|
| `timestamp` | Date et heure de l'événement |
| `badge_id` | Identifiant du badge RFID |
| `door_id` | Porte ou point d'accès |
| `action` | entrée ou sortie |
| `room` | salle concernée |
| `motion_detected` | détection de mouvement |
| `occupancy_sensor` | présence détectée |
| `anomaly_flag` | événement anormal simulé |

---

# ⚙️ Technologies utilisées

| Technologie | Rôle |
|------|------|
| Python | traitement des données |
| Pandas | manipulation des datasets |
| NumPy | calcul scientifique |
| Scikit-learn | détection d'anomalies |
| Plotly | visualisation interactive |

---

# 🧠 Détection d’anomalies

Le système identifie différents types de comportements suspects :

- accès à une **zone sensible**
- mouvement détecté **sans badge RFID**
- badge utilisé **simultanément à plusieurs portes**
- activité anormale **en dehors des horaires**

Algorithmes utilisés :

- Isolation Forest
- Local Outlier Factor

---

# 📈 Analyses réalisées

Le système permet plusieurs analyses :

### Analyse des accès

- fréquentation des portes
- activité des employés
- flux d'entrée et de sortie

### Analyse des mouvements

- occupation des salles
- déplacements dans le bâtiment
- détection de zones à forte activité

### Analyse de sécurité

- identification d’intrusions
- comportements inhabituels
- alertes de sécurité

---

# 📂 Structure du projet
rfid-monitoring-system
│
├── data
│ └── rfid_presence_dataset.csv
│
├── notebooks
│ └── exploration.ipynb
│
├── src
│ ├── preprocessing.py
│ ├── anomaly_detection.py
│ ├── feature_engineering.py
│ └── visualization.py
│
├── dashboard
│ └── monitoring_dashboard.py
│
├── README.md
└── requirements.txt


---

# 🚀 Installation

Clone du projet :

```bash
git clone https://github.com/Ramadiaw12/IoT_project


## Architecture IoMT — Monitoring des accès et mouvements de datasets
