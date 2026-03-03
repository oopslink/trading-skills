import click
from tushare_cli.config import save_token
from tushare_cli.commands.stock import stock
from tushare_cli.commands.index import index
from tushare_cli.commands.futures import futures
from tushare_cli.commands.forex import forex
from tushare_cli.commands.financial import financial
from tushare_cli.commands.concepts import concepts
from tushare_cli.commands.alpha import alpha


@click.group()
@click.option("--format", "fmt", default="table",
              type=click.Choice(["table", "json", "csv"]),
              help="Output format (default: table)")
@click.option("--cache", is_flag=True, default=False,
              help="Enable response caching")
@click.option("--token", default=None,
              help="Tushare API token (overrides env/config)")
@click.pass_context
def cli(ctx, fmt, cache, token):
    """tushare-cli: query Tushare Pro financial data from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["fmt"] = fmt
    ctx.obj["cache"] = cache
    ctx.obj["token"] = token


@cli.group()
def config():
    """Manage tushare-cli configuration."""


@config.command("set-token")
@click.argument("token")
def config_set_token(token):
    """Save Tushare API token to config file."""
    save_token(token)


cli.add_command(stock)
cli.add_command(index)
cli.add_command(futures)
cli.add_command(forex)
cli.add_command(financial)
cli.add_command(concepts)
cli.add_command(alpha)
