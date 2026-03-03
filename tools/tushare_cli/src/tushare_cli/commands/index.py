import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def index():
    """Index data commands."""


@index.command("global")
@click.option("--index-code", "ts_code", default="")
@click.option("--index-name", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def global_index(ctx, ts_code, index_name, trade_date, start_date, end_date):
    """Global index data (S&P500, Nikkei, HSI, etc.)."""
    pro = get_pro(ctx)
    df = pro.index_global(ts_code=ts_code, trade_date=trade_date,
                          start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@index.command("sw-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def sw_daily(ctx, ts_code, trade_date, start_date, end_date):
    """Shenwan industry index daily data."""
    pro = get_pro(ctx)
    df = pro.sw_daily(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@index.command()
@click.option("--level", default="L1", help="L1, L2, or L3")
@click.option("--src", default="SW2021")
@click.pass_context
def classify(ctx, level, src):
    """List industry index codes by classification level."""
    pro = get_pro(ctx)
    df = pro.index_classify(level=level, src=src)
    click.echo(format_output(df, ctx.obj["fmt"]))


@index.command("sw-members")
@click.option("--l1-code", default="")
@click.option("--l2-code", default="")
@click.option("--l3-code", default="")
@click.option("--ts-code", default="")
@click.pass_context
def sw_members(ctx, l1_code, l2_code, l3_code, ts_code):
    """Shenwan industry index constituent stocks."""
    pro = get_pro(ctx)
    df = pro.index_member_all(l1_code=l1_code, l2_code=l2_code,
                               l3_code=l3_code, ts_code=ts_code)
    click.echo(format_output(df, ctx.obj["fmt"]))
