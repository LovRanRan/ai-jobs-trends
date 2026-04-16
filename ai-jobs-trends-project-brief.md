# AI Jobs Trends Tracker · 项目启动文档

> 这份文档是 Cowork project 的 context 起点。包含项目动机、架构、技术选型、实施路线图。
> 后续在 Cowork 中直接基于这份文档推进开发。

---

## 1. 项目背景与动机

AI 领域工具/框架迭代极快,"现在在学的东西"和"市场真正在招的技能"之间有明显错位。本项目的目标是**量化市场真实需求**:通过持续抓取 AI 相关岗位的 JD、提取并归一化其中的技能要求,以日/周/月趋势的形式呈现出来。

### 定位

这是一个 **ETL + NLP + 趋势分析** 的数据产品,核心能力包括:

- **Extraction**:非结构化 JD → 结构化技能数据(LLM 做实体识别,比正则健壮)
- **Normalization**:`LangChain` / `Langchain` / `langchain` 归一化,`Pinecone` 和 "vector database" 同义归并
- **Aggregation**:日/周/月滑动窗口,环比同比
- **Insight**:哪些技能在涨,哪些在衰,哪些是新出现的信号

---

## 2. 整体架构

### 四阶段管道

```
Stage 1: Ingestion
  ├─ Greenhouse API (Anthropic, OpenAI via Scale, Databricks, Figma...)
  ├─ Lever API (Netflix, 很多 AI 创业公司)
  ├─ Ashby API (Ramp, Vanta...)
  ├─ FAANG careers pages (Meta, Amazon, Google 爬虫)
  ├─ LinkedIn (Week 3+, 通过第三方 API)
  └─ Dedup layer (一级: company+external_id 哈希精确去重;
                   二级: 同公司同日岗位标题 RapidFuzz ≥ 92 视为重复)
        ↓
Stage 2: Extraction & Normalization
  ├─ LLM Extractor (Claude Haiku 4.5, tool use 结构化输出)
  └─ Canonical taxonomy (embedding similarity 归一化)
        ↓
Stage 3: Storage
  ├─ jobs_raw (append-only, 一行一个 job)
  └─ skill_mentions (fact table, 一行一个 "某日某岗位提到某技能")
        ↓
Stage 4: Output
  ├─ GitHub repo (daily/weekly/monthly markdown)
  └─ Next.js Dashboard (Vercel 部署, 可视化趋势)
```

---

## 3. 技术选型详解

### Stage 1 · 数据源策略(分阶段接入)

**Week 1 就能做的(公开 API,零成本):**

| 来源 | API | 覆盖公司 |
|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{company}/jobs` | Anthropic, Scale AI, Databricks, Airbnb, Figma, Notion, Stripe |
| Lever | `https://api.lever.co/v0/postings/{company}` | Netflix, 大量 AI 创业公司 |
| Ashby | Ashby 公开 API | Ramp, Vanta 等新兴独角兽 |

**这三个就能覆盖 80% 目标公司**——AI 独角兽几乎全用这三家 ATS。

**FAANG 特殊处理(Week 2 再做):**
- Meta, Amazon:自建 careers 页面,需要 Playwright 爬虫,但结构稳定
- Google:careers.google.com 有内部 API,抓取成本中等
- Apple, Netflix:结构化页面可抓

**LinkedIn → Week 3 以后**:反爬严格,用第三方 API(RapidAPI JSearch 或 Bright Data),月费 $20-50,避免自己维护爬虫。

### Stage 2 · 抽取 + 归一化(项目最核心亮点)

**模型选择:Haiku 4.5 而非 Opus**
- 成本差 10 倍以上
- 抽取任务简单,Haiku 完全够
- Tool use 强制结构化输出

**Extraction Schema(Tool use input_schema,标准 JSON Schema):**

```json
{
  "type": "object",
  "properties": {
    "required_skills": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Hard requirements — canonical skill names only"
    },
    "nice_to_have": {
      "type": "array",
      "items": {"type": "string"}
    },
    "frameworks":    {"type": "array", "items": {"type": "string"}},
    "llm_providers": {"type": "array", "items": {"type": "string"}},
    "vector_dbs":    {"type": "array", "items": {"type": "string"}},
    "infra":         {"type": "array", "items": {"type": "string"}},
    "seniority": {
      "type": "string",
      "enum": ["junior", "mid", "senior", "staff", "principal"]
    },
    "years_required": {"type": "integer", "minimum": 0},
    "is_agent_role":  {"type": "boolean", "description": "True if role explicitly builds LLM agents"},
    "remote_policy": {
      "type": "string",
      "enum": ["remote", "hybrid", "onsite"]
    }
  },
  "required": ["required_skills", "seniority", "is_agent_role"]
}
```

**归一化是技术亮点** —— JD 里同一个东西有十种写法:
- "LangChain" / "Langchain" / "langchain" / "LangChain framework"
- "vector database" / "vector DB" / "Pinecone/Weaviate (any vector store)"
- "LLM orchestration" / "agent framework" / "agent orchestration"

**做法:**
1. **Taxonomy 存储**:`data/taxonomy.yaml` 手工维护 canonical 词表(每个 canonical 词附常见 alias),另维护 `data/taxonomy_embeddings.npy` 存对应向量(repo 内,<1MB)
2. **Embedding 模型**:OpenAI `text-embedding-3-small`(1536 维,$0.02/M tokens,便宜且够用)。备选 Voyage-3 若要更高精度
3. **匹配流程**:新词 → embedding → 与 taxonomy 向量做 cosine similarity →
   - `similarity ≥ 0.85`:自动归并到最近的 canonical
   - `0.70 ≤ similarity < 0.85`:进 `data/review_queue.yaml`,每周人工 review 一次
   - `similarity < 0.70`:视为候选新词,若某词月内出现 ≥ 5 次则自动晋升 canonical
4. **检索实现**:taxonomy 规模小(预计 <500 词),直接 numpy 矩阵乘,不用 FAISS/Pinecone

这一块实际上就是个小型 **entity resolution** 系统,参数(阈值、晋升规则)都是可解释的决策。

### Stage 3 · 存储选型

**选 SQLite + GitHub Actions,不上 PostgreSQL:**

- 数据量小:每天 100-500 新岗位(`jobs_raw` 一年约 36k-180k 行;`skill_mentions` 按每岗 10-20 个技能算,一年百万级)
- SQLite 文件跟着 repo 走,CI 里直接读写 commit 回去
- 零运维、零成本
- 要做 dashboard 时再迁 Turso(libsql 远程版,500MB 免费)

**Schema:**

```sql
-- 原始数据表
CREATE TABLE jobs_raw (
    id TEXT PRIMARY KEY,           -- company + external_id hash
    company TEXT,
    title TEXT,
    location TEXT,
    remote_policy TEXT,
    full_description TEXT,
    posted_date DATE,
    source TEXT,                    -- greenhouse/lever/ashby/...
    seniority TEXT,
    is_agent_role BOOLEAN,
    scraped_at TIMESTAMP
);

-- 事实表,用于聚合查询
CREATE TABLE skill_mentions (
    id INTEGER PRIMARY KEY,
    date DATE,
    canonical_skill TEXT,
    skill_category TEXT,            -- framework/llm_provider/vector_db/infra/...
    job_id TEXT REFERENCES jobs_raw(id),
    is_required BOOLEAN             -- required vs nice-to-have
);
```

**聚合查询都在 `skill_mentions` 上做 GROUP BY**,极快。

### Stage 4 · 输出双轨

**GitHub repo 结构(Week 1 就有):**

```
ai-jobs-trends/
├── .github/workflows/
│   └── daily-run.yml              # 每天自动跑
├── src/
│   ├── sources/
│   │   ├── greenhouse.py
│   │   ├── lever.py
│   │   └── ashby.py
│   ├── extraction/
│   │   ├── extractor.py           # Haiku tool use
│   │   └── schemas.py
│   ├── normalization/
│   │   ├── taxonomy.py            # canonical taxonomy 管理
│   │   └── embedder.py            # 相似度归并
│   ├── storage/
│   │   └── models.py              # SQLAlchemy models
│   └── reporter/
│       ├── daily.py
│       ├── weekly.py
│       └── monthly.py
├── digests/
│   ├── daily/2026-04-16.md
│   ├── weekly/2026-W16.md
│   └── monthly/2026-04.md
├── data/
│   ├── jobs.sqlite
│   └── taxonomy.yaml
└── README.md
```

**Next.js Dashboard(Week 3):**
- Vercel 部署,免费
- 后端读 Turso(SQLite 远程版)
- 核心视图:
  - 技能趋势折线图(日/周/月切换)
  - 新兴 vs 衰退 Top 10
  - 公司画像对比(Anthropic 要什么 vs Google 要什么)
  - **"自定义技能栈 vs 市场契合度" 雷达图**(个性化视图)

---

## 4. 成本估算

假设:每天入库 300 JD,去重后实际抽取约 150 新 JD/天,单个 JD 约 1500 tokens input + 200 tokens output。

| 项 | 计算 | 月成本 |
|---|---|---|
| Haiku 4.5 抽取 | 150 JD × 30 天 × 1500 in / 200 out @ $1/$5 per M tokens | ~$10-15 |
| Embedding(新词归一化,增量) | ~500 新词/月 × 100 tokens @ $0.02/M | <$1 |
| GitHub Actions(2000 分钟/月免费) | — | $0 |
| Vercel 部署 | — | $0 |
| Turso(500MB 免费额度) | — | $0 |
| **合计** | | **~$12-16/月** |

若未来去重率下降或扩展公司数,成本上限估到 $25/月。

---

## 5. 实施路线图

### Week 1(Apr 16-22)· 数据管道跑通

**周一 — 项目骨架**
- GitHub repo `ai-jobs-trends` 建好
- 环境:Python 3.11 + uv + Anthropic SDK + SQLAlchemy
- GitHub Actions workflow 空架子跑通(每天 UTC 20:00;夏令时 PDT 为 13:00,冬令时 PST 为 12:00)
- SQLite schema 定好

**周二 — Greenhouse ingestion**
- `sources/greenhouse.py`:输入 company slug,输出标准化 job 列表
- 先接 10 家:Anthropic, Scale AI, Databricks, Airbnb, Figma, Notion, Stripe, Ramp, Vanta, 另选一家
- 跑一次看数据

**周三 — Lever + Ashby**
- `sources/lever.py` 和 `sources/ashby.py`
- 再接 5-10 家
- 统一 schema + dedup(company + external_id 做主键)

**周四 — Haiku 抽取**
- 定义 extraction schema(tool use)
- Prompt 工程:few-shot 示例区分 required vs nice-to-have
- 完整抽取一次,肉眼 review

**周五 — Markdown 报告**
- `reporter/daily.py`:读 SQLite,生成 `digests/daily/YYYY-MM-DD.md`
- 模板:新增岗位数、Top 10 技能、新出现的技能、公司分布
- GitHub Actions 自动 commit

**周末 — 打磨 + LangGraph 预研**
- LangGraph 官方文档 State + Graph 核心概念(为 Week 4 重构做准备)
- README 完整化:动机、架构图、如何本地跑、如何接入新公司

### Week 2(Apr 23-29)· 聚合和扩展

- 每周/每月滚动统计
- 新兴技能检测(本月出现但上月没有)
- 衰退检测
- FAANG careers 页面爬虫(Playwright)
- 更多数据源

### Week 3(Apr 30 - May 6)· Dashboard

- Next.js 前端
- 趋势图表(Recharts,Next.js/React 原生集成最顺)
- 自定义技能栈 vs 市场契合度视图
- Vercel 部署

### Week 4(May 7-14)· 改写为多 agent 架构

- 用 LangGraph StateGraph 重构 pipeline
- Scraper / Extractor / Normalizer / Reporter 四个 agent
- 加入 Supervisor 模式编排
- LangSmith 追踪

### Week 5(May 15-21)· MCP 集成 + 稳定性收尾

- 暴露 MCP server(`src/mcp_server.py`),Claude Desktop 可以直接问"这周最火的技能是什么"。初始 tool set:
  - `get_top_skills(date_range, category?, top_n)` — 某时间窗口 Top N 技能
  - `get_skill_trend(skill, granularity)` — 日/周/月趋势
  - `compare_companies(company_a, company_b)` — 两家公司要求差异
  - `list_new_skills(since_date)` — 新出现的技能
  - `match_stack(stack_yaml_path)` — 自定义技能栈 vs 市场契合度
- 稳定性 checklist:AWS Bedrock fallback(Anthropic API 宕机时切换)、SQLite 自动备份到 GitHub Release、LangSmith 监控报错阈值

### Week 6+(后续迭代)

- Dashboard 打磨、性能优化
- 更多数据源(LinkedIn 第三方 API、猎头聚合站)
- 博客 / 技术复盘文章

---

## 6. 成功标准(KPI)

项目不是"跑通就算完",需要可量化的验收标准:

| 维度 | 指标 | 目标 | 测量方式 |
|---|---|---|---|
| 抽取质量 | required_skills 准确率(P/R/F1) | F1 ≥ 0.85 | 人工标注 50 个 JD 做 golden set,每两周 re-eval |
| 归一化质量 | canonical 归并准确率 | ≥ 95% 人工抽查无误 | `review_queue` 中误判率 < 5% |
| 管道稳定性 | 连续无故障运行天数 | ≥ 30 天 | GitHub Actions 成功率 |
| 覆盖度 | 每日入库岗位数(去重后) | ≥ 100 | `jobs_raw` 日增量 |
| 成本 | 月实际支出 | ≤ $20 | Anthropic console + OpenAI dashboard |
| Dashboard | p95 首屏加载时间 | < 2s | Vercel analytics |

---

## 7. Risk 与应对

| 风险 | 影响 | 应对 |
|---|---|---|
| Greenhouse/Lever/Ashby API 格式变更 | 管道静默失败 | 每个 source 模块写 schema 校验;抽取字段缺失超阈值时 CI 告警 |
| LLM 抽取质量漂移(新模型版本) | 下游统计失真 | 固定模型版本号(`claude-haiku-4-5-20251001`);每月跑一次 golden set eval |
| API 限流 / 超时 | 当日数据丢失 | 指数退避重试;失败任务写 `dead_letter` 队列,次日自动重跑 |
| 成本超预期 | 月支出失控 | GitHub Actions 里加 token usage budget,日预算超 $1 即停止后续抽取 |
| 数据合规(存储 full JD 可能触及版权/ToS) | repo 被投诉 | 默认只存 JD **摘要 + 抽取字段**,不存 full_description 到公开 repo;本地副本留全文做调试 |
| LinkedIn 第三方 API 限制 | Week 3+ 阻塞 | 降级到仅用 ATS 三件套(Greenhouse/Lever/Ashby),文档中声明"LinkedIn 为 stretch goal" |
| 单人维护、时间不足 | 进度落后 | 路线图以 Week 1 MVP 为硬目标,Dashboard / 多 agent 重构为软目标可延后 |

---

## 8. 关键决策记录(ADR)

| # | 决策 | 理由 |
|---|---|---|
| 1 | 用 Haiku 4.5 不用 Opus | 成本差 10×,抽取任务简单够用 |
| 2 | SQLite 不用 Postgres | 数据量小,跟 repo 走,零运维 |
| 3 | 先 Greenhouse/Lever/Ashby,LinkedIn 后置 | 80% 覆盖,零反爬成本 |
| 4 | Canonical taxonomy 手动 + LLM 辅助,不全自动 | 质量比覆盖率重要,避免垃圾进垃圾出 |
| 5 | 归一化用 cosine similarity + numpy 直算,不引入 FAISS/Pinecone | taxonomy 规模 <500,复杂化无收益 |
| 6 | 抽取 schema 固定 Claude 模型版本号 | 防止模型升级导致下游统计漂移 |
| 7 | 公开 repo 不存 full_description,只存摘要 + 抽取字段 | 规避版权 / ATS ToS 风险 |

---

## 9. 下一步

按优先级推进:

1. **先建 repo 骨架**:按 Week 1 周一清单
2. **跑通最小闭环**:一家公司 → Greenhouse API → Haiku 抽取 → SQLite → Markdown,端到端
3. **再扩展**:更多数据源、归一化、多 agent、dashboard

---

*Last updated: 2026-04-16*
