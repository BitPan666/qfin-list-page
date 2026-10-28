---
name: qifu-zhineng-yunying-list-page
description: Use when creating, updating, or auditing SmartOps or 智能运营 desktop list pages in Figma, including its independent navigation shell, filters, tables, and per-run acceptance.
---

# 智能运营列表页

固定 `platform=zhineng-yunying`。当前 `readiness=preflight-required`：已有独立适配，只有本次结构和整页截图均 PASS 才可完成交付；离线计划成功不代表页面通过。缺失能力明确 BLOCKED，不代用其他平台外壳。

每次读取 VERSION、[平台与组件规则](references/platform-and-components.md)和[验收](references/validation.md)。`use_figma` 前加载 figma-use，完整页面同时加载 figma-generate-design。

## PageSpec

`platform / pageName / targetPageId / sidePath[] / filters[] / tableActions[] / columns[{key,label,kind}] / tableSelection / rowActions[] / pagination / data[] / state`。

- sidePath 必填，最多两级，只展开当前祖先；一级名称与图标来自源外壳，当前标签必须等于 activeTab。
- columns 为1–8个唯一业务字段；筛选数、列数与业务数据动态决定，不限固定4+1；tableSelection只接受显式true/false，默认false，不从批量按钮推断。
- targetPageId必须来自用户目标或本轮明确的测试目标；不默认第一Page。正式任务缺失目标时先确认。
- 使用 `python3 scripts/plan_page.py --spec <JSON>` 得到只读计划；该脚本不调用Figma。它拒绝外平台Mode、菜单和未经登记来源。

## 执行

1. 从原Frame `6155:1851` 回读当前结构、字体、主题与真实菜单owner。不得因空白内容重建壳。
2. 为更新目标保留带时间戳的可编辑副本；创建新画板时克隆已核实的源外壳，保留源节点。写前记录源/备份/目标ID。
3. 在副本的 `(216,102,1134,633)` 区域创建垂直auto-layout内容Frame。原内容 `6148:34365` 是RECTANGLE，不能注入Slot；只在副本移除或隐藏对应空白矩形。
4. Header、渐变背景、侧栏和Tabs保留。菜单必须使用 `6158:1989` 真实实例；按动态读取的Label/State/expanded属性设置路径。`#5763`属性后缀不改变owner；禁止swap成电销母版。
5. 设置本副本 `basic 基础` 的 `2158:0` 智能运营Mode。先加载所涉字体和字体变量各Mode字体，再写Mode并回读；下层显式外平台Mode必须移除或纠正。
6. 内容使用已登记的共享真实Input/Select/Button/HeaderCell/Row/ContentCell/Text/Tag/Pagination实例。仅布局Frame可新建；动态列按内容需要分配宽度，业务变化通过公开属性、真实Slot和实例swap完成。
7. 组件属性按“读真实key→类型/值域校验→写入→回读”，Slot必须定位到真实SLOT后appendChild，不能setProperties写SLOT。真实组件不得detach，也不能隐藏后覆画裸Text。
8. 页级文字绑定现有批准Text Style；源缺失样式时先记录COMPONENT_SOURCE_GAP。页面级Frame文字可在副本修复；组件内部只能在独立备份后的组件版本修复，不能在实例层伪造已修复。
9. 按验收回报结构、语义主题、字体、菜单和截图；任何未解决项返回BLOCKED/FAIL及节点ID。更新不改无关节点。

## 交付

回报版本、Page和画板链接、来源/备份、组件实例关系、主题Mode、结构和截图结果。明确列出补全的示例数据；样本通过范围不扩展到未测试状态或控件。
