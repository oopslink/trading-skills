import click
import tushare as ts
from tushare_cli.config import resolve_token
from tushare_cli.output import format_output


def get_pro(ctx):
    token = resolve_token(ctx.obj.get("token"))
    ts.set_token(token)
    return ts.pro_api()


@click.group()
def financial():
    """Financial statement commands."""


@financial.command()
@click.option("--ts-code", required=True)
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--report-type", default="")
@click.pass_context
def income(ctx, ts_code, start_date, end_date, report_type):
    """Income statement data."""
    pro = get_pro(ctx)
    df = pro.income(ts_code=ts_code, start_date=start_date,
                    end_date=end_date, report_type=report_type)
    click.echo(format_output(df, ctx.obj["fmt"]))


@financial.command()
@click.option("--ts-code", required=True)
@click.option("--ann-date", default="")
@click.option("--start", "start_date", default="")
@click.option("--end", "end_date", default="")
@click.option("--period", default="")
@click.pass_context
def indicator(ctx, ts_code, ann_date, start_date, end_date, period):
    """Key financial indicators (ROE, EPS, gross margin, etc.)."""
    pro = get_pro(ctx)
    df = pro.fina_indicator(ts_code=ts_code, ann_date=ann_date,
                            start_date=start_date, end_date=end_date, period=period)
    click.echo(format_output(df, ctx.obj["fmt"]))
