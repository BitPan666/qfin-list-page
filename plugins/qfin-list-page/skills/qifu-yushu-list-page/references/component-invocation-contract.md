# 组件调用契约

本文件定义从 Component Map 找到组件之后，如何可靠地创建实例、解析真实属性 Key、写入属性、替换 Slot 并回读验证。它解决的是“怎么调用”，不是“选哪个组件”。

## 目录

- [核心原则](#1-核心原则)
- [PageSpec 到组件计划](#2-pagespec-到组件计划)
- [组件解析](#3-组件解析)
- [属性解析与写入](#4-属性解析与写入)
- [关键组件逻辑属性](#5-关键组件逻辑属性)
- [Slot 组装](#6-slot-组装)
- [失败分类](#7-失败分类)
- [写后验证](#8-写后验证)

## 1. 核心原则

每个业务属性必须完成以下闭环：

```text
逻辑属性
→ 读取实例 componentProperties
→ 解析唯一真实 Key
→ 校验属性类型和值域
→ 写入
→ 重新读取
→ 验证最终值
```

Component Map 中的 `Label`、`text`、`value 文本` 等是逻辑名称。Figma 运行时可能返回 `Label#2405:0` 这类带内部后缀的真实 Key。不得假设展示名称就是可写 Key，也不得把当前后缀永久写入 Skill。

属性或 Slot 无法完成闭环时，执行结果为失败。不要隐藏真实组件、覆盖文字、绘制替代控件或手绘表格继续交付。

## 2. PageSpec 到组件计划

先把业务提示词解析为 PageSpec，再生成唯一 `ComponentPlan`。不要从业务名直接跳到画布绘制。

| PageSpec 信息 | ComponentPlan |
| --- | --- |
| `platform=yushu`、`headerActive` | 1 个 Yushu Header-V2，设置当前入口 |
| `navigationMode=yushuPreset`、`sidePath[]` | 按毓数默认树和图标映射创建 SideMenuItem-V2，只有当前路径祖先展开 |
| `navigationMode=custom`、`customSideMenu`、`sidePath[]` | 按自定义配置创建 SideMenuItem-V2；逐项设置文案、层级、子集、状态和展开，一级图标按完整唯一组件名解析并 INSTANCE_SWAP |
| `compositionName` | List Page Shell-V2、Filter Bar-V2、可选 List Action Bar、Table Shell-V2 的稳定骨架 |
| `filters[]` | 每项 1 个 Filter Item-V2，加 1 个语义匹配的 Input、Select、DatePicker、DateRange、Checkbox 或 Cascader |
| `filterItemDisplay` | 写入每个 Filter Item-V2 的显示形式和标题 |
| `filterTrigger=按钮触发` | Filter Bar-V2 按钮触发变体，加确定/重置 Button 实例 |
| `filterTrigger=实时触发` | Filter Bar-V2 实时触发变体，不创建确定/重置 |
| `listActions.left/right` | 页面级 List Action Bar 内创建对应 Button 实例 |
| `primaryAction` | 页面级 List Action Bar 内创建唯一 Primary Button；按 placement 放在全栏最左或最右 |
| `tableSelection=true`（提示词“左侧是否有多选框：是”） | Table Shell-V2 `selection=on`，表头和每行插入 Selection Cell-V2 |
| `tableSelection=false` 或未填写 | Table Shell-V2 `selection=off`，不插入 Selection Cell-V2；列表操作按钮不改变此结果 |
| `columns[]` | 每列 1 个 Header Cell-V2；每行每列 1 个 Content Cell-V2 |
| 普通文本列 | Content Cell-V2 内放 Text-V2 |
| 所有标签型状态，不区分文案、二元或多状态 | Content Cell-V2 内放真实 Tag，并统一写入 `medium/square`；主题按状态语义映射 |
| PageSpec 明确要求 Status-V2 的额外状态内容能力 | 仅当其内部真实 Tag 也可写并回读为 `medium/square` 时使用；否则使用 Tag 或按失败关闭 |
| `rowActions[]` | Content Cell-V2 内放 Action Content-V2 |
| `pagination` | Table Shell-V2 的 paginationSlot 放 Pagination-V2 |

`ComponentPlan` 至少记录：用途、组件完整名称、预计实例数量、逻辑属性、Slot 目标和验收数量。计划中的必需组件全部解析成功后才创建页面。

## 3. 组件解析

按以下顺序解析组件，并把结果写入 `ComponentResolutionManifest`：

1. 同文件优先使用 `component-map.md` 中的本地节点 ID。
2. 节点 ID 失效时，按完整组件集名称精确查找。
3. 跨文件使用发布 Key 导入，再核对完整名称。
4. 同名结果多于一个时停止，不按模糊相似度选择。
5. 创建实例后记录实例 ID、main component ID、组件集名称和来源方式。

自定义一级菜单图标属于精确名称解析：`iconComponentName` 必须符合 `Icon/<system>/<purpose>` 三段式完整路径，并在当前可用组件库中恰好匹配一个 ComponentNode。禁止只按末段、中文用途、Node ID、相似度或画面外观推断；匹配为 0 时报告 `COMPONENT_MISSING`，多于 1 时报告 `COMPONENT_AMBIGUOUS`。

```text
ComponentResolutionManifest[]:
  purpose
  expectedName
  source=nodeId|publishKey|exactName
  componentId
  instanceId
  status=resolved|missing|ambiguous|failed
```

所有必需组件均为 `resolved` 后才能开始页面组装。`missing` 和 `ambiguous` 不能通过相似组件或手绘内容静默替代。

## 4. 属性解析与写入

### 3.1 属性解析规则

为每个逻辑属性声明：

```text
logicalName
keyPrefixes[]
expectedType=TEXT|BOOLEAN|VARIANT|INSTANCE_SWAP|SLOT
allowedValues[]（仅已知枚举）
required=true|false
```

从实例实时返回的 `componentProperties` 中筛选：

1. Key 与任一 `keyPrefix` 完全相同，或以 `<keyPrefix>#` 开头；
2. 属性类型等于 `expectedType`；
3. 候选必须恰好为一个。

候选为 0 时报告 `PROPERTY_NOT_FOUND`；候选多于 1 时报告 `PROPERTY_AMBIGUOUS`。不要选第一个候选继续执行。

### 3.2 写入顺序

单个实例按以下顺序配置：

1. 写入决定结构的 VARIANT；
2. 重新读取属性，因为变体切换可能改变可用属性；
3. 写入 BOOLEAN；
4. 写入 TEXT；
5. 写入 INSTANCE_SWAP；
6. 替换 SLOT；
7. 回读全部必需属性与嵌套实例。

只向当前实例真实存在的属性写值。枚举值必须来自该实例当前组件属性定义或本契约已确认的值，不创造近义值。

### 3.3 INSTANCE_SWAP

INSTANCE_SWAP 的目标必须是已解析的真实 ComponentNode：

- 同文件传目标组件节点 ID；
- 跨文件先通过发布 Key 导入，使用导入后的组件节点 ID；
- 写入后回读目标组件 ID 或嵌套实例 main component ID；
- 业务图标必须与平台映射逐项相符，不能全部保留母版默认图标。

## 5. 关键组件逻辑属性

下表只记录稳定的逻辑 Key 前缀和类型。实际 Key 必须在实例上动态解析。

| 组件 | 逻辑属性 | Key 前缀 | 类型 | 必需条件 |
| --- | --- | --- | --- | --- |
| Yushu Header-V2 | 当前入口 | `activeMenu 当前菜单` | VARIANT | 毓数页面必需 |
| List Page Shell-V2 | 页面标题 | `pageHeaderSlot` | SLOT | 显示标题时必需 |
| List Page Shell-V2 | 筛选栏 | `filterBarSlot` | SLOT | 显示筛选时必需 |
| List Page Shell-V2 | 数据区 | `tableSlot` | SLOT | 必需 |
| List Page Shell-V2 | 标题开关 | `showPageHeader` | BOOLEAN | 必需 |
| List Page Shell-V2 | 筛选开关 | `showFilterBar` | BOOLEAN | 必需 |
| SideMenuItem-V2 | 文案 | `Label` | TEXT | 每项必需 |
| SideMenuItem-V2 | 层级 | `Level` | VARIANT | 每项必需 |
| SideMenuItem-V2 | 子菜单 | `Has Submenu` | VARIANT | 每项必需 |
| SideMenuItem-V2 | 状态 | `State` | VARIANT | 每项必需 |
| SideMenuItem-V2 | 展开 | `expanded 展开` | VARIANT | 有子菜单时必需 |
| SideMenuItem-V2 | 显示图标 | `showIcon 显示图标` | BOOLEAN | 一级菜单必需 |
| SideMenuItem-V2 | 图标 | `icon 图标` | INSTANCE_SWAP | 一级菜单必需 |
| Filter Item-V2 | 显示形式 | `display 显示形式` | VARIANT | 每个筛选项必需 |
| Filter Item-V2 | 尺寸 | `size 尺寸` | VARIANT | 每个筛选项必需 |
| Filter Item-V2 | 标题 | `label 标题` | TEXT | 带标题时必需 |
| Filter Item-V2 | 控件 | `controlSlot 筛选控件插槽` | SLOT | 每个筛选项必需 |
| Filter Bar-V2 | 展开 | `expanded 展开` | VARIANT | 必需 |
| Filter Bar-V2 | 触发方式 | `trigger 触发方式` | VARIANT | 必需 |
| Filter Bar-V2 | 快捷条件 | `showQuickFilters` | BOOLEAN | 必需 |
| Filter Bar-V2 | 主操作 | `showPrimaryAction` | BOOLEAN | 必需 |
| Filter Bar-V2 | 常用筛选 | `primaryFiltersSlot` | SLOT | 有筛选时必需 |
| Filter Bar-V2 | 更多筛选 | `moreFiltersSlot` | SLOT | 展开筛选时必需 |
| Filter Bar-V2 | 快捷条件内容 | `quickFiltersSlot` | SLOT | 显示快捷条件时必需 |
| Filter Bar-V2 | 查询操作 | `queryActionsSlot` | SLOT | 按钮触发时必需 |
| Filter Bar-V2 | 页面主操作 | `primaryActionSlot` | SLOT | 仅兼容旧页面；新列表页不使用 |
| Input Base-V2 | 文案 | `value 文本` | TEXT | 必需 |
| Input Base-V2 | 内容状态 | `content 内容` / `content` | VARIANT | 必需 |
| Input Base-V2 | 尺寸 | `size 尺寸` / `size` | VARIANT | 必需 |
| Input Base-V2 | 状态 | `state 状态` / `state` | VARIANT | 必需 |
| Select | 文案 | `value` | TEXT | 必需 |
| Select | 模式 | `mode` | VARIANT | 必需 |
| Select | 尺寸 | `size` | VARIANT | 必需 |
| Button | 文案 | `text` | TEXT | 必需 |
| Button | 类型 | `variant` | VARIANT | 必需 |
| Button | 尺寸 | `size` | VARIANT | 必需 |
| Table Shell-V2 | 尺寸 | `size` | VARIANT | 必需 |
| Table Shell-V2 | 类型 | `type` | VARIANT | 必需 |
| Table Shell-V2 | 选择列 | `selection` | VARIANT | 必需 |
| Table Shell-V2 | 表头 | `headerSlot` | SLOT | Data 状态必需 |
| Table Shell-V2 | 数据行 | `rowsSlot` | SLOT | 必需 |
| Table Shell-V2 | 分页 | `paginationSlot` | SLOT | 显示分页时必需 |
| Header Cell-V2 | 文案 | `headerText` | TEXT | 每列必需 |
| Header Cell-V2 | 尺寸 | `size` | VARIANT | 每列必需 |
| Row-V2 | 单元格 | `cellsSlot` | SLOT | 每行必需 |
| Content Cell-V2 | 内容 | `contentSlot` | SLOT | 每格必需 |
| Text-V2 | 文案 | `value` | TEXT | 文本格必需 |
| Action Content-V2 | 动作文案 | `action1`…`action4` | TEXT | 按动作数必需 |
| Action Content-V2 | 动作开关 | `showAction2`…`showAction4` | BOOLEAN | 按动作数必需 |
| Tag | 类型/主题/尺寸/形状 | `variant` / `theme` / `size` / `shape` | VARIANT | 每个列表标签必需；`variant=light`、`size=medium`、`shape=square` |
| Tag | 禁用 | `disabled` | BOOLEAN | 每个列表标签必需；固定为 `false` |
| Tag | 文案 | `text` | TEXT | 每个列表标签必需 |
| Tag | 图标/关闭 | `Show icon` / `Show closeBtn` | BOOLEAN | 每个列表标签必需；均固定为 `false` |
| Pagination-V2 | 页数档位 | `pageCount` | VARIANT | 分页必需 |
| Pagination-V2 | 总数/每页/跳页 | `showTotal` / `showPageSize` / `showJumper` | BOOLEAN | 分页必需 |

如果表中的前缀与运行时属性无法唯一匹配，先记录实际属性清单并停止。只有维护者核对母版后才能更新契约。

## 6. Slot 组装

Slot 必须由真实实例组成，并按依赖从内到外构建：

```text
Text-V2 / Tag / Action Content-V2
→ Content Cell-V2.contentSlot
→ Row-V2.cellsSlot
→ Table Shell-V2.rowsSlot

Header Cell-V2
→ Table Shell-V2.headerSlot

Pagination-V2
→ Table Shell-V2.paginationSlot

Input / Select / DateRange
→ Filter Item-V2.controlSlot
→ Filter Bar-V2 筛选 Slot
```

每次替换后验证：

- Slot 的当前值指向刚创建的节点；
- 节点仍为 INSTANCE，且 main component 名称符合预期；
- 节点数量与 PageSpec 一致；
- 原母版默认内容没有与自定义内容同时可见；
- 外层 Auto Layout、高度和裁切状态包住真实内容。

不要把裸 Text、矩形、Group 或整张截图写入用于设计系统组件的 Slot。

## 7. 失败分类

| 代码 | 含义 | 处理 |
| --- | --- | --- |
| `COMPONENT_MISSING` | 组件库确实没有目标能力 | 允许进入受限 Fallback 评估 |
| `COMPONENT_AMBIGUOUS` | 同名或候选不唯一 | 停止并报告候选 |
| `PROPERTY_NOT_FOUND` | 真实属性 Key 未找到 | 停止并报告属性清单 |
| `PROPERTY_AMBIGUOUS` | 属性候选不唯一 | 停止并报告候选 |
| `PROPERTY_WRITE_FAILED` | 属性写入报错 | 停止并报告实例与错误 |
| `PROPERTY_READBACK_MISMATCH` | 回读值与目标值不同 | 停止并报告期望/实际值 |
| `INSTANCE_SWAP_FAILED` | 图标或嵌套实例替换失败 | 停止，不绘制替代图标 |
| `SLOT_WRITE_FAILED` | Slot 无法替换 | 停止，不手绘对应区块 |
| `POSTCONDITION_FAILED` | 数量、结构或变量验收失败 | 停止，不标记完成 |

只有 `COMPONENT_MISSING` 可以进入 Fallback 判断。工具、脚本、权限、属性 Key、变体、字体加载和 Slot 写入问题都属于执行失败。

## 8. 写后验证

为每个实例记录：

```text
instanceId
componentName
logicalProperty
resolvedKey
expectedType
expectedValue
actualValue
status=pass|fail
```

页面创建过程中按实例即时验证，不把所有错误留到最后。任一必需项为 `fail` 时停止后续页面组装，并按 `structural-validation.md` 输出失败报告。
