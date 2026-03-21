# client_s1.py
# Ce script lit un jeu de données, construit des échantillons et les envoie au serveur
# en utilisant la stratégie de transmission "S1". Il enregistre dans un fichier CSV
# les latences réseau et la taille des paquets pour chaque envoi.

# Import des fonctions utilitaires fournies par le module client_common
# - load_dataset : charge les données (probablement un fichier CSV contenant les logs)
# - build_sample : transforme une ligne de données en un dictionnaire prêt à être envoyé
# - post_payload : envoie les données au serveur et retourne (t_send, t_recv, size_bytes)
from client_common import load_dataset, build_sample, post_payload

import csv                # Pour écrire les métriques réseau dans un fichier CSV
from pathlib import Path  # Gestion robuste des chemins de fichiers
import time               # Pour simuler un intervalle d'échantillonnage

# Construction du chemin absolu vers le dossier racine du projet (deux niveaux au-dessus)
BASE_DIR = Path(__file__).resolve().parents[1]

# Chemin complet du fichier CSV qui stockera les logs réseau pour la stratégie S1
NETLOG = BASE_DIR / "data" / "netlog_s1.csv"

def main():
    """
    Fonction principale :
    - Charge le dataset via load_dataset()
    - Crée le dossier parent du fichier NETLOG s'il n'existe pas
    - Ouvre le fichier CSV en écriture et écrit l'en-tête
    - Pour chaque ligne du dataset :
        - Construit un échantillon (sample) à envoyer
        - Envoie au serveur avec la stratégie "S1" et récupère les métriques
        - Écrit une ligne dans le CSV avec les métriques
        - Attend 0.1 seconde pour simuler un intervalle d'échantillonnage réaliste
    """
    # 1. Chargement des données (probablement un DataFrame pandas)
    df = load_dataset()

    # 2. Création du répertoire "data" si inexistant
    NETLOG.parent.mkdir(exist_ok=True, parents=True)

    # 3. Ouverture du fichier CSV en écriture (mode 'w' écrase l'ancien fichier)
    with NETLOG.open("w", newline="") as f:
        writer = csv.writer(f)

        # Écriture de l'en-tête : colonnes pour la stratégie, timestamps, nombre d'échantillons, taille
        writer.writerow(["strategy", "t_send", "t_recv", "n_samples", "size_bytes"])

        # 4. Parcours de chaque ligne du dataset
        #    df.iterrows() retourne (index, row). On ignore l'index avec '_'
        for _, row in df.iterrows():
            # Construction d'un dictionnaire représentant l'échantillon
            sample = build_sample(row)

            # Envoi au serveur avec la stratégie "S1"
            # post_payload renvoie :
            #   t_send     : timestamp d'envoi (côté client)
            #   t_recv     : timestamp de réception renvoyé par le serveur
            #   size_bytes : taille de la charge utile envoyée (en octets)
            t_send, t_recv, size_bytes = post_payload("S1", sample)

            # Écriture d'une ligne de métriques dans le CSV
            writer.writerow(["S1", t_send, t_recv, 1, size_bytes])

            # Pause de 100 ms pour simuler une fréquence d'acquisition réaliste
            # (ex : 10 échantillons par seconde)
            time.sleep(0.1)

# Point d'entrée du script : exécute main() uniquement si le fichier est lancé directement
if __name__ == "__main__":
    main()