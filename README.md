# 🏥 Monitoring des Accès et Mouvements – Système IoT Hospitalier

> **Détection de présence, simulation RFID, stratégies de transmission intelligentes et dashboard temps réel**

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?logo=scikit-learn&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Compatible-A22846?logo=raspberry-pi&logoColor=white)
![License](https://img.shields.io/badge/Licence-MIT-green)
![Status](https://img.shields.io/badge/Statut-Production-brightgreen)

---

## 📋 Table des matières

- [🏥 Monitoring des Accès et Mouvements – Système IoT Hospitalier](#-monitoring-des-accès-et-mouvements--système-iot-hospitalier)
  - [📋 Table des matières](#-table-des-matières)
  - [🎯 Contexte et Objectifs](#-contexte-et-objectifs)
  - [🏗 Architecture du Projet](#-architecture-du-projet)
    - [📁 Structure des dossiers](#-structure-des-dossiers)
  - [📊 Dataset et Préparation des Données](#-dataset-et-préparation-des-données)
    - [Étapes de traitement](#étapes-de-traitement)
  - [🤖 Modèles de Détection d'Anomalies](#-modèles-de-détection-danomalies)
    - [Modèle 1 – Seuil Simple](#modèle-1--seuil-simple)
    - [Modèle 2 – Régression Logistique](#modèle-2--régression-logistique)
    - [Modèle 3 – Arbre de Décision](#modèle-3--arbre-de-décision)
    - [📈 Tableau comparatif des performances](#-tableau-comparatif-des-performances)
  - [📡 Stratégies de Transmission](#-stratégies-de-transmission)
  - [📺 Dashboard de Monitoring (Streamlit)](#-dashboard-de-monitoring-streamlit)
    - [Fonctionnalités principales](#fonctionnalités-principales)
    - [Aperçu](#aperçu)
    - [Lancer le dashboard](#lancer-le-dashboard)
  - [📌 Résultats et Interprétations](#-résultats-et-interprétations)
  - [⚙️ Installation et Exécution](#️-installation-et-exécution)
    - [Prérequis](#prérequis)
    - [Étapes](#étapes)
  - [🎬 Démonstration](#-démonstration)
  - [🚀 Améliorations Possibles](#-améliorations-possibles)
  - [👥 Équipe](#-équipe)

---

## 🎯 Contexte et Objectifs

Les hôpitaux font face à des défis croissants en matière de **surveillance des accès aux zones sensibles**, notamment les pharmacies, où des comportements anormaux (allers-retours excessifs, accès non autorisés) peuvent indiquer des risques de détournement de médicaments ou d'incidents de sécurité.

Ce projet propose une solution IoT embarquée sur **Raspberry Pi** pour simuler des événements RFID à partir de données de capteurs inertiels (accéléromètre, gyroscope), détecter automatiquement les comportements anormaux via des modèles légers, et transmettre les alertes de manière optimisée. L'ensemble est supervisé via un **dashboard Streamlit interactif** offrant une visibilité temps réel aux équipes de sécurité hospitalière.

---

## 🏗 Architecture du Projet

```
┌─────────────────────────────────────────────────────────────────┐
│                     COUCHE ACQUISITION                          │
│         Dataset Kaggle (accéléro, gyroscope, location_id)       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   COUCHE DATA PROCESSING                        │
│   Nettoyage → Rééchantillonnage 10Hz → Détection mouvement      │
│               → Simulation événements RFID                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│              COUCHE MODÈLES (embarqués sur RPi)                 │
│   ┌─────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│   │ Seuil simple│  │Régr. Logistique  │  │Arbre de Décision │  │
│   │ (règle logiq│  │(features: trajets│  │(profondeur 3,    │  │
│   │   ue)       │  │ durée moy.)      │  │ interprétable)   │  │
│   └─────────────┘  └──────────────────┘  └──────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│               COUCHE TRANSMISSION                               │
│   S1: Immédiat │ S2: Agrégation (N=5) │ S3: Anomalie seulement  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│              COUCHE APPLICATION (Dashboard)                     │
│                Streamlit – Monitoring temps réel                │
└─────────────────────────────────────────────────────────────────┘
```

### 📁 Structure des dossiers

```
hospital-iot-monitoring/
├── data/
│   ├── raw/                        # Dataset brut Kaggle
│   └── processed/
│       └── rfid_events_simules.csv # Événements RFID générés
├── notebooks/
│   └── 01_preprocessing_rfid.ipynb # Pipeline complet de traitement
├── models/
│   ├── threshold_model.py          # Modèle 1 : Seuil simple
│   ├── logistic_model.py           # Modèle 2 : Régression logistique
│   └── decision_tree_model.py      # Modèle 3 : Arbre de décision
├── transmission/
│   ├── strategy_s1_immediate.py    # Envoi immédiat
│   ├── strategy_s2_batch.py        # Agrégation par paquets
│   └── strategy_s3_anomaly.py      # Envoi sur anomalie
├── dashboard/
│   └── dashboard.py                # Application Streamlit
├── assets/
│   └── screenshots/                # Captures d'écran du dashboard
├── requirements.txt
└── README.md
```

---

## 📊 Dataset et Préparation des Données

**Source :** Dataset Kaggle — données IMU de capteurs portables (colonnes : `timestamp`, `acc_x`, `acc_y`, `acc_z`, `gyro_x`, `gyro_y`, `gyro_z`, `location_id`, `session_id`).

### Étapes de traitement

**1. Nettoyage**
- Suppression des doublons et valeurs aberrantes
- Rééchantillonnage à **10 Hz** (interpolation linéaire)
- Normalisation des colonnes numériques

**2. Détection de mouvement**

```python
# Calcul de la norme d'accélération
df['acc_norm'] = np.sqrt(df['acc_x']**2 + df['acc_y']**2 + df['acc_z']**2)

# Variance glissante sur fenêtre de 50 échantillons
df['acc_variance'] = df['acc_norm'].rolling(window=50).var()

# Seuillage : mouvement si variance > 0.05
df['is_moving'] = df['acc_variance'] > 0.05
```

**3. Simulation RFID**

Un événement RFID (entrée/sortie) est généré à chaque **changement de `location_id`**, en associant l'horodatage, la zone, et le type d'événement. Le fichier `rfid_events_simules.csv` est produit à l'issue du notebook.

---

## 🤖 Modèles de Détection d'Anomalies

Trois modèles sont évalués pour leur déploiement sur Raspberry Pi (contraintes mémoire et énergie strictes).

### Modèle 1 – Seuil Simple

Règle logique : alerte si le nombre d'allers-retours vers une zone dépasse un seuil `N` sur une fenêtre temporelle `T` (ex : > 5 allers-retours en 30 minutes vers la pharmacie).

### Modèle 2 – Régression Logistique

Features : nombre de trajets, durée moyenne par trajet, heure de la journée. Entraîné sur les sessions étiquetées, exporté en format `joblib` (~15 Ko).

### Modèle 3 – Arbre de Décision

Profondeur maximale = 3, entièrement interprétable. Critère de split : Gini. Facilement exportable en règles lisibles par les équipes de sécurité.

### 📈 Tableau comparatif des performances

| Modèle               | Accuracy | Précision | Rappel | F1-Score | RAM (Ko) | Inférence (ms) | Conso. (mAh/1000 inf.) |
|----------------------|----------|-----------|--------|----------|----------|----------------|------------------------|
| Seuil Simple         | 0.81     | 0.78      | 0.85   | 0.81     | ~1       | < 0.01         | ~0.001                 |
| Régression Logistique| 0.88     | 0.86      | 0.89   | 0.87     | ~15      | ~0.05          | ~0.010                 |
| **Arbre de Décision**| **0.93** | **0.91**  |**0.93**| **0.92** | ~45      | ~0.08          | ~0.015                 |

> ✅ **Recommandation :** L'arbre de décision offre le meilleur compromis précision/ressources. Il reste très léger (< 50 Ko de RAM, inférence < 0.1 ms) tout en atteignant un F1-score de **0.92**.

---

## 📡 Stratégies de Transmission

Trois stratégies ont été implémentées et comparées pour optimiser la consommation énergétique du dispositif embarqué.

| Stratégie                     | Description                              | Conso. (mAh/h) | Latence moy. (s) | Bande passante (kbps) |
|-------------------------------|------------------------------------------|----------------|------------------|-----------------------|
| **S1** – Envoi immédiat       | Chaque événement envoyé dès détection    | 0.0417         | ~0.1             | 12.5                  |
| **S2** – Agrégation (N=5)     | Envoi par lots de 5 événements           | 0.0112         | ~2.5             | 3.2                   |
| **S3** – Anomalie seulement   | Envoi uniquement si anomalie détectée    | 0.0089         | ~0.1 (si alerte) | 0.9                   |
| **Hybride (recommandé)**       | S3 pour alertes + S2 pour données norm. | **0.0095**     | ~0.1 (alertes)   | 2.1                   |

> ⚡ **La stratégie hybride permet une économie d'énergie de ~80%** par rapport à l'envoi immédiat (S1), tout en garantissant une latence quasi nulle pour les alertes critiques.

---

## 📺 Dashboard de Monitoring (Streamlit)

### Fonctionnalités principales

- 🔍 **Filtres dynamiques** : session, zone/salle, seuil d'alerte personnalisable
- 📅 **Timeline interactive** : visualisation chronologique des événements RFID
- 📊 **Histogramme des durées** de présence par zone
- 🥧 **Camembert** de répartition des accès par zone
- 📈 **Courbe cumulative** des allers-retours vers la pharmacie
- 🚨 **Alertes visuelles** en temps réel (badge rouge + notification)
- 🔋 **Rapport de consommation** : comparatif des 3 stratégies de transmission

### Aperçu

```
┌─────────────────────────────────────────────────────┐
│  🏥 MONITORING HOSPITALIER          [⚠ 2 ALERTES]  │
├──────────────┬──────────────────────────────────────┤
│  FILTRES     │  TIMELINE DES ÉVÉNEMENTS             │
│  Session: ▼  │  ──●──────●──────●──●──────────────  │
│  Zone: ▼     │  08:00  09:00  10:00  11:00          │
│  Seuil: [5]  ├──────────────────────────────────────┤
│              │  DURÉES PAR ZONE      ACCÈS/ZONE     │
│              │  █████ Pharmacie      🟠 45%          │
│              │  ███ Bloc A           🔵 30%          │
│              │  ██ Urgences          🟢 25%          │
└──────────────┴──────────────────────────────────────┘
```

### Lancer le dashboard

```bash
streamlit run dashboard/dashboard.py
```

Le dashboard est accessible sur `http://localhost:8501`.

---

## 📌 Résultats et Interprétations

| Critère                  | Résultat                                               |
|--------------------------|--------------------------------------------------------|
| 🏆 Meilleur modèle       | Arbre de décision — F1-score **0.92**, RAM < 50 Ko     |
| ⚡ Meilleure transmission | Hybride — **−80% de consommation** vs envoi immédiat   |
| 🚨 Fausses alertes        | Réduites de ~40% vs règle de seuil simple              |
| 🏥 Impact métier          | Surveillance efficace de la pharmacie en temps réel    |

---

## ⚙️ Installation et Exécution

### Prérequis

- Python **3.9+**
- `pip` et `virtualenv`
- Jupyter Notebook (pour le preprocessing)

### Étapes

**1. Cloner le dépôt**

```bash
git clone https://github.com/votre-org/hospital-iot-monitoring.git
cd hospital-iot-monitoring
```

**2. Créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Installer les dépendances**

```bash
pip install -r requirements.txt
```

> **Dépendances principales :** `pandas`, `numpy`, `scikit-learn`, `streamlit`, `plotly`, `joblib`, `scipy`, `jupyter`

**4. Générer les événements RFID simulés**

```bash
jupyter notebook notebooks/01_preprocessing_rfid.ipynb
# Exécuter toutes les cellules → génère data/processed/rfid_events_simules.csv
```

**5. Lancer le dashboard Streamlit**

```bash
streamlit run dashboard/dashboard.py
```

---

## 🎬 Démonstration

> 📽️ *Vidéo de démonstration disponible :* [`assets/demo_dashboard.gif`](assets/demo_dashboard.gif)

Pour une démonstration rapide sans exécution complète du notebook, un fichier de données exemple est inclus dans `data/processed/sample_rfid_events.csv`.

---

## 🚀 Améliorations Possibles

- **Temps réel via MQTT** : intégration d'un broker Mosquitto pour les flux live capteurs
- **Modèles Edge TPU** : utilisation de TensorFlow Lite + Google Coral pour des modèles plus profonds sans surcoût énergétique
- **Cartographie des zones** : ajout d'une carte géographique interactive de l'hôpital (Folium/Plotly Maps)
- **Apprentissage fédéré** : entraînement distribué sur plusieurs dispositifs Raspberry Pi sans centraliser les données patients
- **Intégration DICOM/HL7** : interconnexion avec les systèmes d'information hospitaliers existants

---

## 👥 Équipe

| Nom                  | Rôle                                        |
|----------------------|---------------------------------------------|
| **DIAWANE R**      | Ingénieur Data -   |
| **MOUSSAVOU Audes M**   | Data Engineer –  |
| **BENZEKRY Aimée A**   | Développeur –            |
| **?OMBO AZZILE S**   | Développeur –           |


---

<div align="center">

*Projet réalisé dans le cadre d'un livrable hospitalier – Tous droits réservés © 2024*

[![MIT License](https://img.shields.io/badge/Licence-MIT-green)](LICENSE)

</div>