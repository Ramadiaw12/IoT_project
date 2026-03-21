# client_s3.py
# Ce script implémente une stratégie de transmission basée sur la détection d'anomalies.
# Seuls les échantillons où la présence est détectée (presence == 1) sont envoyés.
# Cela permet de réduire drastiquement le trafic réseau dans les périodes d'inactivité,
# tout en transmettant les événements pertinents.

from client_common import load_dataset, build_sample, post_payload
import csv
from pathlib import Path
import time

# Chemin du dossier racine du projet
BASE_DIR = Path(__file__).resolve().parents[1]

# Fichier CSV pour enregistrer les métriques réseau pour la stratégie S3
NETLOG = BASE_DIR / "data" / "netlog_s3.csv"

def main():
    """
    Fonction principale :
    - Charge le dataset via load_dataset()
    - Crée le dossier parent pour NETLOG s'il n'existe pas
    - Ouvre le fichier CSV en écriture et écrit l'en-tête
    - Parcourt chaque ligne du dataset :
        - Vérifie si la présence vaut 1 (événement d'activité)
        - Si oui, construit l'échantillon, l'envoie au serveur et enregistre les métriques
        - Si non, ignore l'échantillon (aucune transmission)
        - Pause de 0.1 s pour simuler le rythme d'acquisition
    """
    # Chargement des données
    df = load_dataset()

    # Création du répertoire "data" si inexistant
    NETLOG.parent.mkdir(exist_ok=True, parents=True)

    # Ouverture du fichier CSV en écriture (écrase l'ancien)
    with NETLOG.open("w", newline="") as f:
        writer = csv.writer(f)

        # Écriture de l'en-tête
        writer.writerow(["strategy", "t_send", "t_recv", "n_samples", "size_bytes"])

        # Parcours de chaque ligne du dataset
        for _, row in df.iterrows():
            # Condition d'envoi : présence détectée (1)
            if int(row["presence"]) == 1:
                # Construction de l'échantillon à partir de la ligne
                sample = build_sample(row)

                # Envoi au serveur avec la stratégie "S3"
                t_send, t_recv, size_bytes = post_payload("S3", sample)

                # Enregistrement des métriques (un seul échantillon par paquet)
                writer.writerow(["S3", t_send, t_recv, 1, size_bytes])
            else:
                # Échantillon ignoré : on ne fait rien, mais on pourrait compter
                # le nombre d'ignorés pour des statistiques.
                pass

            # Pause pour simuler une fréquence d'acquisition de 10 Hz
            time.sleep(0.1)

# Point d'entrée du script
if __name__ == "__main__":
    main()