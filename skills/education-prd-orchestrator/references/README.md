# References 索引

这里放的是 `education-prd-orchestrator` 的规则层材料。

它们不是案例，也不是脚本，而是"这个 skill 怎么编排、怎么判断、怎么停下来问用户、怎么审"的基线文档。

## 推荐阅读顺序

1. `sop.md`
2. `orchestration-rules.md`
3. `agent-map.md`
4. `user-checkpoints.md`
5. `prompt-rules.md`
6. `review-criteria.md`
7. `evidence-rules.md`
8. `html-design-rules.md`
9. `visualization-protocol.md`
10. `package-scope.md`
11. `developer-handoff.md`

## 方法论知识库

`methodology/` 目录下放产品方法论参考文件，按需阅读：

1. `methodology/user-persona.md` — 用户画像方法论
2. `methodology/user-story.md` — 用户故事方法论
3. `methodology/user-journey.md` — 用户旅程图方法论
4. `methodology/pain-point-abstraction.md` — 核心痛点抽象方法论
5. `methodology/solution-ideation.md` — 方案构思方法论
6. `methodology/hypothesis-validation.md` — 核心假设方法论
7. `methodology/feature-prioritization.md` — 功能列表与优先级方法论

## 文件作用

- `sop.md`
  - 产品策划工作的标准执行顺序（完整 14 步链路）
- `orchestration-rules.md`
  - 主编排器的调度边界和阶段依赖
- `agent-map.md`
  - 内部全部 agent 的职责地图（evidence / persona / story / journey / pain-point / ideation / hypothesis / priority / definition / chapter / diagram / sync）
- `user-checkpoints.md`
  - 哪些情况必须停下来让用户参与（8 类检查点）
- `prompt-rules.md`
  - 所有内部 agent 共享的写作和表达约束
- `folder-structure.md`
  - skill 包结构与实际产出路径
- `review-criteria.md`
  - 最终提交文档的审核标准
- `evidence-rules.md`
  - 搜索数据、截图和原话如何成为可入稿证据
- `html-design-rules.md`
  - HTML 页面稿的最小结构、插图规则和 reviewer 检查点
- `visualization-protocol.md`
  - 流程图、功能架构图和数据图表的使用边界与输出规则
- `package-scope.md`
  - zip 打包时哪些文件必须带、哪些只适合 repo 内保留
- `developer-handoff.md`
  - 后续维护者如何新增模板、validator、fixture 和发版验证
