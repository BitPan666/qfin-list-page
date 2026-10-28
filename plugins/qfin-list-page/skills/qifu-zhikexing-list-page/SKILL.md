---
name: qifu-zhikexing-list-page
description: Use when creating, updating, or auditing Zhikexing or 智客星 desktop list pages in Figma from its verified candidate shell, with dynamic filters, columns, selection and source validation.
---

# 智客星列表页

固定 `platform=zhikexing`，`readiness=preflight-required`。独立适配可生成并验收候选副本；源候选仍是candidate。本次结构和整页截图均PASS才可交付，离线计划不等于生成成功。

每次读取VERSION、[来源和组件](references/platform-and-components.md)、[验收](references/validation.md)。`use_figma`前加载figma-use；完整页面同时加载figma-generate-design。

## PageSpec与计划

提取 `platform / pageName / targetPageId / sidePath[] / filters[] / tableActions[] / columns[{key,label,kind}] / tableSelection / rowActions[] / pagination / data[] / state`。路径最多三级，叶子=sideActive=activeTab；不推测缺失层级。

`python3 scripts/plan_page.py --spec <JSON>` 输出只读PREFLIGHT_REQUIRED计划，不写Figma。业务列1–8个唯一key；筛选和表格动态装配，不受历史4+1或固定selectable矩阵限制。tableSelection仅显式布尔，默认false，不从批量按钮推断。目标Page必须明确。

## 执行顺序

1. 回读 `5468:3233`，确认1366×768、Header真实owner `5517:2109`、实际 `Items=0`，不是实例名称里的Items=5。旧 `4892:34812` 返回BLOCKED_SOURCE；不得换Header后继续利用旧底图。人工参考5408:13969仅可重新完成等价预检后维护为新的版本，不作为本计划器自动后备。
2. 候选已明确复用菜单 `3650:998`，这是允许的共享资产；一级图标必须来自 `Icon/zhikexing/*`。禁止错误毓数Header `3639:1529`，不能把允许共享的菜单母版误判为整页串平台。
3. 更新前保留目标可编辑备份；创建时克隆候选为独立画板。Header与侧栏保留，只在副本修改业务内容及当前路径。保持1366×768，Header48、侧栏200。
4. 主题继承核实候选的语义绑定，`modeId=null`，不强行指定毓数Mode9:6，不假设品牌十六进制颜色。比较源/副本实际resolved颜色；目标Page导致主题漂移时返回THEME_AMBIGUOUS，不借其他平台Mode兜底。
5. 在Page Surface业务内容内按PageSpec更新筛选、操作、动态列、行、分页和选择列。真实公开Slot允许适配；没有公开能力则重新用真实组件和布局Frame组合业务内容，不拆Header、菜单、Button、Cell或Pagination。
6. 属性写入必须真实key→类型/合法值→写入→回读；SLOT是可容纳子节点的真实节点，不用setProperties写SLOT。字段多选和分页计数必须与输入一致。
7. 页级文字只在副本绑定批准Text Style。组件内部样式缺失须记录COMPONENT_SOURCE_GAP；修改组件版本前先保留可编辑副本，修复组件本体而非实例字体覆盖。无样式不能当作已通过。
8. 按验收核对结构与截图，返回版本、Page/画板链接、源/备份/目标、实例与主题回读及实际结果。样本通过不升级源候选或未经测试的状态。

## 常见错误

- 旧模板、外观相近Header、相同绿色均不能替代真实来源证据。
- 不能把固定旧样本的菜单、4+1筛选和已有数据直接带入新业务。
- 不能因模板字面名称写1440而生成1440宽；当前适配为1366×768。
