"""
CLI entrypoint. Week 1 只有 init-db,后续 ingest/extract/report 陆续加进来。

usage:
    uv run ai-jobs init-db
    uv run ai-jobs --help
"""

from __future__ import annotations

import click

from src.storage.init_db import init_db


@click.group()
def cli() -> None:
    """AI Jobs Trends Tracker CLI."""


@cli.command("init-db")
def cmd_init_db() -> None:
    """初始化 SQLite 数据库(幂等,已存在不会重建)。"""
    init_db()


@cli.command("version")
def cmd_version() -> None:
    """显示版本。"""
    from src import __version__

    click.echo(f"ai-jobs-trends v{__version__}")


if __name__ == "__main__":
    cli()
