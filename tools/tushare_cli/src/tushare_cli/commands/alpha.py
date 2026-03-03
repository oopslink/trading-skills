import click
from tushare_cli.api import get_pro, call_api
from tushare_cli.output import format_output


@click.group()
def alpha():
    """Alpha strategy analysis commands."""


@alpha.command("sector-strategy")
@click.option("--sector-code", required=True, help="e.g. 801010.SI")
@click.option("--end-date", default="")
@click.pass_context
def sector_strategy(ctx, sector_code, end_date):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"ts_code": sector_code, "trade_date": end_date}
    df = call_api(ctx, "sw_daily_sector_strategy", params,
                  lambda: pro.sw_daily(ts_code=sector_code, trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1")
@click.option("--end-date", default="")
@click.pass_context
def rank_l1(ctx, end_date):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"trade_date": end_date}
    df = call_api(ctx, "sw_daily_rank_l1", params,
                  lambda: pro.sw_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l2")
@click.option("--end-date", default="")
@click.pass_context
def rank_l2(ctx, end_date):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"trade_date": end_date}
    df = call_api(ctx, "sw_daily_rank_l2", params,
                  lambda: pro.sw_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1-full")
@click.option("--end-date", default="")
@click.pass_context
def rank_l1_full(ctx, end_date):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"trade_date": end_date}
    df = call_api(ctx, "sw_daily_rank_l1_full", params,
                  lambda: pro.sw_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1-velocity")
@click.option("--end-date", default="")
@click.pass_context
def rank_l1_velocity(ctx, end_date):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"trade_date": end_date}
    df = call_api(ctx, "sw_daily_rank_l1_velocity", params,
                  lambda: pro.sw_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l2-velocity")
@click.option("--end-date", default="")
@click.pass_context
def rank_l2_velocity(ctx, end_date):
    """Returns raw Shenwan daily data. Alpha computation requires tushare_mcp's alpha_strategy_analyzer module."""
    pro = get_pro(ctx)
    params = {"trade_date": end_date}
    df = call_api(ctx, "sw_daily_rank_l2_velocity", params,
                  lambda: pro.sw_daily(trade_date=end_date))
    click.echo(format_output(df, ctx.obj["fmt"]))
