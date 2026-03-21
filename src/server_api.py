# Import des bibliothèques nécessaires
from flask import Flask, request, jsonify   # Framework web
from datetime import datetime               # Pour les horodatages
import sqlite3                               # Base de données légère
from pathlib import Path                     # Manipulation robuste des chemins
import json                                  # (non utilisé directement mais peut servir)

# Définition du chemin absolu de la base de données.
# On remonte d’un dossier parent par rapport à l’emplacement du script,
# et on place la base dans un sous-dossier 'db'.
# Exemple : /home/user/projet/src/server.py → /home/user/projet/db/iot_monitoring.db
DB_PATH = Path(__file__).resolve().parents[1] / "db" / "iot_monitoring.db"

# Création de l’application Flask
app = Flask(__name__)


def init_db():
    """
    Initialise la base de données : crée les tables si elles n’existent pas.
    À appeler au démarrage du serveur.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Table des logs d’accès (authentifications)
    c.execute("""
    CREATE TABLE IF NOT EXISTS access_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,       -- Horodatage de l’événement (string ISO)
        person_id TEXT,       -- Identifiant de la personne
        presence INTEGER,     -- 1 = présent, 0 = absent
        strategy TEXT         -- Stratégie de transmission utilisée
    )
    """)

    # Table des logs réseau (pour mesurer les performances)
    c.execute("""
    CREATE TABLE IF NOT EXISTS network_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        strategy TEXT,        -- Stratégie utilisée pour cette transmission
        t_send REAL,          -- Timestamp d’envoi (côté client)
        t_recv REAL,          -- Timestamp de réception (côté serveur)
        n_samples INTEGER,    -- Nombre d’échantillons envoyés
        size_bytes INTEGER    -- Taille totale des données en octets
    )
    """)

    conn.commit()
    conn.close()


@app.route("/data", methods=["POST"])
def receive_data():
    """
    Point d’entrée pour recevoir les données IoT.
    Attend un JSON contenant :
        - "strategy" : nom de la stratégie de transmission (optionnel, défaut "UNK")
        - "samples"  : soit un dictionnaire unique, soit une liste de dictionnaires.
                       Chaque dictionnaire doit contenir :
                         "timestamp" (str), "person_id" (str), "presence" (int)

    Renvoie un JSON avec le timestamp de réception côté serveur (t_recv).
    """
    # Récupération des données JSON de la requête
    data = request.get_json()
    strategy = data.get("strategy", "UNK")  # Valeur par défaut si absent

    # Gestion des deux formats possibles pour "samples"
    if isinstance(data.get("samples"), list):
        samples = data["samples"]           # Cas S2 : une liste d’échantillons
    else:
        samples = [data["samples"]]         # Cas S1 / S3 : un seul échantillon

    # Connexion à la base de données
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Insertion de chaque échantillon dans la table access_log
    for s in samples:
        c.execute(
            "INSERT INTO access_log(timestamp, person_id, presence, strategy) VALUES (?,?,?,?)",
            (s["timestamp"], s["person_id"], s["presence"], strategy),
        )

    # Validation de la transaction
    conn.commit()
    conn.close()

    # Réponse : on renvoie l’instant de réception (UTC) pour permettre au client
    # de calculer la latence réseau (t_recv - t_send)
    return jsonify({"t_recv": datetime.utcnow().timestamp()})


if __name__ == "__main__":
    # Initialisation de la base de données au démarrage du serveur
    init_db()

    # Lancement de l’application sur toutes les interfaces réseau, port 5000
    # debug=False pour éviter les rechargements intempestifs en production
    app.run(host="0.0.0.0", port=5000, debug=False)