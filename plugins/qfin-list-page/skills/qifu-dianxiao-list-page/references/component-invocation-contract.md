# 电销组件调用契约

## 解析清单

写入前为每个必需组件记录：逻辑能力、精确名称、节点 ID 或发布 Key、解析结果 `resolved / missing / ambiguous / failed`。只有全部为 `resolved` 才可进入创建阶段。

## 属性写入闭环

每个实例固定执行：

1. 创建真实实例并读取 `componentProperties`。
2. 按展示名称解析唯一真实 Key，不固化内部后缀。
3. 校验类型与合法值；Instance swap 只接受 ComponentNode。
4. 写入属性并再次读取实例。
5. 比较预期值、实际值、主组件和可见截图。

找不到 Key、值域不支持、写入未持久化或回读不一致，均返回 `BLOCKED`，不是组件缺口的手绘许可。

## SideMenu

1. 使用 `Navigation / Dianxiao SideMenu / MenuRoot` 和 `Navigation / Dianxiao SideMenu / SideMenuItem`。
2. 一级标签从固定预设读取；二、三级标签从 PageSpec 当前路径和同级项读取。
3. 一级图标只能 Instance swap 到已确认 `Icon/dianxiao/*` 组件。
4. 回读 Level、Has Submenu、State、expanded、label、icon 主组件和唯一选中路径。
5. `State=Selected` 且显示 Icon 时，Icon 必须解析为电销主题色；Instance swap 后再次回读 Icon 内部可见矢量的 fill/stroke，旧实例 override 保持深色即 FAIL。
6. `1366px × 768px` 下菜单树超高时，使用 `Dianxiao Menu Scroll Viewport`：`全部菜单` 和 `收藏菜单` 固定，只滚动中间菜单树，且当前 `sideActive` 必须可见。

## Tabs 与筛选

1. 页签使用 `Data Display / Tag / Tag`，当前页签标签必须等于 `sideActive`。
2. 筛选控件保持 `200px × 28px`，父行使用 WRAP；不得把控件拉伸。
3. 设置标签、值、占位和操作按钮为 12px，并回读实际字体属性。
4. 查询、重置、展开/收起作为一个完整操作组；不得拆分到不同换行位置。

## 页面 Shell

1. 实例化 `Templates / Dianxiao / List Page Shell`（`5829:31`），不得使用其他平台 Shell。
2. 完整页固定由电销 Header 和 Workspace Shell 构成；Workspace 内的侧栏使用 `sidebarSlot 侧边导航插槽` 注入。
3. Content Shell 只允许通过 `tabsSlot`、`filterSlot`、`tableSlot` 三个原生 Slot 注入业务内容；不得新增 `actionSlot`、`showActionBar` 或在 Slot 上方覆盖手绘白底。
4. 表格标题和列表操作都属于 `tableSlot`：标题默认隐藏；操作按钮默认左对齐；按钮与表格距白色承载面左右各 20px。左侧操作组距顶部 20px，按主按钮 → 次按钮排序。提示词明确要求时才显示标题或改为右对齐。
5. 回读 Workspace 的 `200 + 28 + 1118 + 20 = 1366` 几何、三个承载面的 `--qifu-bg-color-surface`、`--qifu-radius-8` 变量绑定，以及 List Page、Workspace、Content Shell 的 `电销/Light` 模式。

## 动态表格

1. 使用 `Data Display / Table / Shell-V2`，按 Header Cell → Shell.headerSlot、Content → Cell → Row → Shell.rowsSlot 的顺序组装。
2. Header Cell 数量必须等于 `columns.length`；每行 Content Cell 数量和列顺序保持一致。
3. Header Cell 设置 `headerFont=12px`，Text 设置 `contentFont=12px`，Tag 与 Pagination 回读原生 12px。Action Content-V2 无字号属性：完成操作属性设置后，加载实际字体并将实例内每个可见操作 TEXT 覆盖为 `fontSize=12px`、`lineHeight=20px`。
4. 遍历 Table Shell 下全部可见 TEXT；任一节点无法回读为 12px 时 FAIL。属性切换导致新的操作文字出现后必须重新执行覆盖和回读。
5. 选择列由 `tableSelection` 决定。显示时 Header Selection Cell 根背景绑定 `背景色/--qifu-bg-color-canvas`。
6. 自定义行完成后重算 `requiredTableHeight = headerSlot.height + rowsSlot.height + paginationSlot.height`，避免裁切；Pagination 的可见内容顶部必须距最后一行数据底部 12px。
7. 分页父容器宽度必须等于当前表格可视宽度，内部 `MAX` 右对齐并设置右内边距 20px。共享 Shell 的分页 Slot 若仍为 `1248px`，先把 Slot 对齐改为 `MIN`；电销基准页使用 `1078px` 分页容器从表格左边缘起排，禁止让 Slot 的 `MAX` 把容器推到表格右侧之外。
8. 回读表格与分页绝对坐标，断言 `tableRight - paginationRight = 20px`；只看容器属性、不校验最终几何视为 FAIL。
9. 上一页箭头必须向左、下一页箭头必须向右。若共享实例内部旋转不可覆盖，替换为方向正确的真实箭头组件，不得用字符或手绘箭头。
10. 共享 Table Shell 的 Slot 高度无法按真实行数覆盖时，可使用布局 Frame 组装真实 Header Cell、Row、Content Cell 与 Pagination 实例；该 Frame 只承担布局，不得冒充发布组件，也不得分离或重画内部视觉组件。

## 平台隔离与失败关闭

- 允许共享基础组件，前提是 `component-map.md` 明确登记并在电销模式下完成回读。
- 禁止调用任何其他平台的 Header、SideMenu、Shell、平台 Icon 或固定菜单数据。
- 禁止为修改外观而分离 Button、Cell、Row、Pagination 等真实组件，或隐藏真实组件后覆盖裸 Text、矩形、截图或手绘替代品；纯布局组装 Frame 按动态表格第 10 条执行。
- PENDING 必需组件或完整属性回读未解决时，返回 `BLOCKED`，不创建部分正式页面。
