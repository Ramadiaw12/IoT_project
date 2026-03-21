from client_common import load_dataset, build_sample, post_payload
import csv
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parents[1]
NETLOG = BASE_DIR / "data" / "netlog_s1.csv"

def main():
    df = load_dataset()
    NETLOG.parent.mkdir(exist_ok=True, parents=True)
    with NETLOG.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["strategy", "t_send", "t_recv", "n_samples", "size_bytes"])
        for _, row in df.iterrows():
            sample = build_sample(row)
            t_send, t_recv, size_bytes = post_payload("S1", sample)
            writer.writerow(["S1", t_send, t_recv, 1, size_bytes])
            time.sleep(0.1)  # fréq. d’échantillonnage simulée

if __name__ == "__main__":
    main()