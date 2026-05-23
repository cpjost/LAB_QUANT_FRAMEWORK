import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from config import DEFAULT_ROBOT, robot_output_dirs
    from robot_loader import carregar_robo
except ImportError:
    from .config import DEFAULT_ROBOT, robot_output_dirs
    from .robot_loader import carregar_robo


def calcular_metricas(df: pd.DataFrame) -> dict:
    base = df.copy()
    base["equity"] = base["resultado"].cumsum()
    base["max_equity"] = base["equity"].cummax()
    base["drawdown"] = base["equity"] - base["max_equity"]

    trades = len(base)
    lucro = base["resultado"].sum()
    ganhos = base.loc[base["resultado"] > 0, "resultado"].sum()
    perdas = base.loc[base["resultado"] < 0, "resultado"].sum()
    pf = ganhos / abs(perdas) if perdas != 0 else np.nan
    winrate = (base["resultado"] > 0).mean() * 100 if trades else 0
    media_trade = base["resultado"].mean() if trades else 0
    dd = base["drawdown"].min() if trades else 0

    streak = 0
    max_streak = 0
    for loss in (base["resultado"] < 0):
        if loss:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    return {
        "trades": trades,
        "lucro_liquido": lucro,
        "ganhos": ganhos,
        "perdas": perdas,
        "profit_factor": pf,
        "winrate": winrate,
        "media_trade": media_trade,
        "drawdown_max": dd,
        "max_losses_seguidos": max_streak,
        "df": base,
    }


def rodar_metrics(robot_name: str = DEFAULT_ROBOT):
    dirs = robot_output_dirs(robot_name)
    metrics_dir = dirs["metrics"]
    charts_dir = dirs["charts"]

    df = carregar_robo(robot_name)
    m = calcular_metricas(df)
    base = m["df"]

    print("\n==============================")
    print(f"METRICS ENGINE V1 — {robot_name}")
    print("==============================")
    print(f"Trades: {m['trades']}")
    print(f"Lucro Líquido: R$ {m['lucro_liquido']:,.2f}")
    print(f"Profit Factor: {m['profit_factor']:.2f}")
    print(f"Winrate: {m['winrate']:.2f}%")
    print(f"Média por Trade: R$ {m['media_trade']:,.2f}")
    print(f"Drawdown Máx: R$ {m['drawdown_max']:,.2f}")
    print(f"Máx Losses Seguidos: {m['max_losses_seguidos']}")

    resumo = pd.DataFrame([{k:v for k,v in m.items() if k != "df"}])
    resumo.to_csv(metrics_dir / "resumo_metricas.csv", sep=";", decimal=",", index=False)
    base.groupby("mes")["resultado"].sum().reset_index().to_csv(metrics_dir / "resultado_mensal.csv", sep=";", decimal=",", index=False)
    base.groupby("data")["resultado"].sum().reset_index().to_csv(metrics_dir / "resultado_diario.csv", sep=";", decimal=",", index=False)
    base.groupby("hora")["resultado"].sum().reset_index().to_csv(metrics_dir / "resultado_por_hora.csv", sep=";", decimal=",", index=False)

    plt.figure(figsize=(14, 6))
    plt.plot(base["Abertura"], base["equity"])
    plt.title(f"Curva de Capital — {robot_name}")
    plt.xlabel("Data")
    plt.ylabel("Equity")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(charts_dir / "curva_capital.png")
    plt.close()

    plt.figure(figsize=(14, 6))
    plt.plot(base["Abertura"], base["drawdown"])
    plt.title(f"Drawdown — {robot_name}")
    plt.xlabel("Data")
    plt.ylabel("Drawdown")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(charts_dir / "drawdown.png")
    plt.close()

    print("\nArquivos salvos em:")
    print(f"- {metrics_dir}")
    print(f"- {charts_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calcula métricas de um robô.")
    parser.add_argument("--robot", default=DEFAULT_ROBOT, help="Nome do robô sem .csv")
    args = parser.parse_args()
    rodar_metrics(args.robot)
