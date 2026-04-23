"""
Dashboard de monitoring hospitalier – Version Premium
Auteur : SARA
Thème : Dark mode avec animations, couleurs vives, graphiques interactifs
Fonctionnalités : visualisation des accès, détection d'anomalies, alertes, consommation énergétique
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

# --------------------------------------------------
# Configuration de la page (thème dark personnalisé)
# --------------------------------------------------
st.set_page_config(
    page_title="Monitoring Hôpital - Accès & Mouvements",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CSS personnalisé : fond noir, animations, cartes, polices
# --------------------------------------------------
st.markdown("""
<style>
    /* Fond global et couleurs */
    .stApp {
        background: linear-gradient(135deg, #0a0f1e 0%, #0c1222 100%);
        color: #e0e0e0;
    }
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background: rgba(18, 25, 45, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid #2a3a5a;
    }
    /* Cartes métriques animées */
    .metric-card {
        background: linear-gradient(145deg, #1e2a3a, #0f1722);
        border-radius: 20px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #2c3e50;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.5);
        border-color: #4a6a8a;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00c6fb, #005bea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #a0b0c0;
        letter-spacing: 1px;
    }
    /* Alertes animées */
    .alert-box {
        animation: pulse 1.5s infinite;
        border-radius: 12px;
        padding: 0.8rem;
        font-weight: bold;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 80, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 80, 80, 0); }
    }
    /* Boutons et sélecteurs */
    .stButton > button {
        background: linear-gradient(90deg, #2c3e50, #1a2635);
        color: white;
        border-radius: 30px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        background: linear-gradient(90deg, #3e5a70, #2a3a50);
    }
    /* Titres */
    h1, h2, h3, h4 {
        background: linear-gradient(90deg, #ffffff, #88aaff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    /* Dataframe */
    .dataframe {
        background: #111a24;
        border-radius: 15px;
        border: none;
    }
    /* Sidebar text */
    .css-1v3fvcr, .css-1y4p8pa {
        color: #ccddee;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Chargement des données (caché)
# --------------------------------------------------
@st.cache_data
def load_rfid_events():
    """Charge les événements RFID simulés depuis le CSV"""
    df = pd.read_csv('outputs/rfid_events_simules.csv', parse_dates=['timestamp'])
    if 'zone' not in df.columns:
        zone_mapping = {34: "Pharmacie", 35: "Salle d'attente", 36: "Bureau médecin",
                        37: "Couloir", 38: "Chambre patient"}
        df['zone'] = df['location_id'].map(zone_mapping).fillna(f"Zone {df['location_id']}")
    return df

@st.cache_data
def compute_round_trips(events_df, target_zone="Pharmacie"):
    sub = events_df[events_df['zone'] == target_zone].sort_values('timestamp')
    trips = []
    entry_time = None
    for _, row in sub.iterrows():
        if row['event'] == 'enter' and entry_time is None:
            entry_time = row['timestamp']
        elif row['event'] == 'exit' and entry_time is not None:
            duration = (row['timestamp'] - entry_time).total_seconds()
            trips.append({'entry': entry_time, 'exit': row['timestamp'], 'duration_sec': duration})
            entry_time = None
    return trips

def compute_transmission_metrics(total_events, time_span_sec, strategy, N=5):
    TX_CURRENT_MA = 30
    TX_DURATION_S = 0.5
    ENERGY_PER_TX_MAH = (TX_CURRENT_MA * TX_DURATION_S) / 3600
    EVENT_SIZE_BYTES = 200
    LATENCY_PER_TX_S = 0.1
    if total_events == 0:
        return {'consumption_mah': 0, 'avg_latency_s': 0, 'bandwidth_kbps': 0}
    if strategy == 'immediate':
        num_tx = total_events
        avg_latency = LATENCY_PER_TX_S
        total_bytes = total_events * EVENT_SIZE_BYTES
    elif strategy == 'aggregated':
        num_tx = math.ceil(total_events / N)
        avg_inter_event = time_span_sec / total_events if total_events > 1 else 1
        agg_delay = (N / 2) * avg_inter_event
        avg_latency = agg_delay + LATENCY_PER_TX_S
        total_bytes = num_tx * (EVENT_SIZE_BYTES * N)
    elif strategy == 'anomaly_only':
        num_tx = 1
        avg_latency = time_span_sec / 2
        total_bytes = total_events * EVENT_SIZE_BYTES
    else:
        raise ValueError("Stratégie inconnue")
    consumption_mah = num_tx * ENERGY_PER_TX_MAH
    bandwidth_kbps = (total_bytes * 8) / (time_span_sec * 1000) if time_span_sec > 0 else 0
    return {'consumption_mah': consumption_mah, 'avg_latency_s': avg_latency, 'bandwidth_kbps': bandwidth_kbps}

# --------------------------------------------------
# Chargement effectif
# --------------------------------------------------
rfid_events = load_rfid_events()
total_events = len(rfid_events)
time_span = (rfid_events['timestamp'].max() - rfid_events['timestamp'].min()).total_seconds()
if time_span <= 0:
    time_span = 1

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.header("🔧 Paramètres")
available_zones = rfid_events['zone'].unique()
target_zone = st.sidebar.selectbox("Zone cible pour la détection d'anomalies", available_zones,
                                   index=list(available_zones).index("Pharmacie") if "Pharmacie" in available_zones else 0)
anomaly_threshold = st.sidebar.number_input("Seuil d'alerte (nombre d'allers-retours)", min_value=1, value=10, step=1)
session_list = rfid_events['session'].unique()
selected_session = st.sidebar.selectbox("Session (utilisateur)", session_list)
session_events = rfid_events[rfid_events['session'] == selected_session]

trips = compute_round_trips(session_events, target_zone)
n_trips = len(trips)

# Alerte animée dans la sidebar
if n_trips >= anomaly_threshold:
    st.sidebar.markdown(f'<div class="alert-box" style="background:#ff4444; color:white;">🚨 ALERTE : {n_trips} allers-retours détectés dans {target_zone} (seuil={anomaly_threshold})</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<div style="background:#2e7d32; border-radius:12px; padding:0.8rem;">✓ {n_trips} allers-retours dans {target_zone} (seuil={anomaly_threshold})</div>', unsafe_allow_html=True)

# Rapport consommation
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Rapport de consommation")
metrics_imm = compute_transmission_metrics(total_events, time_span, 'immediate')
metrics_agg = compute_transmission_metrics(total_events, time_span, 'aggregated', N=5)
has_anomaly = n_trips >= anomaly_threshold
metrics_anom = compute_transmission_metrics(total_events, time_span, 'anomaly_only')
if not has_anomaly:
    metrics_anom['consumption_mah'] = 0
    metrics_anom['avg_latency_s'] = 0
    metrics_anom['bandwidth_kbps'] = 0

st.sidebar.write("**S1 - Immédiat :**")
st.sidebar.write(f"⚡ {metrics_imm['consumption_mah']:.4f} mAh | ⏱️ {metrics_imm['avg_latency_s']:.2f} s | 📡 {metrics_imm['bandwidth_kbps']:.2f} kbps")
st.sidebar.write("**S2 - Agrégé (N=5) :**")
st.sidebar.write(f"⚡ {metrics_agg['consumption_mah']:.4f} mAh | ⏱️ {metrics_agg['avg_latency_s']:.2f} s | 📡 {metrics_agg['bandwidth_kbps']:.2f} kbps")
st.sidebar.write("**S3 - Anomalie seule :**")
st.sidebar.write(f"⚡ {metrics_anom['consumption_mah']:.4f} mAh | ⏱️ {metrics_anom['avg_latency_s']:.2f} s | 📡 {metrics_anom['bandwidth_kbps']:.2f} kbps")

# --------------------------------------------------
# Corps principal
# --------------------------------------------------
st.title("🏥 Tableau de bord - Surveillance des accès hospitaliers")
st.markdown(f"**Session :** {selected_session} &nbsp;&nbsp; | &nbsp;&nbsp; **Zone surveillée :** {target_zone} &nbsp;&nbsp; | &nbsp;&nbsp; **Allers-retours :** {n_trips}")

# Métriques en cartes animées (utilisation de colonnes + HTML)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_events}</div>
        <div class="metric-label">Événements RFID</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_trips}</div>
        <div class="metric-label">Allers-retours</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{time_span/60:.1f}</div>
        <div class="metric-label">Durée (minutes)</div>
    </div>
    """, unsafe_allow_html=True)

# Graphiques avec template plotly_dark et couleurs personnalisées
st.subheader("📅 Timeline des entrées/sorties")
fig_timeline = px.scatter(session_events, x='timestamp', y='zone', color='event',
                          title=f"Activité - Session {selected_session}",
                          labels={'timestamp': 'Temps', 'zone': 'Zone', 'event': 'Événement'},
                          color_discrete_map={'enter': '#00ffaa', 'exit': '#ff5555'},
                          hover_data=['location_id', 'is_moving'])
fig_timeline.update_traces(marker=dict(size=12, symbol='circle', line=dict(width=1, color='white')))
fig_timeline.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,20,35,0.8)',
                           font=dict(color='#e0e0e0'), title_font=dict(size=18, color='#88aaff'))
st.plotly_chart(fig_timeline, use_container_width=True)

if trips:
    trips_df = pd.DataFrame(trips)
    trips_df['entry'] = trips_df['entry'].dt.strftime('%H:%M:%S')
    trips_df['exit'] = trips_df['exit'].dt.strftime('%H:%M:%S')
    st.subheader(f"🔄 Allers-retours détaillés - {target_zone}")
    st.dataframe(trips_df, use_container_width=True)

    fig_dur = px.histogram(trips_df, x='duration_sec', nbins=20,
                           title=f"Distribution des durées de présence dans {target_zone}",
                           labels={'duration_sec': 'Durée (secondes)'},
                           color_discrete_sequence=['#00c6fb'])
    fig_dur.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,20,35,0.8)')
    st.plotly_chart(fig_dur, use_container_width=True)
else:
    st.info(f"Aucun aller-retour détecté pour {target_zone} dans cette session.")

st.subheader("🍩 Répartition des événements par zone")
zone_counts = session_events['zone'].value_counts().reset_index()
zone_counts.columns = ['zone', 'count']
fig_pie = px.pie(zone_counts, values='count', names='zone', title="Proportion des événements par zone",
                 color_discrete_sequence=px.colors.sequential.RdBu, hole=0.4)
fig_pie.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,20,35,0.8)')
st.plotly_chart(fig_pie, use_container_width=True)

if n_trips > 0:
    trips_cumul = pd.DataFrame(trips)
    trips_cumul['cumul'] = range(1, len(trips_cumul)+1)
    fig_cumul = px.line(trips_cumul, x='exit', y='cumul',
                        title=f"Allers-retours cumulés vers {target_zone}",
                        labels={'exit': 'Heure de sortie', 'cumul': 'Nombre cumulé'},
                        markers=True, line_shape='linear')
    fig_cumul.add_hline(y=anomaly_threshold, line_dash="dash", line_color="red", annotation_text=f"Seuil = {anomaly_threshold}")
    fig_cumul.update_traces(line=dict(color='#ffaa44', width=3), marker=dict(size=8, color='#ffaa44'))
    fig_cumul.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,20,35,0.8)')
    st.plotly_chart(fig_cumul, use_container_width=True)

st.subheader("📈 Rapport de consommation globale des stratégies de transmission")
report_df = pd.DataFrame({
    'Stratégie': ['Immédiate', 'Agrégation (N=5)', 'Anomalie seule'],
    'Consommation (mAh)': [metrics_imm['consumption_mah'], metrics_agg['consumption_mah'], metrics_anom['consumption_mah']],
    'Latence moyenne (s)': [metrics_imm['avg_latency_s'], metrics_agg['avg_latency_s'], metrics_anom['avg_latency_s']],
    'Bande passante (kbps)': [metrics_imm['bandwidth_kbps'], metrics_agg['bandwidth_kbps'], metrics_anom['bandwidth_kbps']]
})
st.dataframe(report_df.style.background_gradient(cmap='Blues', subset=['Consommation (mAh)', 'Latence moyenne (s)', 'Bande passante (kbps)']), use_container_width=True)

fig_comp = go.Figure()
fig_comp.add_trace(go.Bar(x=report_df['Stratégie'], y=report_df['Consommation (mAh)'],
                          name='Consommation (mAh)', marker_color='#00c6fb', marker_line_color='white', marker_line_width=1))
fig_comp.add_trace(go.Bar(x=report_df['Stratégie'], y=report_df['Latence moyenne (s)'],
                          name='Latence (s)', marker_color='#ffaa44', yaxis='y2'))
fig_comp.update_layout(title="Comparaison des stratégies",
                       xaxis_title="Stratégie",
                       yaxis_title="Consommation (mAh)",
                       yaxis2=dict(title="Latence (s)", overlaying='y', side='right'),
                       legend=dict(x=0.8, y=1.1, font=dict(color='white')),
                       template='plotly_dark',
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(15,20,35,0.8)')
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")
st.caption("Dashboard développé dans le cadre du projet IoT - Monitoring hospitalier | Design premium dark & animations")