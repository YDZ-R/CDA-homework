"""Shared paths and display settings; no network access is used by the pipeline."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN = ROOT / 'data/raw', ROOT / 'data/clean'
TABLES, FIGURES = ROOT / 'outputs/tables', ROOT / 'outputs/figures'
for folder in [CLEAN, TABLES, FIGURES, ROOT / 'outputs/dashboard', ROOT / 'docs']:
    folder.mkdir(parents=True, exist_ok=True)
START, END = '2023-11-01', '2025-12-31'
SEED = 241
COLORS = ['#287D8E', '#79B9BB', '#F1B09A', '#8CA9CE', '#AB9ABD']
BG, INK, MUTED = '#F8FAFB', '#253F4B', '#657E89'

def save_table(frame, name, index=False):
    frame.to_csv(TABLES / (name + '.csv'), index=index, encoding='utf-8-sig')

def dump(obj, path):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def city_data():
    return pd.read_csv(CLEAN / 'city_daily.csv', parse_dates=['date']).set_index('date')

def district_data():
    return pd.read_csv(CLEAN / 'district_daily.csv', parse_dates=['date'])
