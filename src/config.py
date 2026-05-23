from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ROBOTS_DIR = BASE_DIR / "robots"
OUTPUTS_DIR = BASE_DIR / "outputs"
FEATURES_DIR = BASE_DIR / "features"
REPORTS_DIR = BASE_DIR / "reports"

DEFAULT_ROBOT = "Robo_Jost_NEW"
DEFAULT_MARKET_FILE = "WINFUT_F_0_5min.csv"
DEFAULT_MARKET_NAME = "WINFUT_5min"


def robot_output_dirs(robot_name: str):
    base = OUTPUTS_DIR / robot_name
    dirs = {
        "base": base,
        "metrics": base / "metrics",
        "charts": base / "charts",
        "regime": base / "regime",
        "monte_carlo": base / "monte_carlo",
        "walk_forward": base / "walk_forward",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def market_output_dir(market_name: str = DEFAULT_MARKET_NAME):
    d = OUTPUTS_DIR / "market" / market_name
    d.mkdir(parents=True, exist_ok=True)
    return d
