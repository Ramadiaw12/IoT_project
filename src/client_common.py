import json
import time
import requests
import pandas as pd
from pathlib import Path

# Configuration des endpoints et des chemins
SERVER_URL = "http://127.0.0.1:5000/data"

# Gestion dynamique des chemins pour assurer la portabilité du script
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "benign.csv"
presence_col = "HH_L5_magnitude"

def load_dataset(n_rows=10000):
    """
    Charge les données et calcule un seuil de détection statistique.
    """
    df = pd.read_csv(DATA_PATH, nrows=n_rows)
    
    # Logique métier : On définit la 'présence' si la magnitude dépasse 
    # la moyenne + un écart-type (détection d'anomalie/activité)
    seuil = df[presence_col].mean() + df[presence_col].std()
    df["presence"] = (df[presence_col] > seuil).astype(int)
    
    return df

def build_sample(row):
    """
    Formate une ligne du DataFrame en message JSON standardisé.
    """
    ts = time.time()
    return {
        "timestamp": ts,
        "person_id": f"RFID_{row.name % 100}", # Simulation d'identifiants tournants
        "presence": int(row["presence"]),
    }

def post_payload(strategy, samples):
    """
    Encapsule les données, gère la sérialisation et mesure les performances réseau.
    """
    payload = {
        "strategy": strategy,
        "samples": samples if isinstance(samples, list) else samples,
    }
    
    # Sérialisation manuelle pour mesurer précisément la taille du payload en octets
    body = json.dumps(payload).encode()
    size_bytes = len(body)
    
    t_send = time.time()
    
    # Transmission synchrone vers l'API Flask/FastAPI
    resp = requests.post(
        SERVER_URL, 
        data=body,
        headers={"Content-Type": "application/json"}
    )
    
    # On récupère le timestamp du serveur pour calculer plus tard la latence
    t_recv = resp.json()["t_recv"]
    
    return t_send, t_recv, size_bytes