from client_common import load_dataset, build_sample, post_payload
import csv
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parents[1]
NETLOG = BASE_DIR / "data" / "netlog_s2.csv"
BATCH_SIZE = 20  # N

def main():
    df = load_dataset()
    buffer = []
    NETLOG.parent.mkdir(exist_ok=True, parents=True)
    with NETLOG.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["strategy", "t_send", "t_recv", "n_samples", "size_bytes"])
        for _, row in df.iterrows():
            buffer.append(build_sample(row))
            time.sleep(0.1)
            if len(buffer) == BATCH_SIZE:
                t_send, t_recv, size_bytes = post_payload("S2", buffer)
                writer.writerow(["S2", t_send, t_recv, len(buffer), size_bytes])
                buffer = []

        if buffer:
            t_send, t_recv, size_bytes = post_payload("S2", buffer)
            writer.writerow(["S2", t_send, t_recv, len(buffer), size_bytes])

if __name__ == "__main__":
    main()