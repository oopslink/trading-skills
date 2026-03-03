import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def alpha():
    """Alpha strategy analysis commands."""


@alpha.command("sector-strategy")
@click.option("--sector-code", required=True, help="e.g. 801010.SI")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.pass_context
def sector_strategy(ctx, sector_code, benchmark_code, end_date):
    """Analyze a single sector's alpha vs benchmark."""
    pro = get_pro(ctx)
    df = pro.sw_daily(ts_code=sector_code, trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def rank_l1(ctx, benchmark_code, end_date, top_n):
    """Rank L1 Shenwan sectors by alpha vs benchmark."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l2")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def rank_l2(ctx, benchmark_code, end_date, top_n):
    """Rank L2 Shenwan sectors by alpha vs benchmark."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1-full")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.pass_context
def rank_l1_full(ctx, benchmark_code, end_date):
    """Full L1 sector alpha ranking (all sectors)."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l1-velocity")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.pass_context
def rank_l1_velocity(ctx, benchmark_code, end_date):
    """L1 sector alpha rank velocity (momentum of ranking changes)."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))


@alpha.command("rank-l2-velocity")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--end-date", default="")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def rank_l2_velocity(ctx, benchmark_code, end_date, top_n):
    """L2 sector alpha rank velocity (momentum of ranking changes)."""
    pro = get_pro(ctx)
    df = pro.sw_daily(trade_date=end_date)
    click.echo(format_output(df, ctx.obj["fmt"]))
