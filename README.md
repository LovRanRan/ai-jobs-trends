# AI Jobs Trends Tracker

> 量化 AI 工程岗位市场真实需求:每日抓取 20+ AI 公司的 JD,用 LLM 抽取技能要求,做日/周/月趋势。

[![Daily Run](https://github.com/LovRanRan/ai-jobs-trends/actions/workflows/daily-run.yml/badge.svg)](https://github.com/LovRanRan/ai-jobs-trends/actions/workflows/daily-run.yml)

## 项目速览

| 维度 | 说明 |
|---|---|
| 核心能力 | ETL + NLP + 趋势分析 |
| 数据源 | Greenhouse / Lever / Ashby 公开 API,FAANG careers(Week 2+) |
| 抽取 | Claude Haiku 4.5 tool use,标准 JSON Schema |
| 归一化 | OpenAI `text-embedding-3-small` + cosine similarity + canonical taxonomy |
| 存储 | SQLite → Turso(远程只读给 dashboard 用) |
| 输出 | GitHub 自动 commit 的 daily/weekly/monthly markdown + Next.js dashboard |
| 调度 | GitHub Actions,每天 UTC 20:00(PDT 13:00) |

完整设计文档见 [`ai-jobs-trends-project-brief.md`](./ai-jobs-trends-project-brief.md),实施进度见 [`progress.md`](./progress.md)。

## 架构

```
ATS Sources → Dedup → Haiku Extract → Canonical Normalize → SQLite → Reporter → GitHub / Dashboard / MCP
```

详见 brief §2 · 整体架构。

## 本地跑

```bash
# 安装依赖
uv sync

# 复制环境变量模板
cp .env.example .env
# 编辑 .env 填入 ANTHROPIC_API_KEY 和 OPENAI_API_KEY

# 初始化数据库
uv run python -m src.storage.init_db

# 跑一次 ingestion(Week 1 周二之后可用)
uv run python -m src.main
```

## 目录结构

```
ai-jobs-trends/
├── .github/workflows/     # CI 调度
├── src/
│   ├── sources/           # Greenhouse / Lever / Ashby / FAANG
│   ├── extraction/        # Haiku tool use
│   ├── normalization/     # taxonomy + embedder
│   ├── storage/           # SQLAlchemy models
│   └── reporter/          # daily / weekly / monthly markdown
├── digests/               # 自动生成的报告(公开)
├── data/                  # taxonomy + embeddings(jobs.sqlite 本地 gitignore)
├── config/                # companies.yaml / my_stack.yaml
└── notes/                 # 本地笔记(gitignore)
```

## 如何接入新公司

编辑 `config/companies.yaml`,添加一行:

```yaml
- slug: new-company
  source: greenhouse   # greenhouse / lever / ashby
  name: New Company Inc.
```

## License

MIT
