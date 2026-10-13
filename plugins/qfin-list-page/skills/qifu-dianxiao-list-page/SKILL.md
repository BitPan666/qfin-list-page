---
name: qifu-dianxiao-list-page
description: Use when explicit requests concern Qifu Dianxiao desktop list pages, their platform rules, component mappings, audits, or readiness-gated Figma work. Do not use for Yushu, Jinyumeng, forms, detail pages, dashboards, tree tables, or custom workbenches.
---

# Qifu Dianxiao List Page

## Overview

把业务描述转换为电销平台列表页规格，并在组件映射完整后使用真实 Figma 实例组装页面。本 Skill 固定 `platform=dianxiao`；当前为 `readiness=draft`，组件映射与纠偏回归已经完成，等待用户确认后切换为 ready。不得借用毓数或金毓盟的导航、Header、Shell、节点 ID 或视觉规则补缺口。

## Readiness gate

在用户确认 readiness 前，任何正式业务页面的生成或修改请求均返回 `BLOCKED`。页面 Shell、17 个一级菜单图标、12px 动态表格和完整回归页已经通过技术验收；当前只允许：

- 读取和审计电销页面；
- 补全组件映射与平台规则；
- 形成 PageSpec；
- 运行契约校验与只读结构检查。
- 在 Figma Page `测试` 中创建、修正和复核 Skill 回归画板；不得写入正式业务 Page。

禁止手绘 Header、菜单、筛选、表格或分页来绕过映射。缺失信息标记为 `PENDING`，不推断为已存在。

```text
BLOCKED readiness=draft platform=dianxiao
Missing: unresolved required component mappings or complete-page acceptance evidence.
No Figma generation or modification was attempted.
```

## Reference routing

每次执行完整读取 `VERSION`，并按任务读取下列资料：

- [电销平台基线](references/platform-dianxiao.md)：固定 Header 内容、一级菜单、图标、导航层级与平台隔离。
- [页面规则](references/page-rules.md)：页面结构、页签、筛选、操作区、表格、分页和响应式规则。
- [组件映射](references/component-map.md)：真实组件名称、节点 ID、复用边界和 PENDING 缺口。
- [组件调用契约](references/component-invocation-contract.md)：属性解析、Instance swap、Slot、写后回读与失败关闭。
- [结构验收](references/structural-validation.md)：从实例关系、尺寸、字体、状态和布局判断 PASS / FAIL。

任何 `use_figma` 调用前必须加载并遵循 `figma-use`；完整页面生成还需加载 `figma-generate-design`。未连接 Figma 时停止，不以网页截图或手绘替代。

## PageSpec

从自然语言、字段清单、截图或线框提取：

```text
platform=dianxiao
pageName / pageTitle / viewport / targetPage
headerProduct=客户销售平台－借条
topStatus[]
navigationRoot=全部菜单|收藏菜单
sidePath[] / sideActive / sideExpanded[]
sideChildren.level2[] / sideChildren.level3[]
tabs[] / activeTab
filters[]: field, control, placeholder, defaultValue
filterTrigger=实时触发|按钮触发
filterCollapsed=true|false
tableActions[] / tableActions.align=left|right
tableTitle? / showTableTitle=false|true
columns[] / tableSelection / rowActions[]
pagination / data / state
```

固定约束：`activeTab` 必须等于 `sideActive`；一级菜单只可从电销预设中选择；二、三级菜单由提示词提供并仅展开当前路径；不存在独立列表操作栏；`showTableTitle` 默认 `false`，`tableActions.align` 默认 `left`；基准画板固定为 `1366px × 768px`；列表页正常数据优先保留 5–8 个业务字段。

## Workflow

1. 确认请求属于电销列表页；属于其他平台时停止并切换对应 Skill。
2. 读取平台基线和页面规则，形成唯一 PageSpec，不补造菜单树或组件 ID。
3. 按组件映射建立解析清单，逐项标记 `resolved / missing / ambiguous / failed`。
4. 若任一必需项不是 `resolved`，返回 `BLOCKED`，不写 Figma。
5. Readiness 未来切换为 ready 后，按 Header → Side navigation → Tabs → Filter → Table area（可选标题、操作、表格、分页）顺序创建真实实例。
6. 每次属性设置均执行“读取真实 Key → 校验类型和值域 → 写入 → 回读”；Slot 与 Instance swap 同样回读。
7. 按结构验收完成树结构检查，再截图检查整页；两者都 PASS 才可交付完成。

## Quick reference

| 决策 | 规则 |
| --- | --- |
| 平台 | 只使用 `platform=dianxiao` |
| 复用方式 | 复用毓数的工作流与动态表格拼装方法，不复用平台外壳和视觉常量 |
| 页面容器 | 电销白色承载面统一 8px 圆角 |
| 筛选 | 毓数式筛选组件，控件固定 200px，父容器 WRAP |
| 字体 | 筛选、按钮、表格、行操作、分页统一 12px |
| 表格内容区 | 不设独立操作栏；标题默认隐藏、可按提示词显示；操作按钮默认左对齐，距白底左侧和顶部均为 20px，顺序为主按钮 → 次按钮；表格距白底左右各 20px |
| 动态列宽 | 使用内容感知列宽：固定选择列和操作列后，业务列按各列最长内容计算基础宽度，剩余宽度均分为统一视觉尾部留白；禁止机械等宽 |
| 分页 | 上一页向左、下一页向右；分页距最后一行数据底部 12px，距表格白底右侧 20px |
| 导航 | 固定一级菜单；提示词只决定当前路径及其二、三级内容 |
| 失败处理 | 缺映射或回读失败即 `BLOCKED`，禁止手绘替换 |

## Common mistakes

- 把“结构参考毓数”误写成直接调用毓数 Header、SideMenu 或 Shell。
- 不调用正式电销 Header 组件，而把顶部区域手绘成 Group。
- 把 200px 筛选控件拉伸填满列，而不是保持定宽后换行。
- 只把数据行改为 12px，却遗漏筛选标签、按钮、表头、操作项或分页。
- 额外生成独立操作栏，或默认强制显示表格标题、把操作按钮放在右侧。
- 左侧操作区把次按钮放在主按钮之前，或只校验左边距而遗漏顶部 20px。
- 把所有业务列机械等宽，导致短字段列出现大片空白、长字段列与下一列过于拥挤；应按最长内容计算列宽后均分视觉尾部留白。
- 直接缩短根画板却不建立侧栏滚动视口，导致当前选中菜单在 1366px × 768px 视口中不可见。
- 展开不属于当前路径的菜单，或让选中页签与当前菜单不一致。

## Exit condition

仅当 `component-map.md` 中所有 P0 项解析完成、契约校验通过、完整页面结构回读与截图验收通过，并由用户确认后，才可把 `readiness=draft` 改为 `readiness=ready`。
