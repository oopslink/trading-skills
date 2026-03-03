import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def concepts():
    """East Money concept board commands."""


@concepts.command()
@click.option("--ts-code", default="")
@click.option("--name", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def board(ctx, ts_code, name, trade_date, start_date, end_date):
    """Concept board list and daily stats."""
    pro = get_pro(ctx)
    df = pro.dc_index(ts_code=ts_code, name=name, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command()
@click.option("--ts-code", default="", help="Board code")
@click.option("--con-code", default="", help="Stock code")
@click.option("--trade-date", default="")
@click.pass_context
def members(ctx, ts_code, con_code, trade_date):
    """Concept board constituent stocks."""
    pro = get_pro(ctx)
    df = pro.dc_member(ts_code=ts_code, con_code=con_code, trade_date=trade_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--idx-type", default="")
@click.pass_context
def daily(ctx, ts_code, trade_date, start_date, end_date, idx_type):
    """Concept board daily price data."""
    pro = get_pro(ctx)
    df = pro.dc_daily(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--content-type", default="")
@click.pass_context
def moneyflow(ctx, ts_code, trade_date, start_date, end_date, content_type):
    """Concept board capital flow data."""
    pro = get_pro(ctx)
    df = pro.moneyflow_ind_dc(ts_code=ts_code, trade_date=trade_date,
                               start_date=start_date, end_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("volume-anomaly")
@click.option("--end-date", default="")
@click.option("--vol-ratio", "vol_ratio_threshold", default=2.0, type=float)
@click.option("--price-min", "price_change_5d_min", default=-5.0, type=float)
@click.option("--price-max", "price_change_5d_max", default=20.0, type=float)
@click.option("--hot-limit", default=50, type=int)
@click.pass_context
def volume_anomaly(ctx, end_date, vol_ratio_threshold, price_change_5d_min,
                   price_change_5d_max, hot_limit):
    """Scan concept boards for volume anomalies."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("hot-boards")
@click.option("--trade-date", default="")
@click.option("--limit", default=20, type=int)
@click.option("--board-type", default="concept")
@click.pass_context
def hot_boards(ctx, trade_date, limit, board_type):
    """Top hot concept/industry boards by price change."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=trade_date)
    if df is not None and not df.empty and "pct_chg" in df.columns:
        df = df.nlargest(limit, "pct_chg")
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("rank-alpha")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.option("--hot-limit", default=50, type=int)
@click.pass_context
def rank_alpha(ctx, benchmark_code, end_date, top_n, hot_limit):
    """Rank concept boards by alpha vs benchmark."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("rank-alpha-velocity")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--board-type", default="concept")
@click.pass_context
def rank_alpha_velocity(ctx, benchmark_code, end_date, board_type):
    """Rank concept boards by alpha momentum (velocity)."""
    pro = get_pro(ctx)
    df = pro.dc_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))
