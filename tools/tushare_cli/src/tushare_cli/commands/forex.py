import click
from tushare_cli.api import get_pro, call_api
from tushare_cli.output import format_output


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
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "fx_daily", params,
                  lambda: pro.fx_daily(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))
