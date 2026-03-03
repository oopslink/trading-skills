import io
import pandas as pd
from rich.console import Console
from rich.table import Table


def format_output(df: pd.DataFrame, fmt: str) -> str:
    if fmt == "json":
        return df.to_json(orient="records", force_ascii=False, indent=2) if not df.empty else "[]"
    if fmt == "csv":
        return df.to_csv(index=False)
    if fmt == "table":
        return _to_rich_table(df)
    raise ValueError(f"Unknown format: {fmt!r}. Choose table, json, or csv.")


def _to_rich_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "(no data)"
    table = Table(show_header=True, header_style="bold cyan")
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.iterrows():
        table.add_row(*[str(v) for v in row])
    buf = io.StringIO()
    console = Console(file=buf, highlight=False)
    console.print(table)
    return buf.getvalue()
