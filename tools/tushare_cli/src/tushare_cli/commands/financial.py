import click
from tushare_cli.api import get_pro, call_api
from tushare_cli.output import format_output


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
    params = {"ts_code": ts_code, "start_date": start_date,
              "end_date": end_date, "report_type": report_type}
    df = call_api(ctx, "income", params,
                  lambda: pro.income(**params))
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
    params = {"ts_code": ts_code, "ann_date": ann_date,
              "start_date": start_date, "end_date": end_date, "period": period}
    df = call_api(ctx, "fina_indicator", params,
                  lambda: pro.fina_indicator(**params))
    click.echo(format_output(df, ctx.obj["fmt"]))
