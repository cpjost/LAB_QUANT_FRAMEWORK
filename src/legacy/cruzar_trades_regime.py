import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

TRADES_PATH = BASE_DIR / "data" / "Robo_Jost_NEW.csv"
REGIME_PATH = BASE_DIR / "outputs" / "base_regime_winfut_5min.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def br_to_float(valor):
    if pd.isna(valor):
        return np.nan

    valor = str(valor).strip()
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    try:
        return float(valor)
    except ValueError:
        return np.nan


def calcular_resumo(df_base, nome):
    if df_base.empty:
        print(f"\n{nome}: sem trades")
        return None

    trades = len(df_base)
    lucro = df_base["resultado"].sum()
    media = df_base["resultado"].mean()
    winrate = (df_base["resultado"] > 0).mean() * 100

    ganhos = df_base[df_base["resultado"] > 0]["resultado"].sum()
    perdas = df_base[df_base["resultado"] < 0]["resultado"].sum()

    pf = ganhos / abs(perdas) if perdas != 0 else np.nan

    print(f"\n{nome}")
    print(f"Trades: {trades}")
    print(f"Lucro líquido: R$ {lucro:,.2f}")
    print(f"Média por trade: R$ {media:,.2f}")
    print(f"Winrate: {winrate:.2f}%")
    print(f"Profit Factor: {pf:.2f}")

    return {
        "cenario": nome,
        "trades": trades,
        "lucro_liquido": lucro,
        "media_trade": media,
        "winrate": winrate,
        "profit_factor": pf,
        "ganhos": ganhos,
        "perdas": perdas
    }


# =========================
# LER TRADES
# =========================

trades = pd.read_csv(
    TRADES_PATH,
    sep=";",
    encoding="latin1",
    skiprows=5
)

trades.columns = [c.strip() for c in trades.columns]

print("\nCOLUNAS TRADES:")
print(trades.columns)

trades["Abertura"] = pd.to_datetime(
    trades["Abertura"],
    dayfirst=True,
    errors="coerce"
)

col_resultado = "Res. Intervalo Bruto"

if col_resultado not in trades.columns:
    raise ValueError(f"Coluna não encontrada: {col_resultado}")

trades["resultado"] = trades[col_resultado].apply(br_to_float)

if "Lado" not in trades.columns:
    raise ValueError("Coluna 'Lado' não encontrada no arquivo de trades.")

trades = trades.dropna(
    subset=["Abertura", "resultado"]
).copy()

trades = trades.sort_values("Abertura").reset_index(drop=True)

# =========================
# LER REGIME
# =========================

regime = pd.read_csv(
    REGIME_PATH,
    sep=";",
    decimal=","
)

regime.columns = [c.strip() for c in regime.columns]

regime["datetime"] = pd.to_datetime(
    regime["datetime"],
    errors="coerce"
)

regime = regime.dropna(subset=["datetime"]).copy()
regime = regime.sort_values("datetime").reset_index(drop=True)

# =========================
# CRUZAR TRADES COM REGIME
# =========================

base = pd.merge_asof(
    trades,
    regime[
        [
            "datetime",
            "regime",
            "ema27",
            "ema55",
            "slope_ema27",
            "dist_emas",
            "atr14"
        ]
    ],
    left_on="Abertura",
    right_on="datetime",
    direction="backward"
)

# =========================
# RESULTADO POR REGIME
# =========================

resumo_regime = base.groupby("regime").agg(
    trades=("resultado", "count"),
    lucro_liquido=("resultado", "sum"),
    media_trade=("resultado", "mean"),
    winrate=("resultado", lambda x: (x > 0).mean() * 100),
    ganhos=("resultado", lambda x: x[x > 0].sum()),
    perdas=("resultado", lambda x: x[x < 0].sum())
).reset_index()

resumo_regime["profit_factor"] = np.where(
    resumo_regime["perdas"] != 0,
    resumo_regime["ganhos"] / resumo_regime["perdas"].abs(),
    np.nan
)

resumo_regime = resumo_regime.sort_values(
    "lucro_liquido",
    ascending=False
)

print("\n==============================")
print("RESULTADO POR REGIME")
print("==============================")
print(resumo_regime)

# =========================
# COMPRAS VS VENDAS
# =========================

print("\n==============================")
print("ANÁLISE COMPRAS VS VENDAS")
print("==============================")

base["lado"] = (
    base["Lado"]
    .astype(str)
    .str.strip()
    .str.lower()
)

print("\nVALORES ENCONTRADOS NA COLUNA LADO:")
print(base["lado"].value_counts())

compras = base[
    base["lado"].str.contains("compra|comprado|buy|long|c", na=False)
].copy()

vendas = base[
    base["lado"].str.contains("venda|vendido|sell|short|v", na=False)
].copy()

resumos = []

resumo_compra = calcular_resumo(compras, "COMPRAS")
resumo_venda = calcular_resumo(vendas, "VENDAS")

if resumo_compra:
    resumos.append(resumo_compra)

if resumo_venda:
    resumos.append(resumo_venda)

resumo_lado = pd.DataFrame(resumos)

# =========================
# RESULTADO POR REGIME E LADO
# =========================

resumo_regime_lado = base.groupby(["regime", "lado"]).agg(
    trades=("resultado", "count"),
    lucro_liquido=("resultado", "sum"),
    media_trade=("resultado", "mean"),
    winrate=("resultado", lambda x: (x > 0).mean() * 100),
    ganhos=("resultado", lambda x: x[x > 0].sum()),
    perdas=("resultado", lambda x: x[x < 0].sum())
).reset_index()

resumo_regime_lado["profit_factor"] = np.where(
    resumo_regime_lado["perdas"] != 0,
    resumo_regime_lado["ganhos"] / resumo_regime_lado["perdas"].abs(),
    np.nan
)

print("\n==============================")
print("RESULTADO POR REGIME E LADO")
print("==============================")
print(resumo_regime_lado)

# =========================
# SALVAR ARQUIVOS
# =========================

base.to_csv(
    OUTPUT_DIR / "trades_com_regime.csv",
    sep=";",
    decimal=",",
    index=False
)

resumo_regime.to_csv(
    OUTPUT_DIR / "resumo_resultado_por_regime.csv",
    sep=";",
    decimal=",",
    index=False
)

resumo_lado.to_csv(
    OUTPUT_DIR / "resumo_compras_vs_vendas.csv",
    sep=";",
    decimal=",",
    index=False
)

resumo_regime_lado.to_csv(
    OUTPUT_DIR / "resumo_regime_por_lado.csv",
    sep=";",
    decimal=",",
    index=False
)

print("\nArquivos salvos em outputs:")
print("- trades_com_regime.csv")
print("- resumo_resultado_por_regime.csv")
print("- resumo_compras_vs_vendas.csv")
print("- resumo_regime_por_lado.csv")

# =========================
# FILTRO FINAL DE REGIME
# =========================

print("\n==============================")
print("FILTRO FINAL DE REGIME")
print("==============================")

base_filtrada = base.copy()

# COMPRAS
compras_ok = base_filtrada[
    (
        (base_filtrada["lado"] == "c") &
        (
            (base_filtrada["regime"] == "tendencia_alta") |
            (base_filtrada["regime"] == "neutro")
        )
    )
].copy()

# VENDAS
vendas_ok = base_filtrada[
    (
        (base_filtrada["lado"] == "v") &
        (
            (base_filtrada["regime"] == "tendencia_baixa") |
            (base_filtrada["regime"] == "neutro")
        )
    )
].copy()

# JUNTAR
final = pd.concat(
    [compras_ok, vendas_ok]
).sort_values("Abertura")

# =========================
# MÉTRICAS
# =========================

trades = len(final)

lucro = final["resultado"].sum()

media_trade = final["resultado"].mean()

winrate = (
    (final["resultado"] > 0).mean()
) * 100

ganhos = (
    final[
        final["resultado"] > 0
    ]["resultado"].sum()
)

perdas = (
    final[
        final["resultado"] < 0
    ]["resultado"].sum()
)

pf = ganhos / abs(perdas)

# EQUITY
final["equity"] = (
    final["resultado"].cumsum()
)

final["max_equity"] = (
    final["equity"].cummax()
)

final["drawdown"] = (
    final["equity"] -
    final["max_equity"]
)

dd = final["drawdown"].min()

# =========================
# RESULTADOS
# =========================

print(f"Trades: {trades}")

print(f"Lucro: R$ {lucro:,.2f}")

print(f"PF: {pf:.2f}")

print(f"Winrate: {winrate:.2f}%")

print(f"Média/trade: R$ {media_trade:,.2f}")

print(f"Drawdown Máx: R$ {dd:,.2f}")

# =========================
# SALVAR
# =========================

final.to_csv(
    OUTPUT_DIR /
    "resultado_regime_filter_final.csv",

    sep=";",
    decimal=",",
    index=False
)

print("\nArquivo salvo:")
print("resultado_regime_filter_final.csv")

# =========================
# FILTRO SLOPE REAL
# =========================

print("\n==============================")
print("FILTRO SLOPE REAL")
print("==============================")

SLOPE_MIN = 15

base_real = base.copy()

# =========================
# COMPRAS
# =========================

compras_real = base_real[
    (
        (base_real["lado"] == "c") &
        (base_real["ema27"] > base_real["ema55"]) &
        (base_real["slope_ema27"] > SLOPE_MIN)
    )
].copy()

# =========================
# VENDAS
# =========================

vendas_real = base_real[
    (
        (base_real["lado"] == "v") &
        (base_real["ema27"] < base_real["ema55"]) &
        (base_real["slope_ema27"] < -SLOPE_MIN)
    )
].copy()

# =========================
# FINAL
# =========================

final_real = pd.concat(
    [compras_real, vendas_real]
).sort_values("Abertura")

# =========================
# MÉTRICAS
# =========================

trades = len(final_real)

lucro = final_real["resultado"].sum()

media_trade = final_real["resultado"].mean()

winrate = (
    (final_real["resultado"] > 0).mean()
) * 100

ganhos = (
    final_real[
        final_real["resultado"] > 0
    ]["resultado"].sum()
)

perdas = (
    final_real[
        final_real["resultado"] < 0
    ]["resultado"].sum()
)

pf = ganhos / abs(perdas)

# =========================
# EQUITY
# =========================

final_real["equity"] = (
    final_real["resultado"].cumsum()
)

final_real["max_equity"] = (
    final_real["equity"].cummax()
)

final_real["drawdown"] = (
    final_real["equity"] -
    final_real["max_equity"]
)

dd = final_real["drawdown"].min()

# =========================
# RESULTADOS
# =========================

print(f"Trades: {trades}")

print(f"Lucro: R$ {lucro:,.2f}")

print(f"PF: {pf:.2f}")

print(f"Winrate: {winrate:.2f}%")

print(f"Média/trade: R$ {media_trade:,.2f}")

print(f"Drawdown Máx: R$ {dd:,.2f}")

# =========================
# SALVAR
# =========================

final_real.to_csv(
    OUTPUT_DIR /
    "resultado_slope_real.csv",

    sep=";",
    decimal=",",
    index=False
)

print("\nArquivo salvo:")
print("resultado_slope_real.csv")