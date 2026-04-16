"""
SQLAlchemy models — 对应 brief §3 Stage 3 · Storage 的两张表。

设计要点:
- jobs_raw:append-only 原始数据,主键 `id = sha1(company + external_id)[:16]`
- skill_mentions:fact table,一行 "某日 · 某岗位 · 某技能",聚合查询全在这张做 GROUP BY
- 所有查询都对 (date, canonical_skill) 建索引 → 趋势查询 < 100ms

参考 brief §3 Stage 3 · ADR #2(SQLite 不用 Postgres)、ADR #7(公开 repo 不存 full_description)。
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

# ---------- Base ----------


class Base(DeclarativeBase):
    """Declarative base. 所有 model 继承自这里。"""


# ---------- Tables ----------


class Job(Base):
    """
    jobs_raw — 一条 job posting 的原始记录。

    - `id` 主键为 `sha1(company + external_id)[:16]`,避免重复入库
    - `full_description` 仅在本地 sqlite 保留;公开 repo 的 sqlite 会清空该字段(见 ADR #7)
    """

    __tablename__ = "jobs_raw"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    company: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    location: Mapped[str | None] = mapped_column(String(128))
    remote_policy: Mapped[str | None] = mapped_column(String(16))  # remote|hybrid|onsite
    full_description: Mapped[str | None] = mapped_column(Text)
    posted_date: Mapped[datetime | None] = mapped_column(Date, index=True)
    source: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # greenhouse|lever|ashby|faang-meta|...
    seniority: Mapped[str | None] = mapped_column(String(16))  # junior|mid|senior|staff|principal
    is_agent_role: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    years_required: Mapped[int | None] = mapped_column(Integer)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    skill_mentions: Mapped[list[SkillMention]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job {self.company}/{self.id[:8]} · {self.title[:40]!r}>"


class SkillMention(Base):
    """
    skill_mentions — 事实表,聚合查询的核心。

    - 一行代表 "某日 · 某岗位 · 某技能" 的提及
    - `is_required=True` 用于区分 required 和 nice-to-have
    - `skill_category` 对应 extraction schema 里的 bucket(framework/llm_provider/vector_db/infra)
    - 复合索引 `(date, canonical_skill)` 加速趋势查询
    """

    __tablename__ = "skill_mentions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    canonical_skill: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_skill: Mapped[str | None] = mapped_column(String(128))  # 归一化前的原始字符串(调试用)
    skill_category: Mapped[str | None] = mapped_column(
        String(32)
    )  # framework|llm_provider|vector_db|infra|other
    job_id: Mapped[str] = mapped_column(
        String(16), ForeignKey("jobs_raw.id", ondelete="CASCADE"), nullable=False
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    job: Mapped[Job] = relationship(back_populates="skill_mentions")

    __table_args__ = (
        Index("ix_skill_date_canonical", "date", "canonical_skill"),
        Index("ix_skill_category_date", "skill_category", "date"),
    )

    def __repr__(self) -> str:
        return f"<SkillMention {self.date} · {self.canonical_skill} · req={self.is_required}>"


# ---------- Session helpers ----------


def _default_db_path() -> str:
    """默认 sqlite 路径。可被 DATABASE_URL 覆盖。"""
    root = Path(__file__).resolve().parents[2]  # repo root
    return f"sqlite:///{root / 'data' / 'jobs.sqlite'}"


def get_engine(url: str | None = None):
    """
    返回 SQLAlchemy engine。优先读 DATABASE_URL 环境变量。

    usage:
        engine = get_engine()
        Base.metadata.create_all(engine)
    """
    url = url or os.environ.get("DATABASE_URL") or _default_db_path()
    # SQLite 需要 check_same_thread=False 以支持多线程(GitHub Actions 环境)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


def get_session(engine=None) -> Session:
    """便捷 session 工厂。若不传 engine 则用默认。"""
    return Session(engine or get_engine(), future=True)
