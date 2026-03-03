import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def forex():
    """Foreign exchange data commands."""


@forex.command()
@click.option("--symbol", "ts_code", default="USDCNH.FX",
              help="Currency pair, e.g. USDCNH or EURUSD")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily(ctx, ts_code, trade_date, start_date, end_date):
    """Forex daily quote data (USDCNH, EURUSD, etc.)."""
    if not ts_code.endswith(".FX"):
        ts_code = ts_code + ".FX"
    pro = get_pro(ctx)
    df = pro.fx_daily(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))
