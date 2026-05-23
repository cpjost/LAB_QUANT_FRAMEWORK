# LAB_QUANT_FRAMEWORK

Framework quantitativo para análise, validação e pesquisa de robôs de trading exportados do Profit.

---

# Objetivo

O objetivo deste projeto é construir um laboratório quantitativo modular para:

- validar estratégias automatizadas;
- medir robustez estatística;
- detectar overfitting;
- analisar regimes de mercado;
- realizar estudos de Monte Carlo;
- executar Walk Forward Analysis;
- construir portfólios quantitativos descorrelacionados.

O framework foi desenvolvido para suportar:
- robôs de WINFUT;
- WDOFUT;
- Forex;
- futuros;
- estratégias baseadas em Renko;
- estratégias direcionais;
- sistemas quantitativos híbridos.

---

# Pipeline Quantitativo

```text
CSV Profit
    ↓
Robot Loader
    ↓
Metrics Engine
    ↓
Regime Engine
    ↓
Monte Carlo
    ↓
Walk Forward
    ↓
Portfolio Engine
```

---

# Estrutura do Projeto

```text
LAB_QUANT_FRAMEWORK/

├── data/                  # Dados OHLCV de mercado
│
├── robots/                # CSVs exportados do Profit
│
├── outputs/               # Resultados organizados por robô
│   ├── market/
│   └── Robo_Jost_NEW/
│       ├── charts/
│       ├── metrics/
│       ├── regime/
│       ├── monte_carlo/
│       └── walk_forward/
│
├── src/
│   ├── engines/           # Engines principais
│   │   ├── metrics_engine.py
│   │   ├── regime_engine.py
│   │   └── regime_cross_engine.py
│   │
│   ├── loaders/           # Carregadores de robôs
│   │   └── robot_loader.py
│   │
│   ├── modules/           # Módulos auxiliares
│   │   ├── drawdown.py
│   │   ├── streaks.py
│   │   └── metricas_auxiliares.py
│   │
│   ├── utils/             # Configurações e helpers
│   │   ├── config.py
│   │   └── helpers.py
│   │
│   └── legacy/            # Scripts antigos
│
├── monte_carlo/
│
├── walk_forward/
│
├── portfolio_engine/
│
├── reports/
│
├── requirements.txt
│
└── README.md
```

---

# Funcionalidades Atuais

## Metrics Engine

- Profit Factor
- Winrate
- Média por trade
- Drawdown máximo
- Streaks de perdas
- Curva de capital
- Resultado mensal
- Resultado diário
- Resultado por horário

---

## Regime Engine

- Cruzamento de trades com mercado
- Análise por horário
- Análise por volatilidade
- Análise de tendência
- Filtro de regime
- Curvas filtradas

---

## Monte Carlo

- Simulação de sobrevivência
- Estudo de drawdown
- Distribuição de capital
- Cenários extremos

---

# Roadmap

## Próximas Implementações

- [ ] Walk Forward Engine V1
- [ ] Portfolio Engine V1
- [ ] Correlation Engine
- [ ] Feature Engineering
- [ ] ML Regime Detection
- [ ] Dashboard Quantitativo
- [ ] Real-time Integration
- [ ] Risk Engine
- [ ] Position Sizing Engine
- [ ] Multi-Robot Supervisor

---

# Como instalar

```bash
git clone https://github.com/cpjost/LAB_QUANT_FRAMEWORK.git

cd LAB_QUANT_FRAMEWORK

pip install -r requirements.txt
```

---

# Como utilizar

## 1. Exportar operações do Profit

Exporte o relatório operacional em CSV e coloque em:

```text
robots/
```

---

## 2. Rodar Loader

```bash
python src/loaders/robot_loader.py
```

---

## 3. Rodar Metrics Engine

```bash
python src/engines/metrics_engine.py
```

---

## 4. Rodar Regime Engine

```bash
python src/engines/regime_engine.py
```

---

# Outputs

Os resultados serão organizados automaticamente em:

```text
outputs/NOME_DO_ROBO/
```

Separados por:

- charts
- metrics
- regime
- monte_carlo
- walk_forward

---

# Tecnologias Utilizadas

- Python
- Pandas
- NumPy
- Matplotlib
- OpenPyXL

---

# Filosofia do Projeto

Este projeto busca construir um laboratório quantitativo profissional baseado em:

- robustez estatística;
- sobrevivência de longo prazo;
- análise quantitativa séria;
- controle de risco;
- modularização;
- escalabilidade.

O foco não é encontrar um único robô vencedor, mas construir um processo quantitativo replicável.

---

# Autor

Carlos Peter Jost

GitHub:
https://github.com/cpjost

---

# Disclaimer

Este projeto possui fins educacionais e de pesquisa quantitativa.

Não constitui recomendação financeira.