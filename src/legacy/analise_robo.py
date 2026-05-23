import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# CAMINHOS
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "Robo_Jost_NEW.csv"

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# CONFIGURAÇÕES
# =========================

HORA_INICIO = 11
HORA_FIM = 16

# =========================
# FUNÇÕES
# =========================

def br_to_float(valor):
    if pd.isna(valor):
        return np.nan

    valor = str(valor).strip()
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    try:
        return float(valor)
    except:
        return np.nan


def calcular_metricas(df_base, nome="ROBÔ"):
    df_calc = df_base.copy()

    df_calc["equity"] = df_calc["resultado"].cumsum()
    df_calc["max_equity"] = df_calc["equity"].cummax()
    df_calc["drawdown"] = df_calc["equity"] - df_calc["max_equity"]

    total_trades = len(df_calc)
    lucro_liquido = df_calc["resultado"].sum()

    ganhos = df_calc[df_calc["resultado"] > 0]["resultado"].sum()
    perdas = df_calc[df_calc["resultado"] < 0]["resultado"].sum()

    profit_factor = ganhos / abs(perdas) if perdas != 0 else np.nan
    winrate = (df_calc["resultado"] > 0).mean() * 100 if total_trades > 0 else 0
    drawdown_max = df_calc["drawdown"].min() if total_trades > 0 else 0
    media_trade = df_calc["resultado"].mean() if total_trades > 0 else 0

    loss_flag = df_calc["resultado"] < 0
    streak = 0
    max_streak = 0

    for loss in loss_flag:
        if loss:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    print("\n==============================")
    print(nome)
    print("==============================")
    print(f"Total trades: {total_trades}")
    print(f"Lucro líquido: R$ {lucro_liquido:,.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Winrate: {winrate:.2f}%")
    print(f"Drawdown Máx: R$ {drawdown_max:,.2f}")
    print(f"Média por trade: R$ {media_trade:,.2f}")
    print(f"Máx losses seguidos: {max_streak}")

    return df_calc


def salvar_grafico(df_base, nome_arquivo, titulo):
    if df_base.empty:
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df_base["Abertura"], df_base["equity"])
    plt.title(titulo)
    plt.xlabel("Data")
    plt.ylabel("Resultado Acumulado")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / nome_arquivo)
    plt.close()


# =========================
# LEITURA DO CSV
# =========================

df = pd.read_csv(
    DATA_PATH,
    sep=";",
    encoding="latin1",
    skiprows=5
)

print("\nCOLUNAS ENCONTRADAS:")
print(df.columns)

# =========================
# TRATAMENTO DAS DATAS
# =========================

df["Abertura"] = pd.to_datetime(
    df["Abertura"],
    dayfirst=True,
    errors="coerce"
)

df["Fechamento"] = pd.to_datetime(
    df["Fechamento"],
    dayfirst=True,
    errors="coerce"
)

# =========================
# RESULTADO FINANCEIRO
# =========================

col_resultado = None

for col in df.columns:
    if "Res. Intervalo Bruto" in col:
        col_resultado = col
        break

if col_resultado is None:
    for col in df.columns:
        if "Res." in col or "Resultado" in col:
            col_resultado = col
            break

print(f"\nColuna resultado encontrada: {col_resultado}")

df["resultado"] = df[col_resultado].apply(br_to_float)

# =========================
# LIMPEZA
# =========================

df = df.dropna(subset=["Abertura", "resultado"]).copy()

df["data"] = df["Abertura"].dt.date
df["hora"] = df["Abertura"].dt.hour

# =========================
# ROBÔ ORIGINAL
# =========================

df_original = calcular_metricas(
    df,
    nome="ROBÔ ORIGINAL"
)

salvar_grafico(
    df_original,
    "curva_capital_original.png",
    "Curva Capital - Robô Original"
)

# Drawdown original
plt.figure(figsize=(12, 6))
plt.plot(df_original["Abertura"], df_original["drawdown"])
plt.title("Drawdown - Robô Original")
plt.xlabel("Data")
plt.ylabel("Drawdown")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "drawdown_original.png")
plt.close()

# =========================
# RESULTADO POR DIA
# =========================

resultado_dia = df.groupby("data")["resultado"].sum()

resultado_dia.to_csv(
    OUTPUT_DIR / "resultado_por_dia.csv",
    sep=";",
    decimal=","
)

# =========================
# RESULTADO POR HORA
# =========================

resultado_hora = df.groupby("hora")["resultado"].sum()

resultado_hora.to_csv(
    OUTPUT_DIR / "resultado_por_hora.csv",
    sep=";",
    decimal=","
)

print("\nRESULTADO POR HORA:")
print(resultado_hora)

# =========================
# FILTRO HORÁRIO
# =========================

df_horario = df[
    (df["hora"] >= HORA_INICIO) &
    (df["hora"] <= HORA_FIM)
].copy()

df_horario = calcular_metricas(
    df_horario,
    nome=f"ROBÔ COM FILTRO HORÁRIO {HORA_INICIO}H ÀS {HORA_FIM}H"
)

salvar_grafico(
    df_horario,
    "curva_capital_filtro_horario.png",
    f"Curva Capital - Filtro Horário {HORA_INICIO}h às {HORA_FIM}h"
)

# Drawdown filtrado
plt.figure(figsize=(12, 6))
plt.plot(df_horario["Abertura"], df_horario["drawdown"])
plt.title(f"Drawdown - Filtro Horário {HORA_INICIO}h às {HORA_FIM}h")
plt.xlabel("Data")
plt.ylabel("Drawdown")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "drawdown_filtro_horario.png")
plt.close()

# =========================
# COMPARATIVO
# =========================

comparativo = pd.DataFrame({
    "cenario": ["Original", f"Filtro {HORA_INICIO}h-{HORA_FIM}h"],
    "lucro_liquido": [
        df_original["resultado"].sum(),
        df_horario["resultado"].sum()
    ],
    "total_trades": [
        len(df_original),
        len(df_horario)
    ],
    "drawdown_max": [
        df_original["drawdown"].min(),
        df_horario["drawdown"].min()
    ]
})

comparativo.to_csv(
    OUTPUT_DIR / "comparativo_original_vs_filtro_horario.csv",
    sep=";",
    decimal=",",
    index=False
)

print("\n==============================")
print("COMPARATIVO SALVO EM OUTPUTS")
print("==============================")
print(comparativo)

print("\nArquivos gerados na pasta outputs.")

# =========================
# TRAVA 3 LOSSES POR DIA
# =========================

MAX_LOSSES_DIA = 3

df_trava = df[
    (df["hora"] >= HORA_INICIO) &
    (df["hora"] <= HORA_FIM)
].copy()

# Ordenar
df_trava = df_trava.sort_values(
    by="Abertura"
).reset_index(drop=True)

# Controle
losses_dia = 0
dia_atual = None

operacoes_filtradas = []

for _, row in df_trava.iterrows():

    dia_trade = row["data"]

    # Novo dia
    if dia_trade != dia_atual:

        dia_atual = dia_trade
        losses_dia = 0

    # Se já bateu limite, ignora trade
    if losses_dia >= MAX_LOSSES_DIA:
        continue

    # Adiciona operação
    operacoes_filtradas.append(row)

    # Conta loss
    if row["resultado"] < 0:
        losses_dia += 1

# Novo dataframe
df_trava = pd.DataFrame(operacoes_filtradas)

# =========================
# MÉTRICAS
# =========================

df_trava = calcular_metricas(
    df_trava,
    nome="FILTRO HORÁRIO + TRAVA 3 LOSSES"
)

# =========================
# CURVA CAPITAL
# =========================

salvar_grafico(
    df_trava,
    "curva_filtro_horario_trava_3_losses.png",
    "Filtro Horário + Trava 3 Losses"
)

# =========================
# DRAWDOWN
# =========================

plt.figure(figsize=(12,6))

plt.plot(
    df_trava["Abertura"],
    df_trava["drawdown"]
)

plt.title(
    "Drawdown - Filtro Horário + Trava 3 Losses"
)

plt.xlabel("Data")

plt.ylabel("Drawdown")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR /
    "drawdown_filtro_trava_3_losses.png"
)

plt.close()

# =========================
# COMPARATIVO FINAL
# =========================

comparativo_final = pd.DataFrame({

    "cenario": [
        "Original",
        "Filtro Horário",
        "Filtro + Trava 3 Losses"
    ],

    "lucro_liquido": [

        df_original["resultado"].sum(),

        df_horario["resultado"].sum(),

        df_trava["resultado"].sum()
    ],

    "total_trades": [

        len(df_original),

        len(df_horario),

        len(df_trava)
    ],

    "drawdown_max": [

        df_original["drawdown"].min(),

        df_horario["drawdown"].min(),

        df_trava["drawdown"].min()
    ]
})

comparativo_final.to_csv(

    OUTPUT_DIR /
    "comparativo_final.csv",

    sep=";",
    decimal=",",
    index=False
)

print("\n==============================")
print("COMPARATIVO FINAL")
print("==============================")
print(comparativo_final)

# =========================
# FILTRO INCLINAÇÃO MÉDIA
# =========================

# Vamos usar o próprio resultado por trade
# como aproximação inicial do filtro de tendência.

# Aqui criaremos uma lógica simples:
# manter trades somente quando
# a curva recente estiver inclinada positivamente.

df_slope = df[
    (df["hora"] >= HORA_INICIO) &
    (df["hora"] <= HORA_FIM)
].copy()

df_slope = df_slope.reset_index(drop=True)

# Média móvel dos resultados
df_slope["media_curta"] = (
    df_slope["resultado"]
    .rolling(5)
    .mean()
)

# Inclinação
df_slope["slope"] = (
    df_slope["media_curta"] -
    df_slope["media_curta"].shift(5)
)

# Mantém apenas tendência positiva
df_slope = df_slope[
    df_slope["slope"] > 0
].copy()

# =========================
# MÉTRICAS
# =========================

df_slope = calcular_metricas(
    df_slope,
    nome="FILTRO HORÁRIO + SLOPE"
)

# =========================
# CURVA CAPITAL
# =========================

salvar_grafico(
    df_slope,
    "curva_filtro_slope.png",
    "Filtro Horário + Slope"
)

# =========================
# DRAWDOWN
# =========================

plt.figure(figsize=(12,6))

plt.plot(
    df_slope["Abertura"],
    df_slope["drawdown"]
)

plt.title(
    "Drawdown - Filtro Horário + Slope"
)

plt.xlabel("Data")

plt.ylabel("Drawdown")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR /
    "drawdown_filtro_slope.png"
)

plt.close()

# =========================
# COMPARATIVO SLOPE
# =========================

comparativo_slope = pd.DataFrame({

    "cenario": [
        "Original",
        "Filtro Horário",
        "Filtro + Slope"
    ],

    "lucro_liquido": [

        df_original["resultado"].sum(),

        df_horario["resultado"].sum(),

        df_slope["resultado"].sum()
    ],

    "total_trades": [

        len(df_original),

        len(df_horario),

        len(df_slope)
    ],

    "drawdown_max": [

        df_original["drawdown"].min(),

        df_horario["drawdown"].min(),

        df_slope["drawdown"].min()
    ]
})

print("\n==============================")
print("COMPARATIVO SLOPE")
print("==============================")
print(comparativo_slope)

# =========================
# FILTRO DISTÂNCIA ENTRE MÉDIAS
# =========================

df_dist = df[
    (df["hora"] >= HORA_INICIO) &
    (df["hora"] <= HORA_FIM)
].copy()

df_dist = df_dist.reset_index(drop=True)

# Proxy de expansão usando resultado recente
df_dist["media_rapida"] = (
    df_dist["resultado"]
    .rolling(3)
    .mean()
)

df_dist["media_lenta"] = (
    df_dist["resultado"]
    .rolling(10)
    .mean()
)

# Distância
df_dist["distancia"] = abs(
    df_dist["media_rapida"] -
    df_dist["media_lenta"]
)

# Threshold
LIMIAR_DISTANCIA = 400

# Filtro
df_dist = df_dist[
    df_dist["distancia"] > LIMIAR_DISTANCIA
].copy()

# =========================
# MÉTRICAS
# =========================

df_dist = calcular_metricas(
    df_dist,
    nome="FILTRO HORÁRIO + DISTÂNCIA"
)

# =========================
# CURVA CAPITAL
# =========================

salvar_grafico(
    df_dist,
    "curva_filtro_distancia.png",
    "Filtro Horário + Distância"
)

# =========================
# DRAWDOWN
# =========================

plt.figure(figsize=(12,6))

plt.plot(
    df_dist["Abertura"],
    df_dist["drawdown"]
)

plt.title(
    "Drawdown - Filtro Distância"
)

plt.xlabel("Data")

plt.ylabel("Drawdown")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR /
    "drawdown_filtro_distancia.png"
)

plt.close()

# =========================
# COMPARATIVO DISTÂNCIA
# =========================

comparativo_dist = pd.DataFrame({

    "cenario": [
        "Original",
        "Filtro Horário",
        "Filtro + Slope",
        "Filtro + Distância"
    ],

    "lucro_liquido": [

        df_original["resultado"].sum(),

        df_horario["resultado"].sum(),

        df_slope["resultado"].sum(),

        df_dist["resultado"].sum()
    ],

    "total_trades": [

        len(df_original),

        len(df_horario),

        len(df_slope),

        len(df_dist)
    ],

    "drawdown_max": [

        df_original["drawdown"].min(),

        df_horario["drawdown"].min(),

        df_slope["drawdown"].min(),

        df_dist["drawdown"].min()
    ]
})

print("\n==============================")
print("COMPARATIVO DISTÂNCIA")
print("==============================")
print(comparativo_dist)

# =========================
# WALK FORWARD
# =========================

print("\n==============================")
print("WALK FORWARD")
print("==============================")

df["mes"] = df["Abertura"].dt.month

# Março = treino
df_marco = df[df["mes"] == 3].copy()

# Abril = validação
df_abril = df[df["mes"] == 4].copy()

# Maio = out-of-sample
df_maio = df[df["mes"] == 5].copy()

calcular_metricas(
    df_marco,
    nome="TREINO - MARÇO"
)

calcular_metricas(
    df_abril,
    nome="VALIDAÇÃO - ABRIL"
)

calcular_metricas(
    df_maio,
    nome="OUT OF SAMPLE - MAIO"
)

# =========================
# MONTE CARLO
# =========================

print("\n==============================")
print("MONTE CARLO")
print("==============================")

# Vamos usar o melhor cenário:
# filtro horário + slope

resultados = df_slope["resultado"].values

capital_inicial = 0

num_simulacoes = 1000

equities_finais = []
drawdowns = []

for i in range(num_simulacoes):

    trades_randomizados = np.random.permutation(resultados)

    equity = capital_inicial

    curva = []

    for trade in trades_randomizados:

        equity += trade

        curva.append(equity)

    curva = np.array(curva)

    max_equity = np.maximum.accumulate(curva)

    dd = curva - max_equity

    drawdown_max = dd.min()

    equities_finais.append(curva[-1])

    drawdowns.append(drawdown_max)

# =========================
# RESULTADOS MONTE CARLO
# =========================

equities_finais = np.array(equities_finais)
drawdowns = np.array(drawdowns)

print(f"Simulações: {num_simulacoes}")

print(f"\nLucro médio final: R$ {equities_finais.mean():,.2f}")

print(f"Pior equity final: R$ {equities_finais.min():,.2f}")

print(f"Melhor equity final: R$ {equities_finais.max():,.2f}")

print(f"\nDrawdown médio: R$ {drawdowns.mean():,.2f}")

print(f"Pior drawdown: R$ {drawdowns.min():,.2f}")

print(f"Melhor drawdown: R$ {drawdowns.max():,.2f}")

# =========================
# HISTOGRAMA EQUITY FINAL
# =========================

plt.figure(figsize=(12,6))

plt.hist(
    equities_finais,
    bins=30
)

plt.title("Monte Carlo - Equity Final")

plt.xlabel("Resultado Final")

plt.ylabel("Frequência")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR /
    "monte_carlo_equity.png"
)

plt.close()

# =========================
# HISTOGRAMA DRAWDOWN
# =========================

plt.figure(figsize=(12,6))

plt.hist(
    drawdowns,
    bins=30
)

plt.title("Monte Carlo - Drawdown")

plt.xlabel("Drawdown")

plt.ylabel("Frequência")

plt.grid(True)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR /
    "monte_carlo_drawdown.png"
)

plt.close()

print("\nMonte Carlo finalizado.")