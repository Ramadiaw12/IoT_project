import pandas as pd
import numpy as np

def load_and_clean(filepath):
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    # Supprimer les doublons éventuels
    df = df[~df.index.duplicated(keep='first')]
    # Trier
    df.sort_index(inplace=True)
    return df

def resample_and_filter(df, freq='0.1s'):
    # Rééchantillonnage à 10 Hz (moyenne)
    df_resampled = df.resample(freq).mean()
    # Interpolation des petites lacunes
    df_resampled.interpolate(method='linear', limit=5, inplace=True)
    return df_resampled