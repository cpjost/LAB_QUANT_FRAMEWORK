import argparse
import numpy as np
import pandas as pd

try:
    from config import DEFAULT_ROBOT, DEFAULT_MARKET_NAME, market_output_dir, robot_output_dirs
    from robot_loader import carregar_robo
except ImportError:
    from .config import DEFAULT_ROBOT, DEFAULT_MARKET_NAME, market_output_dir, robot_output_dirs
    from .robot_loader import carregar_robo


def resumo(df, nome):
    if df.empty:
        return {"cenario": nome, "trades": 0, "lucro_liquido": 0, "media_trade": 0, "winrate": 0, "profit_factor": np.nan}
    ganhos = df.loc[df["resultado"] > 0, "resultado"].sum()
    perdas = df.loc[df["resultado"] < 0, "resultado"].sum()
    return {
        "cenario": nome,
        "trades": len(df),
        "lucro_liquido": df["resultado"].sum(),
        "media_trade": df["resultado"].mean(),
        "winrate": (df["resultado"] > 0).mean() * 100,
        "ganhos": ganhos,
        "perdas": perdas,
        "profit_factor": ganhos / abs(perdas) if perdas != 0 else np.nan,
    }


def rodar_cruzamento(robot_name=DEFAULT_ROBOT, market_name=DEFAULT_MARKET_NAME):
    dirs = robot_output_dirs(robot_name)
    outdir = dirs["regime"]
    regime_path = market_output_dir(market_name) / "base_regime.csv"
    if not regime_path.exists():
        raise FileNotFoundError(f"Base de regime não encontrada. Rode primeiro regime_engine.py. Caminho: {regime_path}")

    trades = carregar_robo(robot_name).sort_values("Abertura")
    regime = pd.read_csv(regime_path, sep=";", decimal=",")
    regime["datetime"] = pd.to_datetime(regime["datetime"], errors="coerce")
    regime = regime.dropna(subset=["datetime"]).sort_values("datetime")

    base = pd.merge_asof(
        trades,
        regime[["datetime", "regime", "ema27", "ema55", "slope_ema27", "delta_slope", "dist_emas", "delta_dist", "atr14", "delta_atr"]],
        left_on="Abertura",
        right_on="datetime",
        direction="backward",
    )

    resumo_regime = base.groupby("regime").agg(
        trades=("resultado", "count"),
        lucro_liquido=("resultado", "sum"),
        media_trade=("resultado", "mean"),
        winrate=("resultado", lambda x: (x > 0).mean() * 100),
        ganhos=("resultado", lambda x: x[x > 0].sum()),
        perdas=("resultado", lambda x: x[x < 0].sum()),
    ).reset_index()
    resumo_regime["profit_factor"] = np.where(resumo_regime["perdas"] != 0, resumo_regime["ganhos"] / resumo_regime["perdas"].abs(), np.nan)
    resumo_regime = resumo_regime.sort_values("lucro_liquido", ascending=False)

    resumo_lado = pd.DataFrame([resumo(base[base["lado"] == "c"], "compras"), resumo(base[base["lado"] == "v"], "vendas")])

    resumo_regime_lado = base.groupby(["regime", "lado"]).agg(
        trades=("resultado", "count"),
        lucro_liquido=("resultado", "sum"),
        media_trade=("resultado", "mean"),
        winrate=("resultado", lambda x: (x > 0).mean() * 100),
        ganhos=("resultado", lambda x: x[x > 0].sum()),
        perdas=("resultado", lambda x: x[x < 0].sum()),
    ).reset_index()
    resumo_regime_lado["profit_factor"] = np.where(resumo_regime_lado["perdas"] != 0, resumo_regime_lado["ganhos"] / resumo_regime_lado["perdas"].abs(), np.nan)

    base.to_csv(outdir / "trades_com_regime.csv", sep=";", decimal=",", index=False)
    resumo_regime.to_csv(outdir / "resumo_resultado_por_regime.csv", sep=";", decimal=",", index=False)
    resumo_lado.to_csv(outdir / "resumo_compras_vs_vendas.csv", sep=";", decimal=",", index=False)
    resumo_regime_lado.to_csv(outdir / "resumo_regime_por_lado.csv", sep=";", decimal=",", index=False)

    print("\nRESULTADO POR REGIME")
    print(resumo_regime)
    print("\nCOMPRAS VS VENDAS")
    print(resumo_lado)
    print(f"\nArquivos salvos em: {outdir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", default=DEFAULT_ROBOT)
    parser.add_argument("--market-name", default=DEFAULT_MARKET_NAME)
    args = parser.parse_args()
    rodar_cruzamento(args.robot, args.market_name)
