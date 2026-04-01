---
name: aibi-query
description: 星火工坊 AIBI 数据查询分析 — 自然语言提问 → 自动查询 DBOPS → 输出分析报告。支持快速版（纯聊天）和深度版（HTML看板+CSV+图表）。
version: 1.0.0
commands:
  - /SQL
  - /SQL深度
triggers:
  - 查数据
  - 看指标
  - 跑个数
  - 数据看板
  - 运营分析
  - 分析业务数据
  - 查一下数据库
review_criteria:
  - label: "Token 闭环：首次使用或 Token 过期时，必须输出完整引导文案（含权限申请链接 + F12 取 Token 步骤），不可跳过。"
  - label: "数据库匹配：根据关键词自动匹配三个线上库之一，无法判断时必须回问用户。"
  - label: "SQL 合规：所有 SQL 必须 SELECT-only、显式字段、WHERE is_delete=0。"
  - label: "输出三件套：快速版输出结论洞察+数据表+图表，深度版额外输出 HTML+CSV 文件。"
  - label: "数据表方向：汇总型用纵排，趋势型用横排（列=日期），不强制统一。"
  - label: "线上数据可用性：仅 starcard/picbook/poptoy 三个库有线上数据，其余库告知用户暂无数据。"
---

# AIBI 数据查询分析

> **入口命令：** `/SQL`
>
> **一句话：** 自然语言提问 → 自动 SQL → 查询内部数据库 → 输出分析报告（结论+数据表+图表）

**Skill 目录结构：**
```
skills/aibi-query/
├── SKILL.md                    ← 主流程（本文件）
├── scripts/
│   └── aibi-token.sh           ← Token 管理工具（save/check/show/guide）
├── references/
│   ├── 数据库全景.md            ← 3 个库 63 张表的完整结构
│   ├── 查询案例库.md            ← 11 个 PM 提问 → SQL 案例（含星卡+绘本+泡泡）
│   └── 查询规范.md              ← DBOPS API 参数 + 限制 + 最佳实践
└── templates/
    └── dashboard.html           ← 深度版 HTML 看板风格参考
```

---

## ⓪ 数据库线上状态

> **重要：只有以下 3 个库有线上数据可查，其余库暂无部署。**

| 数据库 | 业务 | 表数量 | 线上数据 | 备注 |
|--------|------|--------|----------|------|
| **sparklab_starcard** | 星卡（追星小卡鉴定 + 站姐活动电商） | 26 | ✅ 有 | PROD 有真实业务数据 |
| **sparklab_picbook** | 绘本（AI 绘本阅读硬件 + 语音合成） | 19 | ✅ 有 | PROD 有真实业务数据 |
| **sg_sparklab_poptoy** | 泡泡玩具（AI 玩偶社区 + 聊天 + IAP） | 18 | ✅ 有 | PROD 有真实业务数据 |
| sparklab_skinscan | 测肤 | 0 | ❌ 无 | 未部署，暂无表结构和数据 |
| sparklab_aidating | AI 社交 | 0 | ❌ 无 | 未部署，暂无表结构和数据 |
| calio_mvp | Calio MVP | 0 | ❌ 无 | 未部署，暂无表结构和数据 |
| sparklab_homework | 作业 | - | ❌ 不存在 | DBOPS 中未找到逻辑库记录 |
| sparklab_tellme | TellMe | - | ❌ 无实例 | 逻辑库存在但无物理源 |

**当用户查询的业务不在上面三个有数据的库中时，直接告知："该业务数据库暂未部署线上数据，目前仅支持星卡、绘本、泡泡玩具三个库的查询。"**

---

## ① 模式选择（每次启动必做）

### 两个命令入口

| 命令 | 模式 | 输出内容 | 耗时 |
|------|------|----------|------|
| **`/SQL`** + 问题 | 快速版 | 聊天内直接输出：结论 + 数据表格 + 内嵌图表，**不写任何文件** | 1-2 分钟 |
| **`/SQL深度`** + 问题 | 深度版 | 生成文件：HTML 看板 + CSV 数据表 + 聊天内图表 + 洞察 | 3-5 分钟 |

### 判断规则

1. 用户输入 `/SQL` → **强制快速版**
2. 用户输入 `/SQL深度` → **强制深度版**
3. 用户用自然语言触发（"帮我看下数据""查一下星卡"等）→ 按以下规则自动判断：
   - 含"报告""看板""HTML""文件""深度""导出"等词 → 深度版
   - 其他 → 快速版
   - 不确定时 → 问用户："需要快速版（`/SQL` 直接聊天输出）还是深度版（`/SQL深度` 生成 HTML 看板文件）？"

---

## ② Token 检查（每次查询前必做）

### 2.1 读取已保存的 Token

```bash
TOKEN_FILE="$HOME/.aibi/token"
if [ -f "$TOKEN_FILE" ]; then
  TOKEN=$(cat "$TOKEN_FILE" | tr -d '[:space:]')
  echo "TOKEN_LOADED: ${TOKEN:0:15}..."
else
  echo "TOKEN_MISSING"
fi
```

### 2.2 验证 Token 有效性

```bash
curl -s --max-time 10 \
  'https://hdbs-service-api.hellobike.cn/api/v1/db/logicDatabases?env=PROD&logicDbName=sparklab_starcard' \
  -H "Token: $(cat $HOME/.aibi/token)" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('TOKEN_VALID' if d.get('code')==200 else 'TOKEN_EXPIRED: '+str(d.get('code',''))+' '+d.get('message',''))"
```

### 2.3 Token 缺失或过期时的引导

**当 Token 不存在或验证失败时，必须原样发送以下文案给用户：**

---

> **需要你的 DBOPS SSO Token 才能查询数据**
>
> **前置条件：先申请数据库只读权限**（已有权限可跳过）
>
> 打开下面的链接，点击「申请权限」按钮，选择「只读权限」：
> - 星卡：https://dbops.hellobike.cn/?#/workspace/resource/MySQL/sparklab_starcard/1198/info
> - 绘本：https://dbops.hellobike.cn/?#/workspace/resource/MySQL/sparklab_picbook/1199/info
> - 泡泡玩具：https://dbops.hellobike.cn/?#/workspace/resource/MySQL/sg_sparklab_poptoy/1200/info
>
> 权限审批通过后，按以下步骤获取 Token（约 30 秒）：
>
> 1. 浏览器打开 **https://dbops.hellobike.cn** 并登录（公司 SSO）
> 2. 按 **F12** 打开开发者工具 → 切到 **Network（网络）** 标签
> 3. 在 DBOPS 页面**随便点一个数据库**，触发一个请求
> 4. 在 Network 列表中找到发往 `hdbs-service-api.hellobike.cn` 的任意请求
> 5. 点击该请求 → **Request Headers** → 找到 **Token** 字段
> 6. 复制整个值（包含 `bearer_` 前缀），发给我
>
> Token 格式示例：`bearer_0a65d0a1-5b3c-4f04-b415-7c8b4872d0ea`
>
> 有效期约 8 小时，过期后按相同步骤重新获取即可。
>
> 如果查询时返回「无权限」或「连接异常」，说明对应库的只读权限还未批下来，请先完成上面的权限申请。

---

### 2.4 收到 Token 后保存

```bash
mkdir -p "$HOME/.aibi"
echo "用户提供的Token" > "$HOME/.aibi/token"
chmod 600 "$HOME/.aibi/token"
echo "TOKEN_SAVED"
```

保存后**必须重新执行 2.2 验证**，确认有效才继续。

---

## ③ 意图解析与 SQL 生成

### 3.1 数据库匹配

| 关键词 | 数据库 | 业务 | 线上数据 |
|--------|--------|------|----------|
| 星卡、小卡、鉴定、站姐、明星、追星、活动 | `sparklab_starcard` | 星卡 | ✅ |
| 绘本、阅读、声纹、设备、书架、对话 | `sparklab_picbook` | 绘本 | ✅ |
| 玩偶、泡泡、社区、聊天、能量、订阅 | `sg_sparklab_poptoy` | 泡泡玩具 | ✅ |
| 测肤、社交、作业、tellme | — | — | ❌ 暂无数据 |

无法判断 → 明确问用户。匹配到无数据的库 → 告知用户暂不支持。

### 3.2 查阅表结构

**先读取 `references/数据库全景.md` 获取完整表结构。** 如需更精确的字段信息：

```bash
curl -s --max-time 15 \
  'https://hdbs-service-api.hellobike.cn/api/v1/db/dql/sqlQuery' \
  -X POST -H 'Content-Type: application/json' \
  -H "Token: $(cat $HOME/.aibi/token)" \
  -d '{
    "env":"UAT","dbName":"目标库","logicDbName":"目标库",
    "dbType":"MySQL","queryType":"PHYSICAL","unit":"HZUNIT","limit":5000,
    "sqlContent":"SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='"'"'目标库'"'"' AND TABLE_NAME='"'"'目标表'"'"' ORDER BY ORDINAL_POSITION"
  }'
```

### 3.3 指标拆解

| 类型 | 定义 | 示例 |
|------|------|------|
| **直查** | 单条 SQL 直出（COUNT/SUM/AVG/MAX/MIN） | "注册用户数""订单总额" |
| **计算** | 需两个以上直查指标做二次运算 | "转化率=买家数/注册数""客单价=GMV/订单数" |

### 3.4 SQL 编写规则

1. **显式列出字段**，禁止 `SELECT *`
2. **必须** `WHERE is_delete = 0`
3. 时间筛选用 `DATE_SUB(CURDATE(), INTERVAL N DAY)`
4. 聚合用 `GROUP BY` + `ORDER BY`
5. 不写 LIMIT（API 自动追加）
6. L3+ / S2+ 敏感字段需脱敏输出

完整 SQL 案例见 → `references/查询案例库.md`

---

## ④ 查询执行

### 4.1 API 调用

```bash
curl -s --max-time 30 \
  'https://hdbs-service-api.hellobike.cn/api/v1/db/dql/sqlQuery' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H "Token: $(cat $HOME/.aibi/token)" \
  -d '{
    "env": "UAT",
    "dbName": "库名",
    "logicDbName": "库名",
    "dbType": "MySQL",
    "sqlContent": "你的SELECT语句",
    "limit": 100,
    "queryType": "PHYSICAL",
    "unit": "HZUNIT"
  }'
```

参数详情见 → `references/查询规范.md`

### 4.2 异常处理

| 返回码 | 含义 | 自动处理 |
|--------|------|----------|
| 200 | 成功 | 继续 |
| 401 | Token 过期 | **自动触发 ② 的 Token 刷新流程** |
| 400 "非select" | SQL 不合规 | 修改 SQL 后重试 |
| 400 "连接异常" | 该库在当前环境无实例 | 尝试切换 env（UAT→PROD） |
| "无权限" / 403 | 未申请只读权限 | 引导用户前往 DBOPS 申请权限（见 ②.3） |

---

## ⑤ 输出规范

### 快速版输出（纯聊天）

**直接在聊天中依次输出以下三块，不生成任何文件：**

#### 5.1 结论与洞察（必须 3-5 条）

每条格式：
```
[等级标记] **指标名** — 指标值（计算过程）。
业务含义。**建议：具体行动。**
```

等级标记：
- ✅ 正常（≥ 基准线）
- ⚠️ 预警（基准线 50%-100%）
- 🔴 异常（< 基准线 50% 或为零）

#### 5.2 数据表格（Markdown 表格）

直接在聊天中渲染。**根据数据特征选择纵排或横排：**

**纵排（指标汇总型）** — 每行一个指标：

```markdown
| 业务维度 | 指标名称(metric) | 数值(value) | 类型(type) | 来源/公式(source) |
|---------|-----------------|------------|-----------|------------------|
| 用户 | 注册用户数(total_users) | 2 | 直查 | COUNT(*) FROM t_xxx |
| 用户 | 转化率(cvr) | 50% | 计算 | 买家数/注册数×100 |
```

**横排（时间趋势型）** — 列=日期，适用于"最近N天""按周""按月"等场景：

```markdown
| 指标 | 3/26 | 3/27 | 3/28 | 3/29 | 3/30 | 3/31 | 4/1 |
|------|------|------|------|------|------|------|-----|
| 活跃用户(DAU) | 120 | 135 | 128 | 142 | 138 | 155 | 160 |
| 阅读时长(min) | 450 | 520 | 480 | 510 | 490 | 560 | 580 |
```

**选择原则：** 单次汇总用纵排，有时间维度用横排，混合场景可以两张表。

#### 5.3 图表（聊天内嵌）

使用 `user-antv-chart` MCP 工具直接在聊天中绘制：

| 数据特征 | 图表 | MCP 工具名 |
|----------|------|-----------|
| 漏斗/转化 | 漏斗图 | `generate_funnel_chart` |
| 分类对比 | 柱状图 | `generate_bar_chart` |
| 占比分布 | 饼图 | `generate_pie_chart` |
| 时间趋势 | 折线图 | `generate_line_chart` |
| 多维评分 | 雷达图 | `generate_radar_chart` |

**至少 1 张，复杂分析 2-3 张。** 统一使用 `theme: "dark"`。

---

### 深度版输出（生成文件）

**在快速版全部输出的基础上，额外生成以下文件：**

#### 5.4 HTML 看板文件

**参考 `templates/dashboard.html` 的整体风格和 CSS 变量，但不要求照搬布局。**

保存为 `{业务名}_运营分析_{日期}.html`

**必须包含以下 5 个模块（顺序和内部布局自由）：**

| 模块 | 必须 | 说明 |
|------|------|------|
| **Header** | ✅ | 标题、数据来源库名、环境、日期、SQL/指标数量 tag |
| **KPI 卡片** | ✅ | 3-6 个核心数字，每个含标签+数值+辅助说明+计算公式 |
| **图表区** | ✅ | 2-4 张 Chart.js 图表，类型自选（环形/柱状/折线/条形/健康度条） |
| **洞察区** | ✅ | 3-5 条带等级标记（good/warn/bad/info）的洞察分析 |
| **数据表** | ✅ | 完整指标明细，表头含中文+英文 |

**数据表布局规则：**
- **纵排表（默认）**：适用于指标汇总，行=指标，列=维度/数值/类型/来源
- **横排表（时间序列）**：适用于趋势数据，行=指标，列=日期

**根据数据特征自动选择最合适的表格方向和图表类型，不要强制统一。**

#### 5.5 CSV 数据表文件

表头格式：`中文名(英文字段名或计算公式)`

保存为 `{业务名}_数据表_{日期}.csv`

---

## ⑥ 执行清单（Agent 自检用）

### 快速版 Checklist

```
□ 读取 ~/.aibi/token → 验证有效
□ 接收用户问题 → 匹配数据库（仅 starcard/picbook/poptoy 可查）
□ 读取 references/数据库全景.md → 确认表和字段
□ 拆解指标（直查 + 计算）
□ 生成 SQL → 执行 → 拿到结果
□ 二次计算（比率/均值/同比）
□ 输出结论洞察（3-5 条，带等级 + 建议）
□ 输出 Markdown 数据表（纵排或横排）
□ 调用 antv-chart MCP 绘制图表（≥1 张）
□ 全程不生成任何文件
```

### 深度版 Checklist

```
□ 快速版全部步骤
□ 读取 templates/dashboard.html 风格参考
□ 用实际数据生成 HTML（5 大模块齐全）→ 保存为 xxx_运营分析_日期.html
□ 生成 CSV 数据表 → 保存为 xxx_数据表_日期.csv
□ 告知用户文件路径
```

---

## ⑦ 数据库速查表（内嵌版）

> 完整详情见 `references/数据库全景.md`

### sparklab_starcard（星卡）— 26 表 ✅ 有线上数据

| 核心表 | 说明 | 关键字段 |
|--------|------|----------|
| t_starcard_user | 用户 | guid, user_new_id, nickname, permission(1=站姐/0=普通) |
| t_starcard_activity | 活动 | guid, user_id, activity_title, product_amount, stock_quantity, activity_status(0待审/1发布/2拒绝/3结束/4关闭) |
| t_starcard_order | 订单 | guid, order_no, user_id, seller_user_id, pay_amount, order_status |
| t_starcard_identify_task | AI鉴定 | guid, user_id, template_id, ai_result(0不通过/1通过) |
| t_starcard_star_info | 明星 | guid, star_name, category(0内娱/1韩娱/2泰娱/3欧美) |
| t_starcard_user_star_relation | 用户-明星 | user_id, star_id, is_joined, is_followed |

### sparklab_picbook（绘本）— 19 表 ✅ 有线上数据

| 核心表 | 说明 | 关键字段 |
|--------|------|----------|
| t_pic_book_user_info | 用户 | guid, nickname, user_new_id |
| t_pic_book_device_user_binding | 设备绑定 | device_id, user_id, status(1绑定/0解绑) |
| t_pic_book_reading_record | 阅读记录 | user_id, book_id, duration, progress_pct |
| t_pic_book_reading_daily_stat | 每日统计 | user_id, stat_date, total_minutes, book_count |
| t_pic_book_conversation_record | AI对话 | user_id, round_id, conversation_context |
| t_pic_book_voiceprint | 声纹 | user_id, voiceprint_type(PARENT/SYSTEM), generate_status |
| t_pic_book_user_shelf | 书架 | user_id, book_id, book_name, book_source(0=ISBN/1=上传) |
| t_pic_book_feedback | 反馈 | feedback_type(0功能/1内容/2音频/3其他), status(0-3) |

### sg_sparklab_poptoy（泡泡玩具）— 18 表 ✅ 有线上数据

| 核心表 | 说明 | 关键字段 |
|--------|------|----------|
| t_user_info | 用户 | guid, nick_name, user_new_id |
| t_account | 账户 | user_new_id, energy_num, subscribe_status |
| t_room_resident | AI玩偶 | name, voice_type, personality_type, resident_persona |
| t_chat_message | 聊天 | session_id, user_id, resident_id, content, sender_type(1=AI/2=用户) |
| t_chat_session | 会话 | user_id, resident_id, message_count |
| t_subscription_iap_record | 订阅 | user_new_id, subscription_type(1月/2年), price, currency |
| t_consumable_iap_record | 内购 | energy_count, price |

### 其他库（暂无线上数据）

sparklab_skinscan / sparklab_aidating / calio_mvp / sparklab_homework / sparklab_tellme — 均未部署或无物理实例，暂不支持查询。

### 通用表规范

所有表共有：`guid`(PK, 雪花ID) · `create_time` · `update_time` · `is_delete`(0=正常/1=删除)

---

## ⑧ 常见提问 → SQL 快速参考

> 完整案例见 `references/查询案例库.md`

**"注册用户数"** → `SELECT COUNT(*) FROM t_xxx_user WHERE is_delete=0`

**"最近7天趋势"** → `GROUP BY stat_date WHERE stat_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)`

**"TOP10热门"** → `GROUP BY xxx ORDER BY cnt DESC LIMIT 10`

**"功能渗透率"** → `COUNT(DISTINCT 功能用户) / COUNT(DISTINCT 总用户) × 100`

**"转化漏斗"** → 逐层统计每步骤人数，计算环比转化率

---

## ⑨ 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| "用户未登录或登录信息已过期" | Token 过期 | 重新执行 ② 获取新 Token |
| "当前语句非select语句" | SQL 含非 SELECT | 改为 SELECT 语句 |
| "查询数据库连接信息异常" | 该库当前 env 无实例 | 切换 env 参数 |
| "无权限" / "权限不足" / 403 | 用户未申请该库的只读权限 | 引导用户前往 DBOPS 申请权限（见 ②.3） |
| 返回空数据 | UAT 数据量少 | 切换 env=PROD 查生产数据 |
| curl 超时 | 网络或 SQL 太慢 | 加 `--max-time 60`，优化 SQL |
| HTML 图表不显示 | CDN 被拦截 | 模板已内置 fallback CDN |
