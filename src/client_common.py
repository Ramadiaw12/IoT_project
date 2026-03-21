import json
import time
import requests
import pandas as pd
from pathlib import Path

SERVER_URL = "http://127.0.0.1:5000/data"

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "benign.csv"
presence_col = "HH_L5_magnitude"

def load_dataset(n_rows=10000):
    df = pd.read_csv(DATA_PATH, nrows=n_rows)
    seuil = df[presence_col].mean() + df[presence_col].std()
    df["presence"] = (df[presence_col] > seuil).astype(int)
    return df

def build_sample(row):
    ts = time.time()
    return {
        "timestamp": ts,
        "person_id": f"RFID_{row.name % 100}",
        "presence": int(row["presence"]),
    }

def post_payload(strategy, samples):
    payload = {
        "strategy": strategy,
        "samples": samples if isinstance(samples, list) else samples,
    }
    body = json.dumps(payload).encode()
    size_bytes = len(body)
    t_send = time.time()
    resp = requests.post(SERVER_URL, data=body,
                         headers={"Content-Type": "application/json"})
    t_recv = resp.json()["t_recv"]
    return t_send, t_recv, size_bytes