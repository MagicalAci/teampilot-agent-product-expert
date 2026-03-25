# 章节图板模板

这份文档给 `配图 agent` 提供默认版式。

所有模板都服务一个原则：

- 真实图优先
- 一张图只证明一个判断
- 图注必须是中文
- 图注要写“证明了什么”，不是只写“这是什么页面”

## 1. 对比板

适用：

- 双端口入口对比
- 入口页 vs 首页
- 主 App vs 独立 App

```html
<table>
  <tr>
    <th align="left" width="14%">对象</th>
    <th align="center" width="22%">入口图片</th>
    <th align="center" width="22%">首页图片</th>
    <th align="left" width="42%">洞察</th>
  </tr>
  <tr>
    <td valign="top"><strong>对象 A</strong></td>
    <td align="center" valign="top">
      <img src="../04-experience/screenshots/example-a-entry.png" style="width:88%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /><br />
      <sub>图 X-1 入口页：说明入口承担什么预期</sub>
    </td>
    <td align="center" valign="top">
      <img src="../04-experience/screenshots/example-a-home.png" style="width:88%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /><br />
      <sub>图 X-2 首页：说明进入后先承接什么</sub>
    </td>
    <td valign="top">这里直接写判断，不写空说明。</td>
  </tr>
</table>
```

## 2. 路径板

适用：

- 首次价值时刻
- 入口 -> 讲题 -> 继续讲 -> 复盘
- 搜索 -> 落地页 -> 转化

```html
<table>
  <tr>
    <td align="center" width="23%"><img src="../04-experience/frames/frame-00001.png" style="width:95%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="4%"><strong>→</strong></td>
    <td align="center" width="23%"><img src="../04-experience/frames/frame-00030.png" style="width:95%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="4%"><strong>→</strong></td>
    <td align="center" width="23%"><img src="../04-experience/frames/frame-00120.png" style="width:95%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="4%"><strong>→</strong></td>
    <td align="center" width="23%"><img src="../04-experience/screenshots/example-result.png" style="width:95%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
  </tr>
  <tr>
    <td align="center"><sub>入口</sub></td>
    <td></td>
    <td align="center"><sub>关键交互</sub></td>
    <td></td>
    <td align="center"><sub>价值时刻</sub></td>
    <td></td>
    <td align="center"><sub>结果或复盘</sub></td>
  </tr>
</table>
```

## 3. 角色板

适用：

- 用户分析
- 不同角色对应不同页面承接
- 学生 / 家长 / 高阶用户对照

```html
<table>
  <tr>
    <td align="center" width="33%"><img src="../04-experience/screenshots/example-role-a.png" style="width:88%; max-width:240px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="33%"><img src="../04-experience/screenshots/example-role-b.png" style="width:88%; max-width:240px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="33%"><img src="../04-experience/screenshots/example-role-c.png" style="width:88%; max-width:240px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
  </tr>
  <tr>
    <td align="center"><sub>角色 A：说明它被优先服务什么</sub></td>
    <td align="center"><sub>角色 B：说明它要补什么能力</sub></td>
    <td align="center"><sub>角色 C：说明它被服务不足什么</sub></td>
  </tr>
</table>
```

## 4. 节点板

适用：

- 商业化
- 认证
- 解锁
- 打印 / 导出 / 下载

```html
<table>
  <tr>
    <td align="center" width="25%"><img src="../04-experience/screenshots/example-trigger.png" style="width:92%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="25%"><img src="../04-experience/screenshots/example-auth.png" style="width:92%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="25%"><img src="../04-experience/screenshots/example-benefit.png" style="width:92%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
    <td align="center" width="25%"><img src="../04-experience/screenshots/example-result.png" style="width:92%; max-width:220px; border:1px solid #e2e8f0; border-radius:12px;" /></td>
  </tr>
  <tr>
    <td align="center"><sub>触发点</sub></td>
    <td align="center"><sub>门槛</sub></td>
    <td align="center"><sub>权益说明</sub></td>
    <td align="center"><sub>最终结果</sub></td>
  </tr>
</table>
```
