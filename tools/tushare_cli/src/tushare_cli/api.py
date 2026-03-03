import click
import sys
import tushare as ts
import pandas as pd
from tushare_cli.config import resolve_token
from tushare_cli.cache import get_cached, set_cached, make_key


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


def safe_call(func):
    """Wrap an API call with user-friendly error handling."""
    try:
        return func()
    except Exception as e:
        msg = str(e)
        if "token" in msg.lower() or "auth" in msg.lower():
            raise click.ClickException(
                f"Authentication failed: {msg}\n"
                "Check your token with: tushare-cli config set-token <token>"
            )
        raise click.ClickException(f"API error: {msg}")


def call_api(ctx, api_name: str, params: dict, api_func):
    """
    Cache-aware API call. Checks cache before calling the API.
    Only makes the network call on a cache miss.
    Returns a DataFrame (empty if None returned by API).
    """
    if ctx.obj.get("cache"):
        key = make_key(api_name, params)
        cached = get_cached(key)
        if cached is not None:
            return cached

    df = safe_call(api_func)
    if df is None:
        df = pd.DataFrame()

    if ctx.obj.get("cache") and not df.empty:
        key = make_key(api_name, params)
        set_cached(key, df)

    return df
