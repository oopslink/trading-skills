import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def futures():
    """Futures market data commands."""


@futures.command()
@click.option("--exchange", default="", help="CFFEX, DCE, CZCE, SHFE, INE, GFEX")
@click.option("--fut-type", default="")
@click.option("--fut-code", default="")
@click.option("--list-date", default="")
@click.pass_context
def contracts(ctx, exchange, fut_type, fut_code, list_date):
    """Futures contract basic info."""
    pro = get_pro(ctx)
    df = pro.fut_basic(exchange=exchange, fut_type=fut_type,
                       fut_code=fut_code, list_date=list_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command("nh-index")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def nh_index(ctx, ts_code, trade_date, start_date, end_date):
    """NanHua futures index daily data."""
    pro = get_pro(ctx)
    df = pro.index_daily(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command()
@click.option("--trade-date", default="")
@click.option("--symbol", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--exchange", default="")
@click.pass_context
def holdings(ctx, trade_date, symbol, start_date, end_date, exchange):
    """Futures institutional holdings ranking (持仓排名)."""
    pro = get_pro(ctx)
    df = pro.fut_holding(trade_date=trade_date, symbol=symbol,
                         start_date=start_date, end_date=end_date, exchange=exchange)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command()
@click.option("--trade-date", default="")
@click.option("--symbol", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--exchange", default="")
@click.pass_context
def wsr(ctx, trade_date, symbol, start_date, end_date, exchange):
    """Warehouse stock receipts (仓单日报)."""
    pro = get_pro(ctx)
    df = pro.fut_wsr(trade_date=trade_date, symbol=symbol,
                     start_date=start_date, end_date=end_date, exchange=exchange)
    click.echo(format_output(df, ctx.obj["fmt"]))


@futures.command()
@click.option("--ts-code", required=True)
@click.option("--freq", default="15MIN",
              type=click.Choice(["1MIN", "5MIN", "15MIN", "30MIN", "60MIN"]))
@click.option("--date", "date_str", default="")
@click.pass_context
def minute(ctx, ts_code, freq, date_str):
    """Futures intraday minute data."""
    pro = get_pro(ctx)
    if date_str:
        df = pro.rt_fut_min_daily(ts_code=ts_code, freq=freq, date=date_str)
    else:
        df = pro.rt_fut_min(ts_code=ts_code, freq=freq)
    click.echo(format_output(df, ctx.obj["fmt"]))
