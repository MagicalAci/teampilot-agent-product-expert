# AgentOps 生命周期（build → eval → ship → govern）

这是产品专家 Agent 的**自我进化生命周期总纲**——把已有的 `/经验写回`、契约测试、`/安全扫描`、`/检查Agent更新` 这些**散落的环节串成一条带准入门禁的闭环**。让"Agent 改进自己"这件事有章可循、可回归、可追溯，而不是零散地改文件。

> 细节编目见 `research/ai-capability-upgrade/findings/08-enterprise-agentops.md`。这是 SYNTHESIS §4 闭环的可执行版；评测脊椎见 `agent-trajectory-eval.md`，写回评审见 `submission-review-contract.md`。

---

## 1. 四阶段闭环 + 各阶段准入门禁

```
① build      → ② eval        → ③ ship       → ④ govern
 经验写回(增量)   契约测试+量化      PR 人审合并      安全扫描+成本+留痕
                                                    ↓ 运行时回流反哺 ①
```

| 阶段 | 做什么 | **准入门禁（不过不得进下一阶段）** |
|---|---|---|
| **build** | `/经验写回`·`/更新请求` 产出**增量 delta**（不整篇重写，防 brevity bias/context collapse）；遵循 `agent-team-methodology.md` 第二、三部分 | 改动是局部增量；Description/Why-First/渐进式披露达标 |
| **eval** | 契约测试（存在性+标记+触发词）+ **With-skill vs Baseline 量化 + pass@k**（`agent-trajectory-eval.md`） | 全量测试通过；**关键指标回归即阻断**；新增能力有契约测试 |
| **ship** | PR 人审合并；版本号/CHANGELOG 同步（`/检查Agent更新` + version-sync 规则） | 人类明确确认；版本与文档一致 |
| **govern** | `/安全扫描`（AgentShield）+ red-team 清单（`red-team-checklist.md`）+ 成本护栏（`cost-discipline-methodology.md`）+ 不可逆动作留痕 | 安全闸通过；无超预算；高风险动作有审计 |

**回归阻断**是闭环的安全阀：eval 阶段任一关键指标相对基线下降超阈值 → 阻断合并、回 build 归因。

## 2. 运行时回流（数据飞轮）
线上失败 / 踩坑 → 转 3–5 条评测用例进"失败回放"桶（`llm-eval-methodology.md`）→ 下次 build 据此改进 → eval 验证不回退。claude-mem 情景记忆 + `cost-log` + `route-log` 反哺规划（`memory-protocol.md`）。

## 3. 与本仓库接线
- `submission-review-contract.md` 的提交/评审项 = 本生命周期 ship/govern 阶段门禁的落地清单。
- `agent-team-methodology.md` 第三/四部分（技能测试 + 运维增量）= build/eval 的方法论。
- 北极星（P2）：eval 基建成熟后把 build 升级为 **ACE 式三角色（Generator/Reflector/Curator）+ 增量 delta + helpful/harmful 计数**。

## 何时查阅
- 执行 `/经验写回`、`/更新请求`、自我进化时 → 全文（走四阶段门禁）
- 判断一次改动能不能合并 → §1 各阶段门禁
