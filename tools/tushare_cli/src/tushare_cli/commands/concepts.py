import click
from tushare_cli.api import get_pro, call_api
from tushare_cli.output import format_output


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
    params = {"ts_code": ts_code, "name": name, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "dc_index", params,
                  lambda: pro.dc_index(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command()
@click.option("--ts-code", default="", help="Board code")
@click.option("--con-code", default="", help="Stock code")
@click.option("--trade-date", default="")
@click.pass_context
def members(ctx, ts_code, con_code, trade_date):
    """Concept board constituent stocks."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "con_code": con_code, "trade_date": trade_date}
    df = call_api(ctx, "dc_member", params,
                  lambda: pro.dc_member(**params))
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
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date, "idx_type": idx_type}
    df = call_api(ctx, "dc_daily", params,
                  lambda: pro.dc_daily(ts_code=ts_code, trade_date=trade_date,
                                       start_date=start_date, end_date=end_date,
                                       idx_type=idx_type))
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
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date, "content_type": content_type}
    df = call_api(ctx, "moneyflow_ind_dc", params,
                  lambda: pro.moneyflow_ind_dc(ts_code=ts_code, trade_date=trade_date,
                                               start_date=start_date, end_date=end_date,
                                               content_type=content_type))
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
    params = {"trade_date": end_date}
    df = call_api(ctx, "dc_daily_volume_anomaly", params,
                  lambda: pro.dc_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("hot-boards")
@click.option("--trade-date", default="")
@click.option("--limit", default=20, type=int)
@click.option("--board-type", default="concept")
@click.pass_context
def hot_boards(ctx, trade_date, limit, board_type):
    """Top hot concept/industry boards by price change."""
    pro = get_pro(ctx)
    params = {"trade_date": trade_date}
    df = call_api(ctx, "dc_daily_hot_boards", params,
                  lambda: pro.dc_daily(trade_date=trade_date))
    if not df.empty and "pct_chg" in df.columns:
        df = df.nlargest(limit, "pct_chg")
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("rank-alpha")
@click.option("--end-date", default="")
@click.option("--hot-limit", default=50, type=int)
@click.pass_context
def rank_alpha(ctx, end_date, hot_limit):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"trade_date": end_date}
    df = call_api(ctx, "dc_daily_rank_alpha", params,
                  lambda: pro.dc_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))


@concepts.command("rank-alpha-velocity")
@click.option("--end-date", default="")
@click.option("--board-type", default="concept")
@click.pass_context
def rank_alpha_velocity(ctx, end_date, board_type):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"trade_date": end_date}
    df = call_api(ctx, "dc_daily_rank_alpha_velocity", params,
                  lambda: pro.dc_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))
