# 域 4：工具与 MCP 生态

> 研究子代理：tools-mcp ｜ 回写：`research/ai-capability-upgrade/findings/04-tools-mcp.md`
> 来源标注：〔web〕= 本轮 WebSearch/WebFetch 核实（2025-2026）；〔知识〕= 既有知识、未本轮逐条联网核实（按保守口径陈述，已尽量只用确有其物的协议/框架/论文）。
> 边界：本域聚焦 **Agent 与外部世界的"接口层"**——工具调用机制、MCP 协议与生态、工具设计、工具选择/工具 RAG、沙箱代码执行、computer-use/浏览器、工具安全与缓存。推理范式（CodeAct/ReAct 的"思维"角度）见域 1；代理↔代理 A2A 协议与编排见域 2；RAG 检索基建见域 5；工具结果缓存的记忆/上下文角度见域 6；评估/可观测（OTel GenAI、tool eval）见域 9；通用注入/护栏/最小权限见域 10；模型/语义缓存与成本见域 12。本域只取这些主题的**工具·接口角度**并交叉引用。

---

## 领域概述

「工具与 MCP」是 Agent 的"手脚与神经接口"——决定它能调用什么、调得准不准、贵不贵、安不安全。2025-2026 的范式跃迁有四条主线：①**协议标准化**：MCP（Anthropic 2024-11）成为"模型↔工具的 USB-C 口"事实标准，2025 完成 stdio→Streamable HTTP 传输升级、强制远程 OAuth 2.1、并在 2025-09 上线**官方 Registry**（registry.modelcontextprotocol.io）+ GitHub/各客户端子注册表，工具从"手工配置"走向"可发现、可发布、可治理"。②**工具设计成为一门工程**：Anthropic《Writing tools for agents》（2025-09）确立"工具是确定性系统与非确定性 Agent 之间的契约"，给出选对工具/命名空间/返回高信噪上下文/token 高效/描述即提示词/**用 Agent 评估并自优化工具**等原则。③**"工具太多"成为新瓶颈**：几百上千个工具定义塞进上下文会"提示膨胀"，解法分两路——**工具 RAG**（RAG-MCP：按查询语义检索 top-k 工具，准确率 3×、token 砍半）与**代码执行式 MCP**（Anthropic 2025-11：把 MCP server 暴露成文件系统里的代码 API，Agent 写代码按需加载工具、在沙箱内处理中间数据，单场景 token 从 15 万降到 2 千，-98.7%）。④**执行面扩张**：沙箱代码执行（E2B/Firecracker、gVisor）、computer-use（Claude/OpenAI 视觉操作）与浏览器工具（Playwright MCP 走无障碍树、非像素）让 Agent 从"调 API"扩展到"用电脑"。与之伴生的是**安全黑暗面**：工具投毒（tool poisoning）、rug pull（批准后偷改工具）、跨工具编排注入成为 MCP 头号客户端风险。

对「产品专家 Agent」尤其关键：它是典型的 **MCP 消费方**——靠 firecrawl/app-insight/小红书/微博/B站/antv-chart 等 MCP + 连接器（AgentShield/nano-banana-pro/last30days/DeerFlow·MediaCrawler）干活，且已有一套成熟的"连接器纪律"（按需安装 + 不可用降级 + 人工降级清单）、`doctor` 状态字典、`summary.md` 工具透明化、`/安全扫描` 配置面治理。但它**只会"用工具"，不会"造工具/选工具/安全地跑代码"**：缺自建 MCP（工具创作）、缺多工具时的工具选择/工具 RAG、缺沙箱代码执行（多步工具操作仍逐个 JSON 调）、工具错误处理是 research 专用而非跨能力通用规范、MCP 运行时投毒/rug-pull 防护尚未显式化。本域要回答的就是：**从"MCP 消费方"走向"会造工具 + 会选工具 + 会安全执行"的具体路线。**

---

## SOTA 技术目录

> 按子类分组，共 **77 条**（9 子类）。成熟度口径：`事实标准`（行业默认/已成规范）、`成熟`（生产广泛使用）、`成长`（活跃、生产可用但仍演进）、`实验`（论文/原型/preview）。

### A. MCP 协议与规范（"模型↔工具"纵向标准）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| MCP（Model Context Protocol） | 开放协议，JSON-RPC 2.0，标准化 LLM 应用接外部工具/数据（"AI 的 USB-C 口"） | 给单 Agent 接工具/数据源、想跨客户端复用 | 事实标准 | Anthropic 2024-11；本仓库已是消费方 | 〔web〕 |
| Host / Client / Server 三角 | Host=LLM 应用发起连接；Client=Host 内连接器（1:1 接一个 server）；Server=提供能力 | 理解 MCP 架构与信任边界 | 事实标准 | Claude Desktop/Cursor=Host；mcps/ 下各 server | 〔web〕 |
| Server 三原语：Tools | 模型可执行的函数（model-controlled）：`tools/list` + `tools/call` | 执行动作、取实时数据 | 事实标准 | 所有 MCP server | 〔web〕 |
| Server 三原语：Resources | 只读数据源（application-controlled，类 GET、无副作用）：`resources/list` + `resources/read` | 注入只读上下文（文件/DB 记录） | 事实标准 | filesystem server 等 | 〔web〕 |
| Server 三原语：Prompts | 预定义模板/工作流（user-controlled）：`prompts/list` + `prompts/get` | 把"最优用法"沉淀成可选模板 | 成熟 | slash-command 式 prompt | 〔web〕 |
| Client 能力：Sampling | server 反向请求一次 LLM 补全（`sampling/createMessage`），实现 server 端 agentic 行为 | server 需要"借用"模型推理 | 成长 | 支持的 Host 较少，正扩散 | 〔web〕 |
| Client 能力：Roots | server 询问可操作的 URI/文件系统边界 | 限定 server 作用域 | 成长 | 文件类 server | 〔web〕 |
| Client 能力：Elicitation | server 运行中向用户索要结构化补充输入 | 缺参数时按需补问 | 成长（新） | 2025 规范新增 | 〔web〕 |
| 传输：stdio | 本地子进程，stdin/stdout 收发换行分隔 JSON-RPC | 本地工具/脚本（同机） | 事实标准 | Playwright MCP、本地 server | 〔web〕 |
| 传输：Streamable HTTP | 远程单端点 POST + 可选 SSE 流，多客户端，替代旧 HTTP+SSE（2024-11-05） | 远程托管 server、多并发 | 成熟 | 2025-03-26 起标准 | 〔web〕 |
| 能力协商 + 有状态会话 | 连接初始化时双方声明 capabilities，按连接维护会话 | 客户端/服务端按需启用特性 | 事实标准 | 所有合规实现 | 〔web〕 |
| Tool Annotations | 工具元数据标注读/写、是否破坏性、是否 open-world | 让客户端/Agent 区分安全 vs 危险操作 | 成长 | 2025 规范；披露 destructive | 〔web〕 |
| MCP Authorization / OAuth 2.1 | 远程 HTTP server 强制 OAuth 2.1 鉴权框架；stdio 走环境变量凭据 | 远程 server 授权、企业接入 | 成长 | 2025-03-26 规范要求 | 〔web〕 |
| 规范版本化 | 规范按日期版本演进（2024-11-05→2025-03-26→2025-06-18→2025-11-25），TypeScript schema 为唯一真源 | 跟踪 breaking change、对齐客户端 | 事实标准 | schema.ts / 自动生成 JSON Schema | 〔web〕 |

### B. MCP 生态：注册表 / 分发 / 打包

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 官方 MCP Registry | 开放目录 + API，server 发布一次、各客户端/市场共享同一权威数据 | 发现/发布公开 MCP server | 成长（preview，2025-09-08） | registry.modelcontextprotocol.io；`server.json`；`mcp-publisher` CLI | 〔web〕 |
| 子注册表 / 市场（federated） | 各客户端在官方上游之上做"有观点的市场"（增补/筛选/排序） | 面向特定用户群的精选分发 | 成长 | GitHub MCP Registry（2025-09-16）、PulseMCP、Goose | 〔web〕 |
| `server.json` 标准 | 描述 server 身份/包/运行时/元数据的标准格式 + DNS/HTTP 域名验证 | 统一发布与命名（`com.anthropic/...`） | 成长 | MCP Registry spec | 〔web〕 |
| DXT（Desktop Extension） | 把本地 MCP server 打成桌面扩展，一键装进 Claude Desktop | 本地工具分发给非开发者 | 成长 | Claude Desktop Extensions | 〔web〕 |
| 本地 MCP server 原型化 | `claude mcp add ...` 或 DXT 接进 Claude Code/Desktop 测自建工具 | 自建工具的最快验证环 | 成熟 | Claude Code / Desktop | 〔web〕 |
| MCP Gateway / Agentgateway | 在 Agent 与多 server 间加网关：schema 校验、鉴权、限流、可观测、deny-list | 企业级多 server 治理与安全 | 成长 | Solo.io Agentgateway（入 LF）、各家 gateway | 〔web〕 |

### C. Function/Tool Calling 机制（API 层）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| Function/Tool Calling | 模型产结构化工具调用→应用执行→回灌结果（`name`+`description`+参数 schema） | 任何要 Agent 调外部能力的场景 | 事实标准 | OpenAI `parameters` / Anthropic `input_schema` | 〔web〕 |
| `tool_choice` 控制 | 强制工具选择：auto / required(any) / 指定某工具 / none | 需要逼模型必调或必不调某工具 | 事实标准 | OpenAI/Anthropic 均支持 | 〔web〕 |
| 并行工具调用 | 一轮内同时发多个独立工具调用，降延迟 | 子任务相互独立、可并行取数 | 成熟 | `parallel_tool_calls`；Claude 4 默认强 | 〔web〕 |
| 并行结果回灌格式 | 多个 tool_result 必须放在**同一条 user 消息**里，否则"教会"模型放弃并行 | 维持并行能力、避免退化 | 成熟（易错点） | Anthropic 明确该坑 | 〔web〕 |
| Strict mode / 受限解码 | `strict:true` 用语法约束采样，保证工具入参严格符合 JSON Schema | 要可靠 schema 一致、避免类型错（`"2"`→`2`） | 成熟 | OpenAI structured outputs；Claude grammar-constrained | 〔web〕 |
| Strict 的 schema 约束 | strict 要求 `additionalProperties:false` 且所有字段 `required` | 设计入参 schema 时遵守 | 成熟 | OpenAI 文档 | 〔web〕 |
| 原生结构化输出 | 不经工具包裹，直接 `output_format`/`response_format` 出 JSON Schema 结果 | 只要结构化产物、不需副作用 | 成熟 | OpenAI Structured Outputs；Claude output_format | 〔web〕 |
| 工具错误回传（is_error） | 工具失败时返回 `is_error:true` + 可读错误，模型自行恢复重试 | 让 Agent 优雅处理失败而非崩 | 成熟 | Anthropic tool_result | 〔web〕 |

### D. 工具设计最佳实践（Anthropic《Writing tools for agents》2025-09）

| 技术/原则 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 工具是"契约"非 API 包装 | 工具是确定性系统↔非确定性 Agent 的契约，要为 Agent 工效设计，不是给开发者的 API | 一切自建工具的心法 | 成长（权威指南） | Anthropic 同文 | 〔web〕 |
| 选高杠杆工具，少即是多 | 别给每个 API 端点都包工具；建少而精、贴合真实工作流的工具 | 决定造哪些/不造哪些工具 | 成长 | `search_contacts` 优于 `list_contacts` | 〔web〕 |
| 工具整合多步工作流 | 一个工具内部完成常被串起来的多步（找空档+建会）减少往返与中间 token | 高频链式操作 | 成长 | `schedule_event`、`get_customer_context` | 〔web〕 |
| 命名空间（namespacing） | 按服务/资源前后缀分组（`asana_search`/`asana_projects_search`）划清边界 | 工具多、易混淆时 | 成长 | MCP 客户端默认前缀；前/后缀有实测差异 | 〔web〕 |
| 返回高信噪上下文 | 只回对下游有用的信息，用自然语言名而非 UUID/mime 等低层标识符 | 减少幻觉、提升检索精度 | 成长 | name/image_url 优于 uuid | 〔web〕 |
| `response_format` 枚举 | 暴露 concise/detailed 让 Agent 自控返回详尽度（类 GraphQL 选字段） | 同工具既要省 token 又要可取 ID | 成长 | concise 省 ~⅔ token | 〔web〕 |
| token 高效：分页/过滤/截断 | 默认对大响应分页、范围选择、过滤、截断（Claude Code 默认上限 25k token） | 任何可能吐大量数据的工具 | 成长 | 25k 截断 + 引导更小搜索 | 〔web〕 |
| 有用的错误返回 | 错误信息要可操作（提示正确入参/用过滤），不给 traceback/错误码 | 让 Agent 自纠而非卡死 | 成长 | 校验失败给示例 | 〔web〕 |
| 描述即提示词 | 工具 description/spec 被载入上下文，是最有效的优化点（小改动大增益） | 提升工具调用准确率 | 成长 | Sonnet 3.5 借此刷 SWE-bench | 〔web〕 |
| 响应结构（XML/JSON/MD）影响表现 | 无万能格式，结构按各自 eval 选 | 调优工具产物格式 | 成长 | 取决于任务/模型 | 〔web〕 |
| 评估驱动 + Agent 自优化工具 | 建真实多步 eval（含数十次工具调用），让 Claude Code 读 transcript 自动改工具 | 系统化提升工具质量 | 成长 | Anthropic tool evaluation cookbook | 〔web〕 |

### E. 多工具下的工具选择 / 工具 RAG（"工具太多"解法）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| 提示膨胀问题 | 全量工具定义塞进上下文 → token 爆、相似工具难区分、选择准确率随工具数骤降 | 工具 > 几十个时的根因 | 成长（共识） | RAG-MCP/Tool RAG 论证 | 〔web〕 |
| RAG-MCP | 把工具描述存向量库，按查询语义检索 top-k 工具再注入上下文 | 大工具集、想省 token+提准 | 实验→成长 | arXiv 2505.03275：准确率 13%→43%，prompt token 砍半 | 〔web〕 |
| Tool RAG（通用范式） | 像知识 RAG 一样从大工具注册表只检索最相关工具 | 企业级几百上千工具 | 成长 | Red Hat 2025-11 综述；AWS Bedrock KB | 〔web〕 |
| Tool2vec / Toolshed / 查询改写 | 嵌入"示例查询"而非工具描述、重写用户请求、重排检索结果等增量改进 | 进一步提升工具检索召回 | 实验 | Tool2vec、Toolshed、Amazon 研究 | 〔web〕 |
| 渐进式工具发现 | Agent 先列目录、按需读取单个工具定义，只加载当前需要的工具 | 工具多、想"懒加载" | 成长 | Anthropic code-execution 文件系统式 | 〔web〕 |
| 动态/分层工具加载 | 运行时按上下文加载工具子集；超大集做嵌套/层级检索 | 工具集规模随业务增长 | 成长 | RAG-MCP 后续工作 | 〔web〕 |
| ToolLLM / ToolBench | 16k+ 真实 API 数据集 + DFSDT 决策树搜索训练工具使用 | 训练/评测多工具调用能力 | 成长（学术经典） | ToolLLM (2023/24) | 〔知识〕 |
| Gorilla / API 检索 | LLM + 文档检索器调用海量 ML API，减少幻觉调用 | API 海量、需检索接地 | 成长（学术经典） | Gorilla / APIBench、OpenFunctions | 〔web〕 |

### F. 代码执行 / 沙箱（CodeAct 的工程面，交叉域 1）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| CodeAct（代码即动作） | 用可执行代码当统一动作空间替代逐个 JSON 工具调用（推理角度见域 1） | 多步/批量/带逻辑的工具编排 | 成长（快速上升） | CodeActAgent；MS Agent Framework | 〔web〕 |
| Code execution with MCP | 把 MCP server 暴露成文件系统代码 API，Agent 写 TS 代码调用、在运行时处理中间数据 | 工具多、中间数据大、要省 token | 实验→成长（2025-11） | Anthropic：15 万→2 千 token（-98.7%） | 〔web〕 |
| E2B（Firecracker microVM） | 开源云沙箱，跑 AI 生成代码，硬件级隔离 + 代码解释器（Jupyter） | 安全跑不可信生成代码、数据处理 | 成熟 | e2b-code-interpreter SDK；Perplexity/Manus 用 | 〔web〕 |
| Modal / Daytona | gVisor 等隔离的云沙箱，按需弹性、GPU 可选 | 大规模/需 GPU 的代码执行 | 成熟 | Modal（gVisor）、Daytona | 〔web〕 |
| Sandcastle（MCP 原生沙箱） | `execute_code` 作为 MCP 工具，三档隔离（namespaces/gVisor/Firecracker）、默认断网 | 想直接给任意 MCP Agent 加沙箱 | 实验 | github sandcastle | 〔web〕 |
| 内置 Code Interpreter | 模型厂商内置的沙箱代码执行工具（数据分析/绘图） | 简单数据计算/图表、不想自建 | 成熟 | OpenAI/Claude code interpreter | 〔web〕 |
| 隔离分级 | 进程隔离(namespaces+seccomp+cgroups) < gVisor(系统调用拦截) < Firecracker/KVM(硬件级) | 按代码可信度选隔离强度 | 成熟 | Sandcastle 三档；网络 allowlist | 〔web〕 |
| 沙箱治理要件 | 默认断网 + 域名白名单 + 资源/超时限制 + 自动清理 + 暂停/恢复保态 | 安全跑代码的最小护栏 | 成长 | E2B/Sandcastle | 〔web〕 |

### G. computer-use / 浏览器 / GUI（执行面扩张，模型角度见域 1）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| Claude Computer Use | VLM 看截图、输出鼠标/键盘动作操作 GUI（视觉派） | 无 API 的 GUI/canvas 应用 | 成长 | Anthropic 2024+ | 〔web〕 |
| OpenAI computer-use（CUA/Operator） | Computer-Using Agent，浏览器/桌面里替你操作（视觉派） | Web 任务、表单、信息获取 | 成长 | computer-use-preview 模型 | 〔web〕 |
| Playwright MCP | 官方浏览器 MCP，走**无障碍树(accessibility tree)而非像素**，40+ 工具，每快照 ~200-400 token | 确定性 Web 自动化、抓取、测试、填表 | 成熟（DOM 派首选） | microsoft/playwright-mcp；Cursor/Claude 等可用 | 〔web〕 |
| Chrome DevTools MCP | 基于 CDP 的浏览器 MCP（DOM/性能/网络/运行时） | 需性能/网络/DOM 深检 | 成长 | 本仓库的 `cursor-ide-browser` 即 CDP 式 | 〔web〕 |
| browser-use | 开源浏览器 Agent 库（DOM + 视觉混合） | 自建浏览器 Agent | 成长 | browser-use | 〔知识〕 |
| 视觉派 vs DOM 派 | 视觉：通用但不确定、贵；DOM：确定/省 token，但依赖可访问的 DOM | 选浏览器工具路线 | 成长（共识） | MCP.Directory 对比 | 〔web〕 |
| GUI agent 原生模型 | 端到端 GUI 操作模型（多轮 RL），OSWorld 等 SOTA（详见域 1） | 强 GUI 接地、长程操作 | 成长 | UI-TARS/UI-TARS-2 | 〔web〕 |

### H. MCP 安全（工具投毒/越权，交叉域 10）

| 风险/防御 | 一句话 | 何时警惕 | 成熟度 | 代表实现/证据 | 来源 |
|---|---|---|---|---|---|
| 工具投毒（Tool Poisoning, TPA） | 恶意指令藏进工具描述/参数/响应，进上下文被当可信输入执行（间接注入） | 接第三方/可配置 MCP server | 成长（头号客户端风险） | Invariant Labs；OWASP；影响 Cursor/Zapier 等 | 〔web〕 |
| Rug pull（批准后偷改） | server 在用户批准后悄改工具描述/行为，绕过初次审查 | 远程/托管 MCP server | 成长 | Invariant/Elastic/Microsoft 均列 | 〔web〕 |
| 运行时信任缺口 | 工具描述连接时审一次，但工具**响应**直进上下文无等价校验——攻击点 | 任何不校验工具响应的 Agent | 成长（根因） | OWASP MCP_Tool_Poisoning | 〔web〕 |
| 跨工具编排注入 / 名字碰撞 / 影子 / 被动影响 | 用多工具/跨 server 串联攻击；伪装成可信工具名诱导误用 | 多 server 混用、内外工具同权限 | 成长 | Elastic Security Labs | 〔web〕 |
| STRIDE/DREAD 威胁建模 | 对 Host+Client/LLM/Server/数据存储/授权 5 组件系统建模 | 设计/评审 MCP 接入安全 | 实验→成长 | arXiv 2603.22489 | 〔web〕 |
| 防御：响应当不可信数据 + 净化 | 工具响应不直接当指令；进上下文前校验/净化/隔离 | 所有外部工具响应 | 成长 | Microsoft Prompt Shields | 〔web〕 |
| 防御：最小权限 + 内外工具隔权 | 外部 server 响应不应能触发受信内部工具；后端强制权限非靠模型自觉 | 有特权工具(文件/DB)又接外部 server | 成长 | OWASP 建议 | 〔web〕 |
| 防御：固定/校验完整性 + 人审敏感操作 | 工具定义打 hash/pin、网关 schema 校验、破坏性操作要人确认 | 防 rug pull / 越权 | 成长 | MCP Gateway + 哈希校验 | 〔web〕 |

### I. 工具结果缓存 / 版本化 / 可观测（交叉域 6、9、12）

| 技术/能力 | 一句话 | 何时用 | 成熟度 | 代表实现 | 来源 |
|---|---|---|---|---|---|
| Prompt caching（前缀 KV 缓存） | 缓存静态前缀（系统提示/工具 schema），命中跳过重算，省成本降延迟 | 工具 schema/系统提示稳定且大 | 成熟 | OpenAI（自动，省≤90% 输入/≤80% 延迟）；Claude/Gemini | 〔web〕 |
| 工具结果缓存 | 按"工具名+入参"键缓存工具输出（带 TTL/失效），避免重复昂贵调用 | 同参数昂贵调用（搜索/查库）重复 | 成长 | 需自管 TTL 与状态一致性 | 〔web〕 |
| 语义缓存 | 对近似查询命中缓存（嵌入相似度） | 高重复近似请求 | 成长 | 详见域 12 | 〔web〕 |
| 工具版本化 | 工具/server 按语义版本演进，注册表记版本（`versions`） | 工具升级不破坏既有调用 | 成长 | MCP Registry versions | 〔web〕 |
| 工具可观测（OTel GenAI） | 记录工具调用次数/耗时/token/错误率作为遥测维度 | 诊断工具瓶颈、优化 | 成长 | OpenTelemetry GenAI（详见域 9） | 〔web〕 |
| BFCL（工具调用基准） | Berkeley Function Calling Leaderboard，用 AST 评 serial/parallel/多轮工具调用 | 选模型/评工具调用能力 | 事实标准（评测） | gorilla.cs.berkeley.edu，BFCL V4 | 〔web〕 |
| A2A vs MCP（互补） | MCP=纵向(Agent↔工具)；A2A=横向(Agent↔Agent)；2025 统一 AAIF 治理（详见域 2） | 区分工具接入 vs 代理协作 | 成长 | Google A2A→LF；AAIF（2025-12） | 〔web〕 |

---

## 2025-2026 前沿与趋势

1. **MCP 从"协议"长成"生态"。**〔web〕 2025 完成传输升级（stdio + Streamable HTTP 取代 HTTP+SSE）、强制远程 OAuth 2.1、上线**官方 Registry**（2025-09-08，`server.json` + `mcp-publisher`）+ GitHub 等子注册表；并入 LF AAIF（2025-12）与 A2A 统一治理。工具从"手配 JSON"走向"可发现、可发布、可版本化、可治理"。
2. **"工具太多"成为头号扩展瓶颈，两条解法定型。**〔web〕 ①**工具 RAG**（RAG-MCP：检索 top-k 工具，准确率 13%→43%、token 砍半）；②**代码执行式 MCP**（Anthropic 2025-11：MCP server 当文件系统代码 API，渐进式按需加载 + 沙箱内处理中间数据，单场景 -98.7% token）。趋势是"不要把所有工具定义塞进上下文"。
3. **工具设计成为显式工程学科。**〔web〕 Anthropic《Writing tools for agents》把"选对工具/整合工作流/命名空间/高信噪返回/response_format/分页截断/描述即提示词"系统化，并提出**用 Agent 读 eval transcript 自动优化工具**——"评估驱动 + Agent 自改工具"成为新范式（与本仓库 `/经验写回` 同频）。
4. **CodeAct 与"代码执行"成为多工具编排的省钱主力。**〔web〕 用可执行代码当动作空间，比逐个 JSON 调省轮次/token、天然支持批量与并行、可自调试；催生 E2B/Firecracker、gVisor、Sandcastle(MCP 原生沙箱) 等"安全跑代码"基建（交叉域 1）。
5. **浏览器/computer-use 分化为"视觉派 vs DOM 派"。**〔web〕 视觉派（Claude/OpenAI computer-use）通用但不确定、贵；DOM 派（Playwright MCP 走无障碍树，每快照仅 ~200-400 token）确定、省 token，成为 Web 自动化首选；端到端 GUI 原生模型（UI-TARS-2）在 OSWorld 等领先（交叉域 1）。
6. **MCP 安全黑暗面浮出水面。**〔web〕 工具投毒（指令藏在工具元数据/响应）、rug pull（批准后偷改）、跨工具编排注入成为头号客户端风险；根因是"连接时审描述、运行时不校验响应"的信任缺口。防御走向：网关 schema 校验 + 工具定义 hash/pin + 内外工具隔权 + 响应当不可信数据净化 + 敏感操作人审。
7. **强约束工具调用成为可靠性底线。**〔web〕 strict mode / 受限解码（grammar-constrained sampling）保证入参严格符合 schema（`"2"`→`2`）；并行工具调用 + 正确的结果回灌格式（同一 user 消息）成为降延迟标配；`tool_choice` 强制选择用于关键路径。
8. **三层缓存成为工具型 Agent 的成本基建。**〔web〕 prompt 缓存（静态前缀含工具 schema，省≤90% 输入）+ 工具结果缓存（按名+参，带 TTL）+ 语义缓存（近似查询）分层叠加；工具 schema 越稳定，缓存收益越大（交叉域 6、12）。
9. **工具调用进入"可评测"时代。**〔web〕 BFCL（AST 评 serial/parallel/多轮）成事实标准基准；模型差距从"单轮能调"转向"多轮、记忆、长程工具决策"——评工具能力要看 agentic 多步，不只单次。
10. **"自建工具"门槛骤降、Agent 参与造工具。**〔web〕 MCP SDK + DXT + Claude Code 让"一次性原型工具"成常态；Anthropic 提倡 build→eval→iterate 且让 Agent 自己读 transcript 改工具——"会用工具"的 Agent 正在变成"会造并自优化工具"的 Agent。

---

## 对标产品专家 Agent

> 核心命题：从 **"MCP 消费方"** → **"会造工具（自建 MCP）+ 会选工具（工具 RAG）+ 会安全执行（沙箱）"**。下表逐项给"现状→差距→增强(P0/P1/P2)"。
> 注：产品专家已有的强项要先认清——**连接器纪律**（按需安装+不可用降级+人工降级清单，见 `image-prompt-connector.md`/`agent-security-scan.md`）、**`doctor` 状态字典**与 **`summary.md` 工具透明化**（见 `research-toolkit/protocols/tooling-and-installation.md`）、**`/安全扫描` 配置面治理**、**契约测试纪律**。增强应"复用并泛化这些已有资产"，而非另起炉灶。

| 我们现状 | 差距 | 建议增强（P0/P1/P2） |
|---|---|---|
| 是 MCP 消费方（firecrawl/app-insight/小红书/微博/B站/antv-chart）+ 连接器，工具透明化与降级做得好 | **工具设计/使用最佳实践未成文**：Anthropic"选高杠杆工具/命名空间/高信噪返回/response_format/分页截断/描述即提示词"未沉淀为跨能力规范，仅散落在各 skill | **P0**：新增 `policies/tool-use-protocol.md` 通用工具使用规范（五能力共用），把 Anthropic 工具设计原则 + 工具选择 + 错误处理 + token 高效编成显式条款 |
| `tooling-and-installation.md` 有 `doctor` 状态字典 + `summary.md` 必填"用了什么工具/为何降级/盲区"——这是**优秀的工具错误处理雏形** | 该规范**绑死在 research 能力**：SQL/策划/AI策划/Demo 的工具调用没有统一的"首选→降级→透明记录"错误处理回路 | **P0**：把 research 的 `doctor`/降级/透明记录**泛化**为 `tool-use-protocol.md` 的"工具错误处理 + 降级 + 透明化"通用条款，五能力统一引用 |
| `/安全扫描`（AgentShield）扫**配置面**（密钥/权限/注入/风险 MCP/Hook）| 缺 **MCP 运行时安全**：工具投毒/rug-pull/跨工具注入/"工具响应当可信输入"的防护未显式化；第三方/新增 MCP 无信任分级 | **P0**：扩 `agent-security-scan.md` 增"MCP 运行时风险"小节——第三方 MCP 信任分级、工具响应当不可信数据、敏感/破坏性操作人审、新增 server 入库前校验 |
| 工具数量可控（~6 MCP + 几个连接器），按平台硬编码路由（`tooling-and-installation.md` 第 5 节） | 无**工具选择/工具 RAG**层：现在够用，但连接器/skill 持续增多后，"全量塞上下文"会提示膨胀、选择退化；也无"按需加载工具"机制 | **P1**：先做"工具选择"轻量版——`tool-use-protocol.md` 写命名空间 + "何时用哪个工具"决策表 + 渐进式披露（按任务只加载相关工具）；工具数破阈值再上 Tool-RAG-lite（索引工具描述检索） |
| 是消费方，靠 `npx skills i` 接外部 skill/连接器；`agent-team-methodology` 第二、三部分有**技能编写方法论** | **不会"造工具"**：无"何时自建 MCP/工具 vs 消费 vs 写 skill"的判据，也无自建 MCP 的 build→eval→iterate 流程 | **P1**：新增 `policies/mcp-tool-authoring.md`（或 `skills/` 下 builder skill）——给"造/买/降级"判据 + 自建 MCP 流程（原型→契约测试→eval→连接器化），接入 `/经验写回` |
| 工具调用是逐个 JSON 式、顺序执行；`aibi-query`/`research` 已能跑脚本 | 无 **CodeAct/沙箱代码执行**：多平台采集汇总、SQL+图表流水线逐个调，轮次/token 高、无并行、无安全隔离 | **P1/P2**：在 `aibi-query`/`research-toolkit` 引入 **CodeAct-lite**（能一段脚本完成的多步工具操作就写脚本）；中远期接沙箱（E2B/受管 venv）按 `code-execution with MCP` 模式（交叉域 1 P2-1） |
| 工具结果一次性用，无缓存；任务内可能重复采集 | 无**工具结果缓存 / prompt 缓存**意识：同参数昂贵调用（搜索/查库/采集）重复跑，浪费 token 与时间 | **P2**：在 `tool-use-protocol.md` 写"工具结果缓存"约定（任务内按"工具名+参数"缓存到 `tasks/{task}/.cache/`，带 TTL）；工具 schema 稳定前缀利于 prompt 缓存（交叉域 6/12） |
| 已有 `cursor-ide-browser`（CDP 式浏览器 MCP）+ research 的浏览器链路 | 浏览器工具**未成体系**：视觉 vs DOM 取舍、Playwright MCP 这类确定性/省 token 链路未纳入，深层交互靠单一 MCP | **P2**：在 `tool-use-protocol.md` 记浏览器工具选型（DOM 派 Playwright MCP 优先于截图视觉派，省 token、确定性强），与 `cursor-ide-browser` 现状对齐、按需补 Playwright MCP |
| 无工具调用质量基准；契约测试是"存在性 + 标记 + 触发词" | 工具/连接器质量无**量化 eval**（调用准确率/token/错误率），无 BFCL 式视角 | **P2**：写回自建工具时，按 `agent-team-methodology` 第三部分补"工具 eval"（真实多步任务 + 调用准确率/token/错误率），北极星=Anthropic"Agent 自读 transcript 改工具"（交叉域 9） |

---

## 落地建议

> 原则：**复用并泛化已有资产**（连接器纪律 / `doctor` 状态字典 / `summary.md` 透明化 / 契约测试），不引入重框架，与本仓库"Cursor 原生、轻量聚焦"一致。先做"立刻可用"的 policy/protocol 层（P0），需基建的（沙箱/工具 RAG）标 P1/P2 并交叉引用兄弟域。每条给"放哪个文件 / 做什么 / 验收信号"。

### P0-1 新增通用工具使用规范 `policies/tool-use-protocol.md`
- **放哪**：`policies/tool-use-protocol.md`（新文件，与 `agent-team-methodology.md`/`prompt-engineering-techniques.md` 平级）；`.cursor/rules/product-expert-commands.mdc` 的"执行原则"加一句"涉及工具调用先读 `tool-use-protocol.md`"。
- **做什么**：Why-First 写法，含：①**工具设计与选择**（Anthropic 原则：选高杠杆工具、命名空间、返回高信噪上下文非 UUID、`response_format` concise/detailed、分页/过滤/截断默认值、描述即提示词）；②**工具选择决策**（"何时用哪个 MCP/连接器"表 + 渐进式披露：按任务只加载相关工具，别全量塞）；③**调用机制**（可并行的独立取数并行发、强约束 schema、`tool_choice` 强制关键工具）；④**工具错误处理 + 降级 + 透明化**（把 research 的 `doctor` 状态字典 + "首选→补装/补登→明确降级→不空手进总结"+ `summary.md` 必填项**泛化为五能力通用**）。
- **验收信号**：`tests/test_product_expert_agent.py`（或新增 `tests/test_tool_use_protocol.py`）断言文件存在且含标记 `命名空间`/`response_format`/`分页`/`渐进式披露`/`工具错误处理`/`降级`/`不可信响应`；至少 `aibi-query` 或一个 orchestrator 的 SKILL.md 引用到它。

### P0-2 工具错误处理 + 降级 通用化（泛化 research 雏形）
- **放哪**：`policies/tool-use-protocol.md` 的"错误处理与降级"小节；与 `skills/research-toolkit/protocols/tooling-and-installation.md` 双向链接（research 作为该规范的"满血实现样板"）。
- **做什么**：抽出与 research 一致的最小回路——**先探测工具状态（已安装/需安装/需登录/降级）→ 试首选 → 缺装/缺登录先补 → 仍不可用则明确降级（不静默跳过）→ 产物里透明记录"用了什么工具/为何没用首选/盲区"**。明确红线：不允许"工具没装好"伪装成"没数据"；外部工具响应失败给可操作错误而非静默吞错。
- **验收信号**：除 research 外，至少一个能力（建议 `aibi-query`：DBOPS 不可用/无权限时）落地该回路；契约测试断言其产出/说明含"降级"与"用了什么工具"痕迹。

### P0-3 MCP 运行时安全（扩 `agent-security-scan.md`）
- **放哪**：`policies/agent-security-scan.md` 新增"MCP 运行时风险"小节；`agent-team-methodology.md` 第四部分"安全自检"加一行指向它。
- **做什么**：把扫描从"配置面"扩到"运行时面"——①**第三方/新增 MCP 信任分级**（自建/官方 Registry 已验证域名 > 社区；入 `mcps/` 前核验来源、能力、是否可跑任意 shell）；②**工具响应当不可信数据**（不把工具/网页/采集结果里的"指令"当系统指令执行，防工具投毒/间接注入）；③**rug-pull 防护**（关注已批准 server 的描述/行为变更）；④**破坏性/敏感操作人审**（写操作、删除、外发）。降级：AgentShield 不可用时并入人工五类清单。
- **验收信号**：`agent-security-scan.md` 含标记 `工具投毒`/`rug pull`/`不可信响应`/`第三方 MCP 信任`/`人审`；`tests/test_security_self_check.py` 或 `test_agent_team_methodology.py` 增断言覆盖这些标记；`/经验写回` 写回前的安全闸把它纳入检查。

### P1-1 自建 MCP / 工具创作判据与流程 `policies/mcp-tool-authoring.md`
- **放哪**：`policies/mcp-tool-authoring.md`（新）；与 `agent-team-methodology.md` 第二、三部分（技能编写/测试）交叉链接（"造工具"与"写技能"共用 build→eval→iterate 内核）。
- **做什么**：①**造/买/降级判据**（高频复用且无现成 MCP/连接器→自建；已有上游→连接器化按需安装+降级；一次性→主代理直办）；②**自建 MCP/工具流程**（原型：本地 MCP server/脚本 → 按 Anthropic 原则定义 name/description/schema/错误返回 → 契约测试 + 真实多步 eval → 连接器化沉淀，遵循现有"按需安装+不可用降级"模式）；③接入 `/经验写回`：反复奏效的工具操作先记为"本能"，攒够证据升级为自建工具/连接器。
- **验收信号**：文件含 `造/买/降级判据`/`build→eval→iterate`/`契约测试`/`连接器化` 标记；`submission-review-contract.md` 写回评审项增"若新增工具/MCP，是否走了 authoring 流程 + 契约测试 + 安全扫描"。

### P1-2 工具选择 / 渐进式披露（轻量版，为工具 RAG 铺路）
- **放哪**：`policies/tool-use-protocol.md` 的"工具选择"小节；`tooling-and-installation.md` 第 5 节（平台工具优先级）升级为"带命名空间 + 何时用"的显式表。
- **做什么**：现在工具可控，先做**命名空间 + "何时用哪个工具"决策表 + 渐进式披露**（按任务类型只加载相关工具/连接器，不一次性全列）。写明"工具数破阈值（如 > 20）时升级为 Tool-RAG-lite：把工具/连接器/skill 的 description 建轻量索引，按查询检索 top-k 再用"（引 RAG-MCP，交叉域 5 检索基建）。
- **验收信号**：决策表覆盖现有全部 MCP/连接器且每条有"何时用/何时别用/降级路径"；规范含 `渐进式披露` 与 `Tool-RAG-lite` 触发阈值说明。

### P1-3 CodeAct-lite：脚本优先的多步工具操作（交叉域 1 P2-1）
- **放哪**：`skills/aibi-query/SKILL.md` 与 `skills/research-toolkit/`（已能跑脚本处）的 protocol；规范条款写进 `tool-use-protocol.md`。
- **做什么**：指引"**能用一段脚本完成的多步/批量工具操作（多平台采集汇总、SQL+图表流水线）就写脚本，别逐个 JSON 调**"；在受管 venv/脚本里执行 + 自调试；无脚本环境时降级为现有逐步调用。中远期对接沙箱（E2B/受管隔离）按 Anthropic `code execution with MCP` 模式（按需加载工具 + 运行时处理中间数据，省 token）。
- **验收信号**：至少一条数据/采集流水线改为脚本化并在 `tests/test_pipeline_smoke.py` 类测试中可跑；规范含"脚本优先/沙箱降级"说明。

### P2-1 工具结果缓存约定
- **放哪**：`policies/tool-use-protocol.md` 的"缓存"小节；产物落 `tasks/{task}/.cache/`。
- **做什么**：任务内对**昂贵且同参数**的工具调用（搜索/查库/采集）按"工具名+入参 hash"缓存结果，带 TTL（如采集类当日有效），命中直接复用并标注"来自缓存"。说明工具 schema/系统提示放前缀利于厂商 **prompt 缓存**（交叉域 6/12）。
- **验收信号**：规范含 `工具结果缓存`/`TTL`/`prompt 缓存前缀` 标记；至少一处采集/查询流程支持"二次相同请求走缓存"并在 `summary.md` 标注。

### P2-2 浏览器工具选型对齐 + 自建工具 eval（北极星）
- **放哪**：`tool-use-protocol.md` 浏览器小节；自建工具 eval 并入 `mcp-tool-authoring.md` + `agent-team-methodology` 第三部分。
- **做什么**：①浏览器：DOM 派（Playwright MCP，无障碍树、省 token、确定性）优先于截图视觉派，与现有 `cursor-ide-browser` 对齐、按需补 Playwright MCP；②自建工具质量：写回工具/连接器时补"真实多步任务 eval（调用准确率/token/错误率）"，远期试 Anthropic"让 Agent 读 eval transcript 自动改工具"（交叉域 9 提供 eval/judge 基建）。
- **验收信号**：规范含浏览器选型表（DOM vs 视觉 + 何时用）；自建工具写回 PR 模板要求附"工具 eval 指标"。

---

## 参考来源

- 〔web〕Model Context Protocol 规范（primitives/transports/lifecycle/auth）— modelcontextprotocol.io/specification/2025-03-26（transports、basic）；最新 2025-11-25 版 modelcontextprotocol.org/specification/2025-11-25；MCP Cheat Sheet（webfuse.com/mcp-cheat-sheet）；philschmid.de/mcp-introduction（Tools/Resources/Prompts + OAuth 2.1 + Streamable HTTP）。
- 〔web〕官方 MCP Registry（preview，2025-09-08）— blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview ；modelcontextprotocol.info/tools/registry（`server.json`、`/v0/servers`、`mcp-publisher`）；InfoQ / socket.dev 报道；GitHub MCP Registry（github.blog/changelog 2025-09-16）。
- 〔web〕Anthropic《Writing effective tools for agents—with agents》(2025-09-11) — anthropic.com/engineering/writing-tools-for-agents（选工具/命名空间/高信噪返回/response_format/25k 截断/描述即提示词/eval 自优化）；MCP 教程版 modelcontextprotocol.info/docs/tutorials/writing-effective-tools；《Building agents with the Claude Agent SDK》anthropic.com/engineering/building-agents-with-the-claude-agent-sdk。
- 〔web〕Anthropic《Code execution with MCP》(2025-11) — anthropic.com/engineering/code-execution-with-mcp（文件系统式 MCP 代码 API、渐进式工具发现、15 万→2 千 token / -98.7%）；MarkTechPost / kiadev.net 报道。
- 〔web〕RAG-MCP《Mitigating Prompt Bloat in LLM Tool Selection via RAG》— arxiv.org/html/2505.03275（top-k 工具检索，准确率 13%→43%，prompt token 砍半）；WRITER engineering/rag-mcp；Red Hat《Tool RAG》next.redhat.com/2025/11/26（Tool2vec/Toolshed/Amazon）；github memoverflow/rag-mcp。
- 〔web〕Function/Tool Calling 机制 — developers.openai.com/api/docs/guides/function-calling（strict/`additionalProperties:false`/`parallel_tool_calls`/`tool_choice`）；platform.claude.com/docs（strict tool use 语法约束采样；parallel tool use 同一 user 消息回灌；input_schema）；OpenAI Structured Outputs cookbook。
- 〔web〕沙箱代码执行 — e2b.dev / github e2b-dev/code-interpreter（Firecracker microVM、code-interpreter SDK）；Modal《Best Code Execution Sandboxes 2026》modal.com/resources（gVisor vs Firecracker）；github pruthvirajdgit/sandcastle（MCP 原生沙箱、三档隔离、默认断网）。
- 〔web〕浏览器 / computer-use — playwright.dev/mcp + github microsoft/playwright-mcp（无障碍树、40+ 工具、~200-400 token/快照）；mcp.directory/blog/playwright-browser-mcp-guide-2026（视觉派 vs DOM 派）；Claude Computer Use；OpenAI computer-use-preview（CUA/Operator）。〔知识〕browser-use。
- 〔web〕MCP 安全 — OWASP www-community/pages/attacks/MCP_Tool_Poisoning ；Invariant Labs《Tool Poisoning Attacks》(rug pull)；Microsoft《Protecting against indirect prompt injection in MCP》(Prompt Shields)；Elastic Security Labs《MCP Tools: Attack Vectors and Defense》(跨工具编排/名字碰撞/影子/被动影响)；arXiv 2603.22489（STRIDE/DREAD 威胁建模）。
- 〔web〕缓存与评测 — developers.openai.com/api/docs/guides/prompt-caching（前缀 KV、省≤90% 输入/≤80% 延迟、工具与 schema 可缓存）；BFCL gorilla.cs.berkeley.edu/leaderboard（AST 评 serial/parallel/多轮，`pip install bfcl-eval`）；patil2025bfcl (ICML 2025)。
- 〔知识〕ToolLLM/ToolBench（16k API + DFSDT）、Gorilla/APIBench（API 检索调用）——未本轮逐条联网核实，按学术经典保守口径。
- 交叉引用：CodeAct/computer-use 模型（域 1）；A2A/MCP/AAIF 协议与编排（域 2）；RAG 检索基建（域 5）；工具结果缓存的记忆/上下文角度（域 6）；OTel GenAI/工具 eval（域 9）；通用注入/护栏/最小权限（域 10）；prompt/语义缓存与模型路由成本（域 12）。
