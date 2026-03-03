import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output
from tushare_cli.cache import get_cached, set_cached, make_key


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


def emit(ctx, df, api_name=None, params=None):
    use_cache = ctx.obj.get("cache", False)
    if use_cache and api_name:
        key = make_key(api_name, params or {})
        cached = get_cached(key)
        if cached is not None:
            click.echo(format_output(cached, ctx.obj["fmt"]))
            return
    result_df = df if df is not None else __import__("pandas").DataFrame()
    click.echo(format_output(result_df, ctx.obj["fmt"]))
    if use_cache and api_name and df is not None and not df.empty:
        set_cached(make_key(api_name, params or {}), df)


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
    df = pro.stock_basic(ts_code=ts_code, name=name,
                         fields="ts_code,symbol,name,area,industry,list_date")
    emit(ctx, df)


@stock.command()
@click.option("--keyword", required=True)
@click.pass_context
def search(ctx, keyword):
    """Search stocks by keyword (name or ts_code)."""
    pro = get_pro(ctx)
    df = pro.stock_basic(fields="ts_code,symbol,name,area,industry,list_date")
    if df is not None and not df.empty:
        name_mask = df["name"].str.contains(keyword, na=False) if "name" in df.columns else False
        code_mask = df["ts_code"].str.contains(keyword, na=False) if "ts_code" in df.columns else False
        df = df[name_mask | code_mask]
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily(ctx, ts_code, trade_date, start_date, end_date):
    """Stock daily OHLCV data."""
    pro = get_pro(ctx)
    df = pro.daily(ts_code=ts_code, trade_date=trade_date,
                   start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def weekly(ctx, ts_code, trade_date, start_date, end_date):
    """Stock weekly OHLCV data."""
    pro = get_pro(ctx)
    df = pro.weekly(ts_code=ts_code, trade_date=trade_date,
                    start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("etf-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def etf_daily(ctx, ts_code, trade_date, start_date, end_date):
    """ETF daily data."""
    pro = get_pro(ctx)
    df = pro.fund_daily(ts_code=ts_code, trade_date=trade_date,
                        start_date=start_date, end_date=end_date)
    emit(ctx, df)


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
    df = pro.stk_holdertrade(ts_code=ts_code, ann_date=ann_date,
                              start_date=start_date, end_date=end_date,
                              trade_type=trade_type, holder_type=holder_type)
    emit(ctx, df)


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
    df = pro.stk_holdernumber(ts_code=ts_code, ann_date=ann_date,
                               enddate=enddate, start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def moneyflow(ctx, ts_code, trade_date, start_date, end_date):
    """Stock capital flow (Dongcai)."""
    pro = get_pro(ctx)
    df = pro.moneyflow_dc(ts_code=ts_code, trade_date=trade_date,
                          start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def survey(ctx, ts_code, trade_date, start_date, end_date):
    """Institutional survey records."""
    pro = get_pro(ctx)
    df = pro.stk_surv(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("cyq-perf")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def cyq_perf(ctx, ts_code, trade_date, start_date, end_date):
    """Chip distribution performance."""
    pro = get_pro(ctx)
    df = pro.cyq_perf(ts_code=ts_code, trade_date=trade_date,
                      start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("daily-basic")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def daily_basic(ctx, ts_code, trade_date, start_date, end_date):
    """Daily fundamentals (PE, PB, turnover rate)."""
    pro = get_pro(ctx)
    df = pro.daily_basic(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("top-list")
@click.option("--trade-date", default="")
@click.option("--ts-code", default="")
@click.pass_context
def top_list(ctx, trade_date, ts_code):
    """Dragon and Tiger list."""
    pro = get_pro(ctx)
    df = pro.top_list(trade_date=trade_date, ts_code=ts_code)
    emit(ctx, df)


@stock.command("top-inst")
@click.option("--trade-date", default="")
@click.option("--ts-code", default="")
@click.pass_context
def top_inst(ctx, trade_date, ts_code):
    """Institutional Dragon and Tiger details."""
    pro = get_pro(ctx)
    df = pro.top_inst(trade_date=trade_date, ts_code=ts_code)
    emit(ctx, df)


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
        df = pro.rt_min_daily(ts_code=ts_code, freq=freq, date=date_str)
    else:
        df = pro.rt_min(ts_code=ts_code, freq=freq)
    emit(ctx, df)


@stock.command("rt-k")
@click.option("--ts-code", required=True)
@click.pass_context
def rt_k(ctx, ts_code):
    """Real-time K-line data."""
    pro = get_pro(ctx)
    df = pro.rt_k(ts_code=ts_code)
    emit(ctx, df)


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
    df = pro.share_float(ts_code=ts_code, ann_date=ann_date,
                         float_date=float_date, start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command()
@click.option("--ann-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def repurchase(ctx, ann_date, start_date, end_date):
    """Share repurchase records."""
    pro = get_pro(ctx)
    df = pro.repurchase(ann_date=ann_date, start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("pledge-detail")
@click.option("--ts-code", required=True)
@click.pass_context
def pledge_detail(ctx, ts_code):
    """Share pledge details."""
    pro = get_pro(ctx)
    df = pro.pledge_detail(ts_code=ts_code)
    emit(ctx, df)


@stock.command("block-trade")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def block_trade(ctx, ts_code, trade_date, start_date, end_date):
    """Block trade records."""
    pro = get_pro(ctx)
    df = pro.block_trade(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("index-daily")
@click.option("--ts-code", default="")
@click.option("--trade-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.pass_context
def index_daily(ctx, ts_code, trade_date, start_date, end_date):
    """Stock index daily data."""
    pro = get_pro(ctx)
    df = pro.index_daily(ts_code=ts_code, trade_date=trade_date,
                         start_date=start_date, end_date=end_date)
    emit(ctx, df)


@stock.command("sector-strength")
@click.option("--sector-type", default="sw_l1", help="sw_l1, sw_l2, concept")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def sector_strength(ctx, sector_type, top_n):
    """Real-time strong sectors scan."""
    pro = get_pro(ctx)
    df = pro.rt_k(ts_code=f"*.{sector_type}")
    if df is not None and not df.empty and "pct_chg" in df.columns:
        df = df.nlargest(top_n, "pct_chg")
    emit(ctx, df)


@stock.command("sector-health")
@click.option("--sector-type", default="sw_l1")
@click.option("--benchmark", "benchmark_code", default="000300.SH")
@click.option("--top-n", default=10, type=int)
@click.pass_context
def sector_health(ctx, sector_type, benchmark_code, top_n):
    """Sector health analysis vs benchmark."""
    pro = get_pro(ctx)
    df = pro.rt_k(ts_code=benchmark_code)
    emit(ctx, df)
