# client_s2.py
# Ce script implémente un client IoT avec transmission par lots (batching).
# Les échantillons sont accumulés dans un buffer jusqu'à atteindre BATCH_SIZE,
# puis envoyés en une seule requête POST. Cette stratégie permet de réduire
# le nombre d'appels réseau et de mutualiser les coûts de transmission.

from client_common import load_dataset, build_sample, post_payload
import csv
from pathlib import Path
import time

# Chemin du dossier racine du projet (deux niveaux au-dessus du script)
BASE_DIR = Path(__file__).resolve().parents[1]

# Fichier CSV où seront enregistrées les métriques réseau pour la stratégie S2
NETLOG = BASE_DIR / "data" / "netlog_s2.csv"

# Taille du lot : nombre d'échantillons accumulés avant envoi
BATCH_SIZE = 20  # N

def main():
    """
    Fonction principale :
    - Charge le dataset via load_dataset()
    - Initialise un buffer vide pour accumuler les échantillons
    - Crée le dossier parent pour NETLOG s'il n'existe pas
    - Ouvre le fichier CSV en écriture et écrit l'en-tête
    - Parcourt chaque ligne du dataset :
        - Construit un échantillon et l'ajoute au buffer
        - Pause de 0.1 s pour simuler l'intervalle d'acquisition
        - Si le buffer atteint BATCH_SIZE, on envoie le lot et on vide le buffer
    - À la fin du dataset, envoie le dernier lot (même s'il est plus petit que BATCH_SIZE)
    """
    # Chargement des données (probablement un DataFrame pandas)
    df = load_dataset()

    # Buffer pour accumuler les échantillons avant envoi
    buffer = []

    # Création du répertoire "data" si inexistant
    NETLOG.parent.mkdir(exist_ok=True, parents=True)

    # Ouverture du fichier CSV en écriture (mode 'w' écrase l'ancien fichier)
    with NETLOG.open("w", newline="") as f:
        writer = csv.writer(f)

        # Écriture de l'en-tête : colonnes pour les métriques réseau
        writer.writerow(["strategy", "t_send", "t_recv", "n_samples", "size_bytes"])

        # Parcours de chaque ligne du dataset
        for _, row in df.iterrows():
            # Construction de l'échantillon à partir de la ligne
            sample = build_sample(row)

            # Ajout de l'échantillon au buffer
            buffer.append(sample)

            # Pause pour simuler le rythme d'acquisition (10 Hz)
            time.sleep(0.1)

            # Si le buffer a atteint la taille cible, on envoie le lot
            if len(buffer) == BATCH_SIZE:
                # Envoi du lot au serveur avec la stratégie "S2"
                # Note : post_payload accepte une liste d'échantillons (voir serveur)
                t_send, t_recv, size_bytes = post_payload("S2", buffer)

                # Enregistrement des métriques : nombre d'échantillons = taille du lot
                writer.writerow(["S2", t_send, t_recv, len(buffer), size_bytes])

                # Réinitialisation du buffer pour le prochain lot
                buffer = []

        # Après la boucle, envoi des échantillons restants (buffer non vide)
        if buffer:
            t_send, t_recv, size_bytes = post_payload("S2", buffer)
            writer.writerow(["S2", t_send, t_recv, len(buffer), size_bytes])

# Point d'entrée du script
if __name__ == "__main__":
    main()