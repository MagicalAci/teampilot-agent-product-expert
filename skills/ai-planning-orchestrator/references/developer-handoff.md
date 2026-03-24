# 开发交接说明

这份文档回答一个问题：`/AI脚本` 或 `/AI策划` 走到交接开发时，除了源码，还必须补哪些材料，才能让别人真正接得住。

## 1. 交接物不是只有代码

开发交接至少包含 4 类内容：

1. 核心脚本
2. 输入 / 输出样例
3. 测试报告
4. README / 调用文档

如果缺第 4 类，通常不算"可交接"。

## 2. README / 调用文档必须写什么

至少写清：

- 入口文件在哪
- 需要哪些配置项
- 用什么命令本地验证
- CLI 怎么调
- HTTP / route 怎么调
- 输入样例和输出样例分别在哪
- 当前已知限制是什么
- 哪些能力仍需目标项目补

推荐直接基于 `assets/developer-readme-template.md` 填。

## 3. 脚本包清单必须写什么

至少写清：

- 哪些文件被打进 zip
- 哪些文件是"直接可复用"
- 哪些文件只是样例 / 参考实现
- 哪些能力这次没有打进包

推荐直接基于 `assets/script-bundle-manifest-template.md` 填。

## 4. 调用方式文档的最低标准

### CLI / Demo

至少要有：

- 命令本体
- 输入路径
- 输出路径
- 适用场景

### HTTP / Route

至少要有：

- 请求方法
- 请求路径
- headers
- body 样例
- 响应样例
- 错误 / 超时 / 降级说明

如果当前项目只有 CLI 没有 HTTP，就明确写"当前未提供 HTTP 接入"。

## 5. 建议复用的脚本

- `scripts/init_ai_planning_delivery.py`
  - 初始化 PRD、测试报告、README、清单
- `scripts/validate_ai_planning_assets.py`
  - 校验关键章节和文件是否齐全
- `scripts/package_ai_script_bundle.py`
  - 打 zip
- `scripts/export_svg_to_png.js`
  - 导图导出

## 6. 停止条件

以下情况必须停下来，不要继续打包：

- 还没有稳定的 AI PRD 或字段合同
- README / 调用文档还没补
- 测试报告还没产出
- 输入样例和输出样例还没对齐
- 代码、文档、测试三套口径还没统一
