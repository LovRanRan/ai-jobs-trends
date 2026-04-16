# AI Jobs Trends Tracker · 进度追踪

> 与 `ai-jobs-trends-project-brief.md` 配套。brief 是**做什么/为什么**,progress 是**做到哪了**。
>
> **更新纪律**
> - Daily Log:每个开发日结束前写一条
> - Weekly Retro:每周日晚写一次
> - Decision Log:做任何**对未来有影响的**技术/范围决策当场写
> - Blocker Log:卡住 > 2 小时写,解决后补 resolution
> - 里程碑完成当天更新 Dashboard 的进度条和 KPI

---

## 📊 Dashboard

### 整体进度

```
里程碑: [░░░░░░░░░░░░░░░░░░░░] 0% · 0/9
Week:   Week 1 / Week 5+
```

| 项 | 值 |
|---|---|
| 启动日 | 2026-04-16 |
| 当前 Week | Week 1(Apr 16-22) |
| 本周状态 | 🟡 进行中(周一 M1) |
| 下一 deadline | **Apr 22 周五** — M4 daily markdown 端到端闭环 |
| 累计开发时长 | 0 h |
| 当前月成本 | $0 / 预算 $20 |

### 里程碑进度(9 个 checkpoint)

| ID | 里程碑 | 状态 | 完成日 |
|---|---|---|---|
| M1 | 项目骨架 | 🟡 | — |
| M2 | ATS 三源 ingestion | ⬜ | — |
| M3 | Haiku 抽取闭环 | ⬜ | — |
| M4 | Daily markdown 报告 | ⬜ | — |
| M5 | 归一化系统 | ⬜ | — |
| M6 | 周/月报 + 趋势检测 | ⬜ | — |
| M7 | Dashboard MVP | ⬜ | — |
| M8 | LangGraph 多 agent | ⬜ | — |
| M9 | MCP + 稳定性 | ⬜ | — |

状态符号:⬜ 未开始 · 🟡 进行中 · 🟢 已完成 · 🔴 blocked · ⏸ 暂缓

### KPI 快照(每周日更新)

| 指标 | 目标 | 最新 | 上周 | 趋势 |
|---|---|---|---|---|
| 抽取 F1(required_skills) | ≥ 0.85 | — | — | — |
| 归一化准确率 | ≥ 95% | — | — | — |
| 连续无故障运行天数 | ≥ 30 | 0 | — | — |
| 每日入库岗位数(去重后) | ≥ 100 | — | — | — |
| 月实际支出 | ≤ $20 | $0 | $0 | — |
| Dashboard p95 首屏 | < 2s | — | — | — |

### 本周 Top 3 聚焦(每周一更新)

1. _(待填)_
2. _(待填)_
3. _(待填)_

### 最近 5 天

- 2026-04-16 · project brief 优化 + progress.md 建立
- 2026-04-15 · —
- 2026-04-14 · —
- 2026-04-13 · —
- 2026-04-12 · —

---

## 🎯 里程碑验收标准(M1-M9)

| # | 里程碑 | 验收标准(必须全部满足才算完成) |
|---|---|---|
| M1 | 项目骨架 | repo + CI 空跑 ✅ + SQLite schema 就绪 + `uv sync` 干净安装 |
| M2 | ATS 三源 ingestion | 20+ 家公司每日自动入库 `jobs_raw`,连续 3 天无错误,重复率 < 5% |
| M3 | Haiku 抽取闭环 | 每日新 JD 经 Haiku 抽取后落 `skill_mentions`,抽查 10 条 schema 合法 |
| M4 | Daily markdown 报告 | `digests/daily/YYYY-MM-DD.md` 自动 commit,内容包含所有模板字段 |
| M5 | 归一化系统 | canonical taxonomy + embedding 相似度归并 + review queue 流程跑通 |
| M6 | 周/月报 + 趋势检测 | rolling 统计、新兴/衰退技能检测,误报抽样 < 20% |
| M7 | Dashboard MVP | Vercel 部署,3 个核心视图可用,p95 首屏 < 2s |
| M8 | LangGraph 多 agent | pipeline 重构成 StateGraph,LangSmith 能看到完整 trace |
| M9 | MCP + 稳定性 | 5 个 tool 可用,Bedrock fallback 测试过,连续运行 ≥ 7 天无故障 |

---

## 📋 任务清单(按 Week 展开)

### Week 1(Apr 16-22)· 数据管道跑通 → M1 + M2 + M3 + M4

#### 周一(Apr 16)— 项目骨架 → M1
- [ ] 建 GitHub repo `ai-jobs-trends`(README + LICENSE + .gitignore)
- [ ] Python 环境:`uv init`,装 `anthropic`, `sqlalchemy`, `httpx`, `pyyaml`, `rapidfuzz`, `numpy`
- [ ] 写 `.github/workflows/daily-run.yml` 空架子(cron: `0 20 * * *` UTC)
- [ ] 把 Anthropic / OpenAI API key 加到 GitHub Secrets
- [ ] `src/storage/models.py`:`jobs_raw` + `skill_mentions` 两张表
- [ ] `data/jobs.sqlite` 初始化
- [ ] CI 空跑一次绿灯 ✅

#### 周二(Apr 17)— Greenhouse ingestion → M2 进度 1/3
- [ ] `src/sources/greenhouse.py`:`fetch_jobs(company_slug) -> list[Job]`
- [ ] `config/companies.yaml`:Anthropic, Scale AI, Databricks, Airbnb, Figma, Notion, Stripe, Ramp, Vanta, +1
- [ ] `Job` dataclass 字段对齐 schema
- [ ] 主键:`sha1(company + external_id)[:16]`
- [ ] 跑一次,`jobs_raw` 应有 200-500 行
- [ ] 肉眼检查 5 条:字段完整、无 HTML 乱码

#### 周三(Apr 18)— Lever + Ashby + Dedup → M2 完成
- [ ] `src/sources/lever.py`
- [ ] `src/sources/ashby.py`
- [ ] `companies.yaml` 扩到 20+ 家
- [ ] `src/sources/dedup.py`:一级 hash + 二级 RapidFuzz ≥ 92
- [ ] 三源合并跑,重复率 < 5%
- [ ] 每源公司数 / JD 数写到 `digests/daily/`

#### 周四(Apr 19)— Haiku 抽取 → M3
- [ ] `src/extraction/schemas.py`:brief §3 的 JSON Schema
- [ ] `src/extraction/extractor.py`:`extract(job) -> ExtractedSkills`,Haiku tool use
- [ ] 固定模型版本:`claude-haiku-4-5-20251001`
- [ ] Prompt 加 3-shot:required vs nice-to-have
- [ ] 抽 50 条,肉眼 review 10 条,问题写 `notes/extraction-review.md`
- [ ] 落库 `skill_mentions`(先不归一化,原始字符串)

#### 周五(Apr 20)— Daily markdown 报告 → M4
- [ ] `src/reporter/daily.py`
- [ ] 模板字段:
  - [ ] 今日新增 / 去重后 / 按公司分布
  - [ ] Top 10 提及技能(全部 + is_required 限定)
  - [ ] 今日新出现的 skill
  - [ ] is_agent_role=true 的岗位清单
- [ ] GitHub Actions `git commit -m "daily: YYYY-MM-DD"` 回 main
- [ ] 连跑 2 天验证

#### 周末(Apr 21-22)— 打磨 + LangGraph 预研
- [ ] README 补完:动机、架构图、如何本地跑、如何接入新公司
- [ ] Excalidraw / Mermaid 架构图放 README
- [ ] LangGraph quickstart + State + Graph 核心概念
- [ ] `notes/langgraph-plan.md`:Week 4 改造方案草稿

---

### Week 2(Apr 27 - May 3)· 聚合和扩展 → M5 + M6

#### 归一化系统(M5)
- [ ] `data/taxonomy.yaml` 初版:~50 canonical + alias
- [ ] `src/normalization/embedder.py`:`text-embedding-3-small` 封装 + `data/taxonomy_embeddings.npy` 缓存
- [ ] `src/normalization/taxonomy.py`:`match(term) -> (canonical, confidence)`,三档阈值
- [ ] `data/review_queue.yaml`:0.70-0.85 自动入队
- [ ] 历史数据重跑归一化
- [ ] 第一批 review_queue 手动 review

#### 趋势检测(M6)
- [ ] `src/reporter/weekly.py` + `monthly.py`:滚动窗口
- [ ] 新兴:本周 ≥ 3 次 + 上周 0 次 → 标红
- [ ] 衰退:上周 Top 20 但本周跌出 Top 50
- [ ] GitHub Actions 加 `0 20 * * 0` 每周日触发

#### 扩展数据源
- [ ] `src/sources/faang_meta.py`(Playwright)
- [ ] `src/sources/faang_amazon.py`

---

### Week 3(May 4-10)· Dashboard → M7

- [ ] `apps/web/` Next.js 初始化
- [ ] Turso 开通,SQLite 同步
- [ ] API route:`/api/skills/top`, `/api/skills/trend/:skill`, `/api/companies/compare`
- [ ] 技能趋势折线图(Recharts,日/周/月切换)
- [ ] 新兴 vs 衰退 Top 10
- [ ] 公司画像对比(select 两家 → 条形图)
- [ ] 自定义技能栈雷达图(读 `config/my_stack.yaml`)
- [ ] Vercel 部署,p95 < 2s 验证

---

### Week 4(May 11-17)· 多 agent 架构重构 → M8

- [ ] `uv add langgraph langsmith`
- [ ] `src/agents/state.py`:`PipelineState`(TypedDict)
- [ ] 4 个 agent node:scraper / extractor / normalizer / reporter
- [ ] `src/agents/graph.py`:StateGraph + Supervisor(条件路由)
- [ ] LangSmith 项目接入,查 trace
- [ ] daily run 切 StateGraph 版本,linear pipeline fallback 保留 7 天

---

### Week 5(May 18-24)· MCP server + 稳定性 → M9

- [ ] `src/mcp_server.py`
- [ ] Tool 实现:`get_top_skills` / `get_skill_trend` / `compare_companies` / `list_new_skills` / `match_stack`
- [ ] Claude Desktop 配置本地 MCP
- [ ] 每个 tool 手动验证
- [ ] Bedrock fallback:Anthropic 5xx 时切 `anthropic-bedrock`
- [ ] SQLite 每周打包 → GitHub Release(`gh release create`)
- [ ] LangSmith alert:抽取失败率 > 10% 发邮件
- [ ] 连续 7 天无故障验证

---

### Week 6+ · 后续迭代(软目标)

- [ ] LinkedIn 第三方 API(RapidAPI JSearch / Bright Data)
- [ ] Dashboard 打磨:搜索、收藏、分享链接
- [ ] 博客 / 技术复盘文章
- [ ] Golden set 扩到 200 条,F1 re-eval

---

## 📝 Logs

所有 log 使用下面的**固定模板**,复制到对应 section 的顶部填写(最新在上)。

### A. Daily Log(每个开发日)

**模板** — 复制下面代码块:

```
### YYYY-MM-DD(Week N · 周X)
- **状态**:🟢 on-track / 🟡 slow / 🔴 blocked
- **今日完成**:task1, task2, task3
- **里程碑进展**:M2 60% → 80% / M3 ⬜ → 🟡
- **明日计划**:task1, task2
- **耗时**:X 小时
- **卡点**:无 / 具体问题(严重就开 Blocker Log 条目)
- **commit**:`abc1234`, `def5678`
```

**历史**(最新在上):

---

#### 2026-04-16(Week 1 · 周四)
- **状态**:🟢 on-track
- **今日完成**:project brief v1 初稿 → 13 处优化(成本/schema/KPI/Risk/归一化参数等) + progress.md v1 建立 + Dashboard/Logs 结构化
- **里程碑进展**:M1 ⬜(未开启,周一启动)
- **明日计划**:休整 / 可选读 LangGraph quickstart
- **耗时**:~3 h(规划)
- **卡点**:无
- **commit**:n/a(本地)

---

### B. Weekly Retro(每周日晚)

**模板**:

```
### Week N Retro(Apr X - Apr Y)
- **完成里程碑**:M1 ✅ M2 ✅(相对计划的差距:+1d / -0d / …)
- **KPI 变化**:入库岗位 30→180/日,抽取 F1 实测 0.82(离 0.85 差 0.03)
- **What went well**:… 
- **What didn't**:…
- **根因 + 下周怎么改**:…
- **下周 Top 3**:
  1. …
  2. …
  3. …
- **累计耗时**:X h · 累计成本:$Y
```

**历史**(最新在上):

_(暂无,Week 1 周日 Apr 26 填写第一条)_

---

### C. Decision Log(任何对未来有影响的决策)

> 决策写在 brief 的 ADR 是"最终沉淀版",这里记录**决策发生时**的上下文、选项、权衡,后续回头看才有意义。

**模板**:

```
### D-00N · YYYY-MM-DD · 决策标题
- **上下文**:当时遇到什么问题 / 为什么要做这个决策
- **选项**:A vs B vs C(每个选项 1 句利弊)
- **决定**:选 X
- **理由**:为什么选 X,哪些假设支撑这个选择
- **回滚信号**:什么情况会推翻这个决定(具体指标或现象)
```

**历史**(最新在上):

---

#### D-001 · 2026-04-16 · 归一化用 cosine + numpy 直算,不引入 FAISS
- **上下文**:设计归一化系统时考虑是否需要专用向量库
- **选项**:
  - A. FAISS 本地:快,但多一个依赖,< 500 词规模是 overkill
  - B. Pinecone 远程:托管省心但引入网络延迟 + 月费
  - C. numpy 矩阵乘:一行代码,无依赖
- **决定**:C
- **理由**:taxonomy 规模 < 500,内积算一次 < 1ms;复杂度应匹配数据规模
- **回滚信号**:taxonomy > 5000 词 或 归一化成为管道延迟瓶颈

---

#### D-002 · 2026-04-16 · 公开 repo 不存 full_description
- **上下文**:合规性考量,full JD 存公开 repo 可能触及版权 / ATS ToS
- **选项**:
  - A. 存 full → 最灵活,重新抽取不用重爬
  - B. 只存摘要 + 抽取字段 → 合规,但重新抽取要重爬
  - C. full 存本地 sqlite(.gitignore),公开 repo 只存抽取结果
- **决定**:C
- **理由**:兼顾合规和调试方便
- **回滚信号**:Greenhouse/Lever ToS 明确允许转载(目前未见)

---

### D. Blocker Log(卡住 > 2h)

**模板**:

```
### B-00N · YYYY-MM-DD · 标题
- **阻塞**:具体问题描述
- **尝试过**:按时间顺序列尝试的方法(哪怕失败也写)
- **状态**:🟡 in progress / 🟢 resolved / ⏸ 绕过
- **解决方案**:(resolved 时填)
- **耗时**:X h
- **预防**:下次怎么避免
```

**历史**(最新在上):

_(暂无)_

---

### E. Change Log(计划 / 架构变更)

> 路线图变了、技术选型改了、里程碑删增了 → 都记在这里。防止后来忘了"为什么改"。

**模板**:

```
### YYYY-MM-DD · 变更标题
- **原计划**:
- **变更为**:
- **原因**:
- **影响**:哪些 task / 里程碑 / KPI 被动
- **关联决策**:D-00N(可选)
```

**历史**(最新在上):

---

#### 2026-04-16 · progress.md 结构化为 Dashboard + Logs
- **原计划**:单一进度日志
- **变更为**:Dashboard(顶部状态) + 5 类 Logs(Daily / Weekly / Decision / Blocker / Change)
- **原因**:需要"固定格式"做纪律性记录,事后回溯才能找到信息
- **影响**:每日记录开销略增(~5 min),但项目复盘、面试讲故事、回答"为什么这么决策" 时直接可用
- **关联决策**:无

---

*Last updated: 2026-04-16*
