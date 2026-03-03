import hashlib
import json
from pathlib import Path
import pandas as pd

CACHE_DIR = Path.home() / ".tushare_cli" / "cache"


def make_key(api_name: str, params: dict) -> str:
    canonical = json.dumps({"api": api_name, **dict(sorted(params.items()))}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def get_cached(key: str) -> pd.DataFrame | None:
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    return pd.read_json(path, orient="records")


def set_cached(key: str, df: pd.DataFrame) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{key}.json"
    path.write_text(df.to_json(orient="records", force_ascii=False))
