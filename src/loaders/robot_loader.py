import argparse
from pathlib import Path
import numpy as np
import pandas as pd

try:
    from config import ROBOTS_DIR, DEFAULT_ROBOT
except ImportError:
    from .config import ROBOTS_DIR, DEFAULT_ROBOT


def br_to_float(valor):
    if pd.isna(valor):
        return np.nan
    valor = str(valor).strip().replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return np.nan


def carregar_robo(nome_robo: str = DEFAULT_ROBOT) -> pd.DataFrame:
    nome_arquivo = nome_robo if nome_robo.lower().endswith(".csv") else f"{nome_robo}.csv"
    caminho = ROBOTS_DIR / nome_arquivo

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo do robô não encontrado: {caminho}")

    df = pd.read_csv(caminho, sep=";", encoding="latin1", skiprows=5)
    df.columns = [c.strip() for c in df.columns]

    required = ["Abertura", "Fechamento", "Res. Intervalo Bruto"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes no CSV do robô: {missing}")

    df["Abertura"] = pd.to_datetime(df["Abertura"], dayfirst=True, errors="coerce")
    df["Fechamento"] = pd.to_datetime(df["Fechamento"], dayfirst=True, errors="coerce")
    df["resultado"] = df["Res. Intervalo Bruto"].apply(br_to_float)

    df = df.dropna(subset=["Abertura", "resultado"]).copy()
    df["data"] = df["Abertura"].dt.date
    df["hora"] = df["Abertura"].dt.hour
    df["mes"] = df["Abertura"].dt.to_period("M").astype(str)

    if "Lado" in df.columns:
        df["lado"] = df["Lado"].astype(str).str.strip().str.lower()
    else:
        df["lado"] = "indefinido"

    df = df.sort_values("Abertura").reset_index(drop=True)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carrega CSV de operações do Profit.")
    parser.add_argument("--robot", default=DEFAULT_ROBOT, help="Nome do robô sem .csv")
    args = parser.parse_args()

    df = carregar_robo(args.robot)
    print("\nROBÔ CARREGADO COM SUCESSO")
    print(f"Robô: {args.robot}")
    print(f"Trades: {len(df)}")
    print(f"Resultado líquido: R$ {df['resultado'].sum():,.2f}")
    print("\nColunas:")
    print(df.columns)
