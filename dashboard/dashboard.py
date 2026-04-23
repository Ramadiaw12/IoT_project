import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(page_title="Monitoring Hospitalier - Accès & Mouvements", layout="wide")
st.title("🏥 Dashboard de monitoring des accès - Hôpital")
st.markdown("Détection d'allers-retours anormaux (ex: pharmacie)")

# --------------------------------------------------
# 1. CHARGEMENT DES DONNÉES (à adapter selon ton fichier)
# --------------------------------------------------
@st.cache_data
def load_data():
    # Soit tu charges ton fichier CSV existant
    df = pd.read_csv('data/mouvement.csv')  # adapte le chemin
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

@st.cache_data
def generate_rfid_events(df, location_col='location_id', session_col='session'):
    """Simule les événements RFID à partir des changements de location_id"""
    events = []
    for session_id, group in df.groupby(session_col):
        group = group.sort_index()
        prev_loc = None
        for ts, row in group.iterrows():
            curr_loc = row[location_col]
            if prev_loc is not None and curr_loc != prev_loc:
                # Sortie
                events.append({
                    'timestamp': ts,
                    'session': session_id,
                    'event': 'exit',
                    'location': prev_loc,
                    'location_name': get_location_name(prev_loc)
                })
                # Entrée
                events.append({
                    'timestamp': ts,
                    'session': session_id,
                    'event': 'enter',
                    'location': curr_loc,
                    'location_name': get_location_name(curr_loc)
                })
            prev_loc = curr_loc
    return pd.DataFrame(events)

def get_location_name(loc_id):
    """Mapper les IDs en noms de pièces (personnalisable)"""
    mapping = {34: "Pharmacie", 35: "Salle d'attente", 36: "Bureau médecin", 37: "Couloir"}
    return mapping.get(int(loc_id), f"Zone {loc_id}")

# --------------------------------------------------
# 2. DÉTECTION DES ALLERS-RETOURS
# --------------------------------------------------
def detect_round_trips(events_df, zone_name="Pharmacie", time_window_minutes=30):
    """
    Compte les allers-retours vers une zone donnée.
    Un aller-retour = entrée dans la zone puis sortie (ou l'inverse selon contexte)
    Ici on considère qu'un aller-retour complet est une entrée suivie d'une sortie.
    """
    zone_events = events_df[events_df['location_name'] == zone_name].copy()
    zone_events = zone_events.sort_values('timestamp')
    
    trips = []
    entry_time = None
    for _, row in zone_events.iterrows():
        if row['event'] == 'enter' and entry_time is None:
            entry_time = row['timestamp']
        elif row['event'] == 'exit' and entry_time is not None:
            duration = (row['timestamp'] - entry_time).total_seconds() / 60
            trips.append({
                'entry': entry_time,
                'exit': row['timestamp'],
                'duration_min': duration
            })
            entry_time = None
    return trips

# --------------------------------------------------
# 3. INTERFACE STREAMLIT
# --------------------------------------------------
# Chargement
df_raw = load_data()
rfid_events = generate_rfid_events(df_raw)

# Sidebar filtres
st.sidebar.header("Filtres")
sessions = rfid_events['session'].unique()
selected_session = st.sidebar.selectbox("Session (utilisateur)", sessions)
zone_list = rfid_events['location_name'].unique()
selected_zone = st.sidebar.selectbox("Zone à surveiller", zone_list, index=list(zone_list).index("Pharmacie") if "Pharmacie" in zone_list else 0)
threshold = st.sidebar.number_input("Seuil d'alerte (nombre d'allers-retours)", min_value=1, value=10)

# Filtrer par session
session_events = rfid_events[rfid_events['session'] == selected_session]

# Détection des allers-retours pour la zone choisie
round_trips = detect_round_trips(session_events, zone_name=selected_zone)
n_trips = len(round_trips)

# Alertes
if n_trips >= threshold:
    st.error(f"⚠️ ALERTE : {n_trips} allers-retours détectés dans {selected_zone} (seuil={threshold})")
else:
    st.success(f"✓ {n_trips} allers-retours dans {selected_zone} (seuil={threshold})")

# --------------------------------------------------
# 4. VISUALISATIONS
# --------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.metric("Nombre d'allers-retours", n_trips, delta=None)
with col2:
    st.metric("Durée moyenne (min)", round(np.mean([t['duration_min'] for t in round_trips]), 1) if round_trips else 0)

# Timeline des événements
st.subheader("Timeline des entrées/sorties")
fig = px.scatter(session_events, x='timestamp', y='location_name', color='event',
                 title=f"Activité dans l'hôpital - Session {selected_session}",
                 labels={'timestamp': 'Heure', 'location_name': 'Zone'})
st.plotly_chart(fig, use_container_width=True)

# Histogramme des fréquences par zone
st.subheader("Fréquence des passages par zone")
zone_counts = session_events.groupby(['location_name', 'event']).size().reset_index(name='count')
fig_bar = px.bar(zone_counts, x='location_name', y='count', color='event', barmode='group',
                 title="Nombre d'entrées/sorties par zone")
st.plotly_chart(fig_bar, use_container_width=True)

# Détails des allers-retours
if round_trips:
    st.subheader("Détail des allers-retours")
    trips_df = pd.DataFrame(round_trips)
    trips_df['entry'] = trips_df['entry'].dt.strftime('%H:%M:%S')
    trips_df['exit'] = trips_df['exit'].dt.strftime('%H:%M:%S')
    
    st.dataframe(trips_df)
else:
    st.info("Aucun aller-retour détecté pour cette zone.")

# Optionnel : replay des mouvements (animation)
st.subheader("Replay des mouvements")
if st.button("Lancer l'animation"):
    st.write("Fonctionnalité à implémenter : animation sur la carte de l'hôpital")