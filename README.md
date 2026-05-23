# LAB_QUANT_FRAMEWORK

Framework quantitativo para analisar robôs exportados do Profit.

## Estrutura

```text
LAB_QUANT_FRAMEWORK/
├── data/                 # Dados de mercado OHLCV
├── robots/               # CSVs de operações dos robôs
├── outputs/              # Resultados organizados por robô e por mercado
├── features/             # Futuro dataset de features
├── reports/              # Relatórios finais
├── monte_carlo/          # Módulos/estudos de Monte Carlo
├── walk_forward/         # Módulos/estudos de Walk Forward
├── portfolio_engine/     # Futuro motor de portfólio
└── src/                  # Código-fonte principal
```

## Como adicionar um novo robô

1. Exporte as operações do Profit em CSV.
2. Coloque o arquivo em `robots/`.
3. O nome do arquivo deve ser o nome do robô, por exemplo:

```text
robots/Robo_Jost_NEW.csv
```

## Rodar análise básica

```bash
python src/metrics_engine.py --robot Robo_Jost_NEW
```

Saída:

```text
outputs/Robo_Jost_NEW/metrics/
outputs/Robo_Jost_NEW/charts/
```

## Rodar engine de regime do mercado

```bash
python src/regime_engine.py --market-file WINFUT_F_0_5min.csv --market-name WINFUT_5min
```

Saída:

```text
outputs/market/WINFUT_5min/
```

## Cruzar trades com regime

Antes, rode a engine de regime.

```bash
python src/regime_cross_engine.py --robot Robo_Jost_NEW --market-name WINFUT_5min
```

Saída:

```text
outputs/Robo_Jost_NEW/regime/
```

## Dependências

```bash
pip install -r requirements.txt
```

## Próximos módulos

- `walk_forward_engine.py`
- `monte_carlo_engine.py`
- `feature_engine.py`
- `score_engine.py`
- `portfolio_engine.py`

## Observação

O objetivo deste projeto não é apenas testar um robô isolado.

O objetivo é construir uma infraestrutura quantitativa reutilizável para validar vários robôs com:

- métricas
- drawdown
- walk forward
- Monte Carlo
- regime de mercado
- análise por lado
- análise por horário
- feature engineering
- score engine
- portfólio de estratégias
