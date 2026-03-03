import click


@click.group()
@click.pass_context
def cli(ctx):
    """tushare-cli: query Tushare Pro financial data from the terminal."""
    ctx.ensure_object(dict)
