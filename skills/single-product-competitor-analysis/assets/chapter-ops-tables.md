# 配图与章节校验表格模板

这份模板服务两个文件：

- `08-visuals/VISUAL_PLAN.md`
- `07-factcheck/FACTCHECK_PLAN.md`

目标是让执行者不是“记得补图、记得校验”，而是按表推进。

## 1. `VISUAL_PLAN.md` 章节配图总表

```markdown
| 章节 | 判断点 | 是否必须有真实图 | 可用素材路径 | 应补图类型 | 推荐版式 | 图号 | 图注草案 | 插入位置 | 当前状态 |
|---|---|---|---|---|---|---|---|---|---|
| `3. 产品分析` | `双端口入口承接差异` | `是` | `04-experience/screenshots/...` | `真实截图` | `对比板` | `图 3-1 ~ 3-4` | `[待填]` | `3.1 后` | `todo / doing / done` |
| `3. 产品分析` | `首次价值路径` | `是` | `04-experience/frames/...` | `真实截图` | `路径板` | `图 3-x` | `[待填]` | `3.2 后` | `todo / doing / done` |
| `4. 用户分析` | `不同角色被不同界面承接` | `视情况` | `04-experience/screenshots/...` | `真实截图 + 结构图` | `角色板` | `图 4-x` | `[待填]` | `4.2 后` | `todo / doing / done` |
| `6. SEO 与内容分析` | `搜索承接格局` | `优先` | `03-platforms/seo/...` | `搜索页截图 / 结构图` | `路径板 / 结构图` | `图 6-x` | `[待填]` | `6.1 或 6.2 后` | `todo / doing / done` |
| `7. 商业化分析` | `认证或解锁边界` | `是` | `04-experience/screenshots/...` | `真实截图` | `节点板` | `图 7-x` | `[待填]` | `7.1 或 7.2 后` | `todo / doing / done` |
| `8. 竞争判断` | `强弱与窗口` | `否` | `08-visuals/svg/...` | `结构图` | `矩阵图` | `图 8-x` | `[待填]` | `8.1 后` | `todo / doing / done` |
```

## 2. 单章配图执行表

某一章进入配图阶段时，复制这张表单独推进：

```markdown
| 图片路径 | 图片类型 | 证明的判断 | 是否真实产品图 | 图注是否中文 | 是否已插入正文 | 备注 |
|---|---|---|---|---|---|---|
| `04-experience/screenshots/example.png` | `截图 / 抽帧 / SVG` | `[待填]` | `是 / 否` | `是 / 否` | `是 / 否` | `[待填]` |
```

## 3. `FACTCHECK_PLAN.md` 章节事实校验总表

```markdown
| 章节 | 强判断校验 | 角标校验 | 图文对应 | 图片路径校验 | 中文化校验 | 是否通过 | 问题摘要 |
|---|---|---|---|---|---|---|---|
| `2. 分析建模` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `3. 产品分析` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `4. 用户分析` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `5. 社媒分析` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `6. SEO 与内容分析` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `7. 商业化分析` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `8. 竞争判断` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `9. 对我方建议` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `1. 总结` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
| `10. 证据附录与索引` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `todo / pass / fail` | `yes / no` | `[待填]` |
```

## 4. 单章事实校验表

```markdown
| 检查项 | 结果 | 说明 |
|---|---|---|
| 强判断是否超证据 | `pass / fail` | `[待填]` |
| 是否有证据角标或明确回指 | `pass / fail` | `[待填]` |
| 图和正文判断是否一一对应 | `pass / fail` | `[待填]` |
| 图片是否来自当前任务目录 | `pass / fail` | `[待填]` |
| 图注是否中文 | `pass / fail` | `[待填]` |
| 是否仍有英文标签 / 坏图 / 无意义留白 | `pass / fail` | `[待填]` |
```
