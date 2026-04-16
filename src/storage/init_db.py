"""
初始化 SQLite 数据库,创建所有表。

usage:
    uv run python -m src.storage.init_db
"""

from __future__ import annotations

from pathlib import Path

from src.storage.models import Base, get_engine


def init_db() -> None:
    """创建所有表,幂等。"""
    # 确保 data 目录存在
    root = Path(__file__).resolve().parents[2]
    (root / "data").mkdir(exist_ok=True)

    engine = get_engine()
    Base.metadata.create_all(engine)

    print(f"✅ Database initialized at: {engine.url}")
    print(f"   Tables: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    init_db()
