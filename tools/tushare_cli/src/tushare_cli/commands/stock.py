import click
import pandas as pd
from tushare_cli.api import get_pro, call_api
from tushare_cli.output import format_output


@click.group()
def stock():
    """Stock market data commands."""


@stock.command()
@click.option("--ts-code", default="")
@click.option("--name", default="")
@click.pass_context
def basic(ctx, ts_code, name):
    """Stock basic info."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "name": name,
              "fields": "ts_code,symbol,name,area,industry,list_date"}
    df = call_api(ctx, "stock_basic", params,
                  lambda: pro.stock_basic(ts_code=ts_code, name=name,
                                          fields="ts_code,symbol,name,area,industry,list_date"))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command()
@click.option("--keyword", required=True)
@click.pass_context
def search(ctx, keyword):
    """Search stocks by keyword (name or ts_code)."""
    pro = get_pro(ctx)
    params = {"fields": "ts_code,symbol,name,area,industry,list_date"}
    df = call_api(ctx, "stock_basic_search", params,
                  lambda: pro.stock_basic(fields="ts_code,symbol,name,area,industry,list_date"))
    if not df.empty:
        name_mask = df["name"].str.contains(keyword, na=False) if "name" in df.columns else False
        code_mask = df["ts_code"].str.contains(keyword, na=False) if "ts_code" in df.columns else False
        df = df[name_mask | code_mask]
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily(ctx, ts_code, trade_date, start_date, end_date):
    """Stock daily OHLCV data."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "stock_daily", params,
                  lambda: pro.daily(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def weekly(ctx, ts_code, trade_date, start_date, end_date):
    """Stock weekly OHLCV data."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "stock_weekly", params,
                  lambda: pro.weekly(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("etf-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def etf_daily(ctx, ts_code, trade_date, start_date, end_date):
    """ETF daily data."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "etf_daily", params,
                  lambda: pro.fund_daily(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("holder-trade")
@click.option("--ts-code", default="")
@click.option("--ann-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--trade-type", default="", help="IN or DE")
@click.option("--holder-type", default="", help="P=person, C=company, G=gov")
@click.pass_context
def holder_trade(ctx, ts_code, ann_date, start_date, end_date, trade_type, holder_type):
    """Shareholder buy/sell trades."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "ann_date": ann_date,
              "start_date": start_date, "end_date": end_date,
              "trade_type": trade_type, "holder_type": holder_type}
    df = call_api(ctx, "stk_holdertrade", params,
                  lambda: pro.stk_holdertrade(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("holder-number")
@click.option("--ts-code", default="")
@click.option("--ann-date", default="")
@click.option("--enddate", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def holder_number(ctx, ts_code, ann_date, enddate, start_date, end_date):
    """Number of shareholders."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "ann_date": ann_date,
              "enddate": enddate, "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "stk_holdernumber", params,
                  lambda: pro.stk_holdernumber(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def moneyflow(ctx, ts_code, trade_date, start_date, end_date):
    """Stock capital flow (Dongcai)."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "moneyflow_dc", params,
                  lambda: pro.moneyflow_dc(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def survey(ctx, ts_code, trade_date, start_date, end_date):
    """Institutional survey records."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "stk_surv", params,
                  lambda: pro.stk_surv(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("cyq-perf")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def cyq_perf(ctx, ts_code, trade_date, start_date, end_date):
    """Chip distribution performance."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "cyq_perf", params,
                  lambda: pro.cyq_perf(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("daily-basic")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily_basic(ctx, ts_code, trade_date, start_date, end_date):
    """Daily fundamentals (PE, PB, turnover rate)."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "daily_basic", params,
                  lambda: pro.daily_basic(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("top-list")
@click.option("--trade-date", default="")
@click.option("--ts-code", default="")
@click.pass_context
def top_list(ctx, trade_date, ts_code):
    """Dragon and Tiger list."""
    pro = get_pro(ctx)
    params = {"trade_date": trade_date, "ts_code": ts_code}
    df = call_api(ctx, "top_list", params,
                  lambda: pro.top_list(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("top-inst")
@click.option("--trade-date", default="")
@click.option("--ts-code", default="")
@click.pass_context
def top_inst(ctx, trade_date, ts_code):
    """Institutional Dragon and Tiger details."""
    pro = get_pro(ctx)
    params = {"trade_date": trade_date, "ts_code": ts_code}
    df = call_api(ctx, "top_inst", params,
                  lambda: pro.top_inst(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command()
@click.option("--ts-code", required=True)
@click.option("--freq", default="15MIN",
              type=click.Choice(["1MIN", "5MIN", "15MIN", "30MIN", "60MIN"]))
@click.option("--date", "date_str", default="")
@click.pass_context
def minute(ctx, ts_code, freq, date_str):
    """Intraday minute data."""
    pro = get_pro(ctx)
    if date_str:
        params = {"ts_code": ts_code, "freq": freq, "date": date_str}
        df = call_api(ctx, "rt_min_daily", params,
                      lambda: pro.rt_min_daily(**params))
    else:
        params = {"ts_code": ts_code, "freq": freq}
        df = call_api(ctx, "rt_min", params,
                      lambda: pro.rt_min(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("rt-k")
@click.option("--ts-code", required=True)
@click.pass_context
def rt_k(ctx, ts_code):
    """Real-time K-line data."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code}
    df = call_api(ctx, "rt_k", params,
                  lambda: pro.rt_k(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("share-float")
@click.option("--ts-code", default="")
@click.option("--ann-date", default="")
@click.option("--float-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def share_float(ctx, ts_code, ann_date, float_date, start_date, end_date):
    """Lock-up share release schedule."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "ann_date": ann_date,
              "float_date": float_date, "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "share_float", params,
                  lambda: pro.share_float(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command()
@click.option("--ann-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def repurchase(ctx, ann_date, start_date, end_date):
    """Share repurchase records."""
    pro = get_pro(ctx)
    params = {"ann_date": ann_date, "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "repurchase", params,
                  lambda: pro.repurchase(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("pledge-detail")
@click.option("--ts-code", required=True)
@click.pass_context
def pledge_detail(ctx, ts_code):
    """Share pledge details."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code}
    df = call_api(ctx, "pledge_detail", params,
                  lambda: pro.pledge_detail(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("block-trade")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def block_trade(ctx, ts_code, trade_date, start_date, end_date):
    """Block trade records."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "block_trade", params,
                  lambda: pro.block_trade(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("index-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def index_daily(ctx, ts_code, trade_date, start_date, end_date):
    """Stock index daily data."""
    pro = get_pro(ctx)
    params = {"ts_code": ts_code, "trade_date": trade_date,
              "start_date": start_date, "end_date": end_date}
    df = call_api(ctx, "index_daily_stock", params,
                  lambda: pro.index_daily(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("sector-strength")
@click.option("--sector-type", default="sw_l1", help="sw_l1, sw_l2, concept")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def sector_strength(ctx, sector_type, top_n):
    """Real-time strong sectors scan."""
    pro = get_pro(ctx)
    ts_code_val = f"*.{sector_type}"
    params = {"ts_code": ts_code_val}
    df = call_api(ctx, "rt_k_sector", params,
                  lambda: pro.rt_k(ts_code=ts_code_val))
    if not df.empty and "pct_chg" in df.columns:
        df = df.nlargest(top_n, "pct_chg")
    click.echo(format_output(df, ctx.obj["fmt"]))


@stock.command("sector-health")
@click.option("--sector-type", default="sw_l1")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def sector_health(ctx, sector_type, benchmark_code, top_n):
    """Fetch benchmark K-line data (sector comparison not yet implemented)."""
    pro = get_pro(ctx)
    params = {"ts_code": benchmark_code}
    df = call_api(ctx, "rt_k_benchmark", params,
                  lambda: pro.rt_k(ts_code=benchmark_code))
    click.echo(format_output(df, ctx.obj["fmt"]))
