# 意图路由与对话管理协议（Intent Routing & Dialog）

这是产品专家 Agent 的**进门路由 + 门内对话管理**统一协议。合并两件本质相连的事：**进来一条输入怎么分类/路由/是否澄清**（意图路由）与**对话循环内怎么维护状态/填槽/确认/修复/收尾**（对话管理）——二者共用同一套澄清门禁与护栏，分开写必重复。

> 合并来源：`findings/03-intent-routing.md`（45 条）+ `findings/07-conversational-agents.md`（42 条）。能力的例句/槽位/元数据单一真源见 `policies/capability-registry.yaml`；运行时规则见 `.cursor/rules/intent-router.mdc`。

---

## 1. 三层路由

```
① 命令精确路由（现有，确定）：/深度调研、/SQL… 直接命中能力
        ↓ 未命中
② 语义/分类路由：用 capability-registry 例句做意图判定，输出 reasoning + intent + 置信度
        ↓ 置信度低 / 无匹配
③ 兜底：低置信→澄清门禁；超 5 能力范围→护栏拒答 + 替代建议
```

- 第①层保留为现状（命令名精确匹配）。
- 第②层对自然语言做**意图判定**，结构化输出 `reasoning / intent / confidence / 是否需澄清 / 是否超范围 / 命中多意图?`。
- **铁律：匹配不到就不硬猜**——无匹配返回"无 → 走兜底"比"勉强猜一个"更安全。
- 命中多意图（如"调研完做个 PRD"）→ 输出组合 **pipeline 提案**（调研→PRD→…）。

---

## 2. 置信度与护栏

- **置信度档**：高（直接开跑）/ 中（先给建议再确认）/ 低（澄清或回退 task-navigator）。
- **护栏式路由**：超出五能力范围 → 礼貌说明能力边界 + 给替代途径；五能力内但**低置信/无证据/高风险** → 降级表达或**转人工**复核（与 `agent-safety-protocol.md` HITL 闸、`self-critique-and-grounding.md` abstain 衔接）。

---

## 3. ask-or-act 澄清门禁（对话核心）

实证：LLM"知道歧义却不反问"（比人类少 3× 澄清）。所以立显式门禁：
- 按目标能力的**关键槽位**（见 `capability-registry.yaml`）检查缺失；
- **缺关键槽 → 一次性问全**（列全部缺失项集中追问，不挤牙膏）；**槽齐 → 直接开跑**；
- 判据 = **EVPI / 信息增益**："问的价值 > 打断成本"才问，否则别打断。

---

## 4. 对话状态与确认

- **对话状态**（最小 slot schema）：`{capability, known_slots, missing_slots, confirmed_slots, open_issues, confidence}`，落 `tasks/{task}/.meta/dialog-state.json`，与 `orchestration-runtime.md` 状态账本互补。
- 槽位更新用"LLM 抽取 + 确定性更新（merge/overwrite/confirm）"；用户"不，改成 X"要有显式覆盖逻辑。
- **confirmation 分级**：高风险/不可逆槽位（对外发布、写库、关键口径）**显式复述确认**；低风险隐式。
- **grounding/repair**：发现误解主动 surface（"我理解你要的是 X，对吗"）而非假设共识。
- **persona 一致性**：统一"产品专家"口吻/边界/拒答风格；长任务阶段交接处自检语气是否漂移。

---

## 5. 收尾与转人工
- 收尾产出**结构化交接简报**：`诉求 / 关键决策与理由 / 已做 / 未决项 / 证据引用 / 置信与风险`（写回与转人工复用）。
- 转人工三类话术：超范围 / 无证据低置信 / 高风险不可逆——不静默硬答。

## 6. 与本仓库接线
- `.cursor/rules/intent-router.mdc`：每轮运行时路由规则（结构化输出 + 澄清 + 护栏）。
- `task-navigator.mdc` 预检判定块：路由 + 澄清门禁 + 状态初始化。
- 多轮检索的 history-aware 查询改写（"它/那个/再深一点"补全成自洽查询）见 `retrieval-protocol.md`（P1 接入 research/aibi）。
- 可观测：每次关键路由记一行 `intent/置信度/能力/是否澄清/是否护栏` 入 `.meta/`，反哺 `/经验写回`。

## 何时查阅
- 收到一条输入怎么路由/澄清 → §1–§3
- 多轮对话维护状态/确认/收尾 → §4–§5
