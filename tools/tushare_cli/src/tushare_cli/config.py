import os
import sys
import tomllib
from pathlib import Path

CONFIG_PATH = Path.home() / ".tushare_cli" / "config.toml"


def resolve_token(token: str | None) -> str:
    if token:
        return token
    env = os.environ.get("TUSHARE_TOKEN")
    if env:
        return env
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
        t = data.get("tushare", {}).get("token")
        if t:
            return t
    print(
        "Error: Tushare token not found.\n"
        "Set TUSHARE_TOKEN env var, use --token flag, or run:\n"
        "  tushare-cli config set-token <your-token>",
        file=sys.stderr,
    )
    sys.exit(1)


def save_token(token: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = f'[tushare]\ntoken = "{token}"\n'
    CONFIG_PATH.write_text(content)
    print(f"Token saved to {CONFIG_PATH}")
