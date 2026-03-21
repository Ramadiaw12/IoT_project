# 📡 IoT Access Monitoring System

> Simulation d'un système de monitoring d'accès RFID avec **3 stratégies de transmission réseau** — comparez latence, débit et volume selon le contexte d'usage.

<br>

## Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture](#-architecture)
- [Les 3 stratégies](#-les-3-stratégies)
- [Démarrage rapide](#-démarrage-rapide)
- [API Serveur](#-api-serveur)
- [Format des logs CSV](#-format-des-logs-csv)
- [Analyse des résultats](#-analyse-des-résultats)
- [Personnalisation](#️-personnalisation)
- [Remarques](#-remarques)

---

## 🔍 Vue d'ensemble

Ce projet simule un système de monitoring d'accès IoT qui détecte la présence via RFID et transmet les données à un serveur central selon **trois protocoles distincts**.

```
Capteur RFID ──► Client Python ──► HTTP POST ──► Flask Server ──► SQLite DB
                     │                                  │
                     └──────── netlog_sX.csv ◄──────────┘
                               (métriques réseau)
```

**Composants principaux :**

| Composant | Rôle |
|---|---|
| `server.py` | Serveur Flask · reçoit les données · stocke en SQLite |
| `client_s1.py` | Envoi immédiat sample par sample |
| `client_s2.py` | Envoi groupé par batch de 20 |
| `client_s3.py` | Envoi filtré sur `presence == 1` uniquement |
| `client_common.py` | Fonctions partagées : `load_dataset` · `build_sample` · `post_payload` |

---

## 🏗 Architecture

### Structure du projet

```
IoT_project/
├── 📂 notebooks/ 
├── 📂 dashboard/ 
├── 📂 db/
│   └── iot_monitoring.db
    └── schema.db        ← SQLite (créée automatiquement)
│
├── 📂 data/
│   ├── benign.csv              ← Jeu de données d'entrée
│   ├── netlogs1.csv            ← Logs réseau — Stratégie S1
│   ├── rfid_presence_monitoring_dataset.csv            ← Logs réseau — Stratégie S2
│              ← Logs réseau — Stratégie S3
│
└── 📂 reports/
└── 📂 src/
    ├── server_api.py                ← Serveur Flask (port 5000)
    ├── client_common.py         ← Librairie commune
    ├── client_s1.py             ← Client stratégie S1
    ├── client_s2.py             ← Client stratégie S2
    └── client_s3.py              ← Client stratégie S3
    └── anomaly_detection.py
    └── preprocessing.py
    └── visualization.py  
  
        
```

### Diagramme système

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT SIDE                                │
│                                                                     │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐              │
│  │ client_s1   │   │ client_s2   │   │ client_s3   │              │
│  │  (individ.) │   │  (batch)    │   │  (filtre)   │              │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘              │
│         │                 │                  │                      │
│         └────────────┬────┘──────────────────┘                     │
│                      ▼                                              │
│            ┌──────────────────┐                                     │
│            │  client_common   │  load_dataset · build_sample        │
│            │                  │  post_payload (mesure latence)      │
│            └────────┬─────────┘                                     │
└─────────────────────│───────────────────────────────────────────────┘
                      │  HTTP POST /data  (JSON payload)
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          SERVER SIDE                                │
│                                                                     │
│            ┌──────────────────┐                                     │
│            │   server.py      │  Flask · 0.0.0.0:5000              │
│            │   POST /data     │  → retourne t_recv                  │
│            └────────┬─────────┘                                     │
│                     │                                               │
│          ┌──────────┴──────────┐                                    │
│          ▼                     ▼                                    │
│  ┌───────────────┐   ┌──────────────────┐                          │
│  │  access_log   │   │  network_log     │                          │
│  │  (samples)    │   │  (réservée)      │                          │
│  └───────────────┘   └──────────────────┘                          │
│          └───── iot_monitoring.db ───────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📶 Les 3 stratégies

### Comparaison visuelle

```
Dataset :  [0]  [1✓] [2]  [3✓] [4]  [5]  [6✓] [7]      (✓ = presence==1)
           ─────────────────────────────────────────────────────────────

S1  ──►  →[0] →[1] →[2] →[3] →[4] →[5] →[6] →[7]       8 requêtes
         (chaque sample = 1 requête immédiate)

S2  ──►  ╔═══════════════════════════════════╗ →          1 requête
         ║ [0][1][2][3][4][5][6][7]... ×20   ║
         ╚═══════════════════════════════════╝
         (accumule jusqu'à BATCH_SIZE, puis envoie)

S3  ──►  ✗    →[1] ✗    →[3] ✗    ✗    →[6] ✗            3 requêtes
         (ignore presence==0, envoie uniquement presence==1)
```

---

### S1 — Envoi individuel

```
[sample] ──► POST ──► [sample] ──► POST ──► [sample] ──► POST ...
   ^                     ^                     ^
   │                     │                     │
  t=0ms                t=Δms                t=2Δms        (latence brute)
```

- **Fichier :** `client_s1.py` → `netlog_s1.csv`
- **Usage idéal :** temps réel critique, alerting immédiat
- **Trade-off :** latence minimale ↔ charge réseau maximale

---

### S2 — Envoi par batch

```
Buffer : [ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ][ ]
          ──────────────── BATCH_SIZE = 20 ─────────────────────────────
                                                                    ↓
                                                               POST (×20)
```

- **Fichier :** `client_s2.py` → `netlog_s2.csv`
- **Usage idéal :** bande passante limitée, IoT bas débit
- **Trade-off :** efficacité réseau ↔ latence accrue

> ⚠️ Les samples restants en fin de dataset sont envoyés même si le buffer n'est pas plein.

---

### S3 — Filtrage événementiel

```
[presence=0] ──► ✗ ignoré
[presence=1] ──► POST immédiat  ← uniquement les événements détectés
[presence=0] ──► ✗ ignoré
[presence=1] ──► POST immédiat
```

- **Fichier :** `client_s3.py` → `netlog_s3.csv`
- **Usage idéal :** systèmes d'alarme, détection d'intrusion
- **Trade-off :** trafic réduit ↔ perte des données "vides"

---

### Tableau récapitulatif

| | S1 | S2 | S3 |
|---|:---:|:---:|:---:|
| **Requêtes / dataset** | `N` | `⌈N/20⌉` | `count(presence=1)` |
| **n_samples / requête** | 1 | ≤ 20 | 1 |
| **Latence** | Minimale | Plus haute | Minimale |
| **Charge réseau** | Maximale | Minimale | Réduite |
| **Données perdues** | Aucune | Aucune | presence=0 |
| **Usage** | Temps réel | Bande passante | Alerting |

---

## 🚀 Démarrage rapide

### Prérequis

- Python **3.7+**
- Packages : `flask` · `pandas` · `requests`

```bash
pip install flask pandas requests
```

### Format du dataset d'entrée

Le fichier `data/dataset.csv` doit contenir **au minimum** ces colonnes :

```
timestamp,person_id,presence
2024-01-15T08:30:00,CARD_001,0
2024-01-15T08:30:05,CARD_042,1
2024-01-15T08:30:10,CARD_007,0
```

### Lancement

**Étape 1 — Démarrer le serveur** (laisser ce terminal ouvert)

```bash
cd src
python server.py
# * Running on http://0.0.0.0:5000
```

**Étape 2 — Exécuter les clients** (dans d'autres terminaux)

```bash
cd src
python client_s1.py   # → génère data/netlog_s1.csv
python client_s2.py   # → génère data/netlog_s2.csv
python client_s3.py   # → génère data/netlog_s3.csv
```

**Étape 3 — Vérifier les sorties**

```bash
ls ../data/
# netlog_s1.csv  netlog_s2.csv  netlog_s3.csv
```

---

## 🔌 API Serveur

### Endpoint

```
POST http://127.0.0.1:5000/data
Content-Type: application/json
```

### Payload (requête)

```json
{
  "strategy": "S1",
  "samples": [
    {
      "timestamp": "2024-01-15T08:32:11",
      "person_id": "CARD_042",
      "presence": 1
    }
  ]
}
```

> `samples` peut être un **objet unique** ou une **liste d'objets** (utile pour S2).

### Réponse

```json
{
  "status": "ok",
  "t_recv": "2024-01-15T08:32:11.452319"
}
```

`t_recv` est utilisé par le client pour calculer la **latence réseau** (`t_recv − t_send`).

### Schéma SQLite

```
┌──────────────────────────────────────────┐
│              access_log                  │
├──────────────┬────────────┬──────────────┤
│  timestamp   │  TEXT      │ Horodatage   │
│  person_id   │  TEXT      │ ID carte RFID│
│  presence    │  INTEGER   │ 0 ou 1       │
│  strategy    │  TEXT      │ S1 / S2 / S3 │
└──────────────┴────────────┴──────────────┘

┌──────────────────────────────────────────┐
│  network_log   (réservée — non utilisée) │
└──────────────────────────────────────────┘
```

---

## 📊 Format des logs CSV

Chaque fichier `netlog_sX.csv` contient **une ligne par requête effectuée**.

| Colonne | S1 | S2 | S3 | Description |
|---|:---:|:---:|:---:|---|
| `strategy` | `"S1"` | `"S2"` | `"S3"` | Identifiant de la stratégie |
| `t_send` | ✓ | ✓ | ✓ | Horodatage client à l'envoi |
| `t_recv` | ✓ | ✓ | ✓ | Horodatage serveur retourné |
| `n_samples` | `1` | `≤ 20` | `1` | Nb de samples dans la requête |
| `size_bytes` | ✓ | ✓ | ✓ | Taille du payload JSON (octets) |

**Calcul de la latence :**

```
latence (ms) = (t_recv − t_send) × 1000
```

---

## 📈 Analyse des résultats

```python
import pandas as pd

# Charger les logs
s1 = pd.read_csv("../data/netlog_s1.csv")
s2 = pd.read_csv("../data/netlog_s2.csv")
s3 = pd.read_csv("../data/netlog_s3.csv")

# Calculer la latence en millisecondes
for df in [s1, s2, s3]:
    df["latency_ms"] = (
        pd.to_datetime(df["t_recv"]) - pd.to_datetime(df["t_send"])
    ).dt.total_seconds() * 1000

# Comparaison des indicateurs clés
for name, df in {"S1": s1, "S2": s2, "S3": s3}.items():
    print(f"[{name}]  requêtes={len(df):<6}"
          f"latence_moy={df['latency_ms'].mean():.1f}ms  "
          f"payload_moy={df['size_bytes'].mean():.0f}B")
```

**Métriques à comparer :**

```
┌─────────────────────────────────────────────────────────┐
│  Indicateur          │  S1      │  S2       │  S3       │
│  ────────────────────┼──────────┼───────────┼───────────│
│  Nb de requêtes      │  élevé   │  ÷ 20     │  % détect │
│  Latence moyenne     │  faible  │  élevée   │  faible   │
│  Payload moyen       │  petit   │  grand    │  petit    │
│  Trafic total        │  max     │  minimal  │  réduit   │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Personnalisation

| Paramètre | Fichier | Valeur par défaut | Comment modifier |
|---|---|---|---|
| Taille du batch | `client_s2.py` | `20` | Changer `BATCH_SIZE` |
| Chemin du dataset | `client_common.py` | `../data/dataset.csv` | Modifier le chemin de lecture |
| Adresse du serveur | `client_common.py` | `http://127.0.0.1:5000/data` | Changer l'URL cible |
| Mode fichier CSV | `client_sX.py` | `"w"` (écrase) | Remplacer par `"a"` pour historique |

---

## 📝 Remarques

> **🔴 Important** — Le serveur doit être démarré **avant** tout client.

- Les fichiers `netlog_*.csv` sont **écrasés** à chaque exécution. Pour conserver l'historique, utiliser le mode `"a"` à la place de `"w"`.
- La table `network_log` de la base SQLite est **réservée** — elle pourrait être étendue pour stocker les métriques réseau côté serveur.
- Les dossiers `db/` et `data/` sont **créés automatiquement** par les scripts si nécessaire.

---

## 🏁 Conclusion

Ce projet fournit une base complète pour étudier l'impact des stratégies de transmission IoT sur les performances réseau :

```
S1 ──► Réactivité maximale, charge réseau élevée
S2 ──► Efficacité réseau, latence accrue
S3 ──► Trafic minimal, filtrage événementiel
```

Chaque stratégie représente un **compromis** à évaluer selon les contraintes du système cible : bande passante, temps réel, criticité des données.

---

*Pour toute question ou contribution, référez-vous aux commentaires dans les fichiers sources.*