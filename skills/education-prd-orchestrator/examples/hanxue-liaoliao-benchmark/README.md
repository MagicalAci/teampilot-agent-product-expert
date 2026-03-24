# 和韩雪聊聊教育 Repo Benchmark

这是这个 skill 在当前项目里的基准案例。

它用于说明高标准成品长什么样，但它依赖当前仓库中的真实产物路径，因此属于 repo 参考 benchmark，不是独立分发版的唯一可运行样本。

## 适用目的

用来说明一份“证据驱动、章节化、带总览图”的产品文档应该长什么样。

## 对应真实产物

- 主文档：`docs/workspaces/product/prd/hanxue-liaoliao-education-v0.1.md`
- 产品索引：`docs/workspaces/product/INDEX.md`
- 流程总览图：`docs/workspaces/product/prd/images/hanxue-liaoliao-education/dual-end-flow-overview.png`
- 功能架构图：`docs/workspaces/product/prd/images/hanxue-liaoliao-education/product-function-architecture-mindmap.png`

如果你是在独立 zip skill 场景里使用这个 skill，把这里看成“质量参考”，不要把这些路径当作必须存在的默认前提。

## 这个案例回答了什么

1. 如何先冻结产品定义，再写章节
2. 如何把客服聊天、知识库、现状截图纳入证据链
3. 如何把双端关系写清楚，而不是写成功能拼接
4. 如何在第三章和第五章补总领层图
5. 如何同步版本、工作日志和索引

## 推荐观察路径

先看：

1. `第三章 产品定义与双端关系`
2. `第五章 核心功能定义`
3. 两张总览图
4. `docs/workspaces/product/INDEX.md` 中对应的版本记录

再回看：

1. 第一章和第二章如何用证据支撑判断
2. 第四章如何收口 V1 范围

## 推荐触发方式

### 启动新工作

```markdown
/产品策划 和韩雪聊聊教育
目标：整理成完整 PRD，并补总览流程图和功能架构图。
```

### 校验已有工作

```markdown
/产品策划校验 和韩雪聊聊教育
检查当前 PRD 是否缺总领层、图文口径是否一致、版本与交付说明是否同步。
```

## 这个 benchmark 的标准

- 先证据，后判断
- 先定义，后章节
- 先总领，后细节
- 图和文使用同一口径
- 文档、图片、索引版本同步
