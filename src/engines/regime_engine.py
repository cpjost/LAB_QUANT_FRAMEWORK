import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from config import DATA_DIR, DEFAULT_MARKET_FILE, DEFAULT_MARKET_NAME, market_output_dir
except ImportError:
    from .config import DATA_DIR, DEFAULT_MARKET_FILE, DEFAULT_MARKET_NAME, market_output_dir


def br_to_float(valor):
    if pd.isna(valor):
        return np.nan
    valor = str(valor).strip().replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return np.nan


def detectar_colunas(df):
    cols = {"data": None, "open": None, "high": None, "low": None, "close": None, "volume": None}
    for col in df.columns:
        c = col.lower()
        if "data" in c or "date" in c or "tempo" in c:
            cols["data"] = col
        if "abertura" in c or "open" in c:
            cols["open"] = col
        if "máximo" in c or "maximo" in c or "high" in c:
            cols["high"] = col
        if "mínimo" in c or "minimo" in c or "low" in c:
            cols["low"] = col
        if "fechamento" in c or "close" in c:
            cols["close"] = col
        if "volume" in c or "quantidade" in c:
            cols["volume"] = col
    return cols


def rodar_regime(market_file=DEFAULT_MARKET_FILE, market_name=DEFAULT_MARKET_NAME):
    outdir = market_output_dir(market_name)
    caminho = DATA_DIR / market_file
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de mercado não encontrado: {caminho}")

    df = pd.read_csv(caminho, sep=";", encoding="latin1")
    df.columns = [c.strip() for c in df.columns]
    cols = detectar_colunas(df)
    print("\nMAPEAMENTO:")
    print(cols)

    df["datetime"] = pd.to_datetime(df[cols["data"]], dayfirst=True, errors="coerce")
    df["open"] = df[cols["open"]].apply(br_to_float)
    df["high"] = df[cols["high"]].apply(br_to_float)
    df["low"] = df[cols["low"]].apply(br_to_float)
    df["close"] = df[cols["close"]].apply(br_to_float)
    df["volume"] = df[cols["volume"]].apply(br_to_float) if cols["volume"] else np.nan
    df = df.dropna(subset=["datetime", "open", "high", "low", "close"]).copy()
    df = df.sort_values("datetime").reset_index(drop=True)

    df["ema27"] = df["close"].ewm(span=27, adjust=False).mean()
    df["ema55"] = df["close"].ewm(span=55, adjust=False).mean()
    df["slope_ema27"] = df["ema27"] - df["ema27"].shift(5)
    df["delta_slope"] = df["slope_ema27"] - df["slope_ema27"].shift(5)
    df["dist_emas"] = (df["ema27"] - df["ema55"]).abs()
    df["delta_dist"] = df["dist_emas"] - df["dist_emas"].shift(5)
    df["range"] = df["high"] - df["low"]
    df["atr14"] = df["range"].rolling(14).mean()
    df["atr_media_50"] = df["atr14"].rolling(50).mean()
    df["delta_atr"] = df["atr14"] - df["atr14"].shift(5)
    df["volatilidade_alta"] = df["atr14"] > df["atr_media_50"]

    df["regime"] = "neutro"
    df.loc[(df["close"] > df["ema55"]) & (df["ema27"] > df["ema55"]) & (df["slope_ema27"] > 0) & (df["volatilidade_alta"]), "regime"] = "tendencia_alta"
    df.loc[(df["close"] < df["ema55"]) & (df["ema27"] < df["ema55"]) & (df["slope_ema27"] < 0) & (df["volatilidade_alta"]), "regime"] = "tendencia_baixa"
    df.loc[(df["dist_emas"] < df["dist_emas"].rolling(100).median()) & (df["atr14"] < df["atr_media_50"]), "regime"] = "lateral_compressao"

    print("\nRESUMO REGIMES:")
    print(df["regime"].value_counts())
    df.to_csv(outdir / "base_regime.csv", sep=";", decimal=",", index=False)

    plt.figure(figsize=(14,7))
    plt.plot(df["datetime"], df["close"], label="Close")
    plt.plot(df["datetime"], df["ema27"], label="EMA27")
    plt.plot(df["datetime"], df["ema55"], label="EMA55")
    plt.title(f"{market_name} — Close + EMAs")
    plt.legend(); plt.grid(True); plt.tight_layout()
    plt.savefig(outdir / "close_emas.png")
    plt.close()

    plt.figure(figsize=(14,6))
    plt.plot(df["datetime"], df["atr14"], label="ATR14")
    plt.plot(df["datetime"], df["atr_media_50"], label="ATR média 50")
    plt.title(f"{market_name} — ATR")
    plt.legend(); plt.grid(True); plt.tight_layout()
    plt.savefig(outdir / "atr.png")
    plt.close()

    print("\nEngine de regime finalizada.")
    print(f"Arquivos salvos em: {outdir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--market-file", default=DEFAULT_MARKET_FILE)
    parser.add_argument("--market-name", default=DEFAULT_MARKET_NAME)
    args = parser.parse_args()
    rodar_regime(args.market_file, args.market_name)
