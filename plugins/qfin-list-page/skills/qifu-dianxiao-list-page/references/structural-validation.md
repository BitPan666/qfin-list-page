# 电销列表页结构验收

## 当前可执行检查

- 根 PageSpec 为 `platform=dianxiao`，不存在其他平台规则或专属节点。
- Header 必须为 `Navigation / HeaderMenu / Dianxiao Header`（节点 `5824:4491`）的真实实例，尺寸 `1366 × 56px`、左右内边距 `20px`、背景透明，且固定内容与电销平台一致。
- 页面根必须为 `Templates / Dianxiao / List Page Shell`（节点 `5829:31`）的真实实例；其 Workspace 必须来自节点 `5829:24`，Content Shell 必须来自节点 `5829:15`。
- Workspace 几何固定为 `200px 侧栏 + 28px 间隔 + 1118px 内容区 + 20px 右边距`。
- 顶层分类为 `全部菜单` / `收藏菜单`，中间分割线为 `#EBEBEB`。
- 一级菜单顺序与平台预设完全一致；每个可见一级 Icon 为真实 `Icon/dianxiao/*` 实例且尺寸 `16px × 16px`。
- 菜单容器宽 `200px`，当前路径唯一选中，只有当前祖先展开。
- 选中且显示 Icon 的菜单项，其 Icon 与文字都解析为电销主题色；短视口中当前项位于 `Dianxiao Menu Scroll Viewport` 的可见范围。
- 当前页签名称等于当前叶子菜单，选中颜色为电销主题。
- Tabs、Filter、Table 白色承载面圆角均为 `8px`。
- Content Shell 只有 Tabs、Filter、Table 三个 Slot；不存在独立操作栏、`actionSlot` 或 `showActionBar`。
- 表格标题默认隐藏；提示词未明确要求时不得显示标题。
- 表格操作按钮默认左对齐，按钮顺序为主按钮 → 次按钮；首个按钮距表格白底左侧和顶部均为 `20px`；表格本体距白底左右各 `20px`，1366px 基准页实际宽度为 `1078px`。
- List Page、Workspace、Content Shell 和页面内品牌型实例均解析到 `电销/Light`；不得出现毓数或金毓盟品牌色。
- 每个筛选控件宽 `200px`、高 `28px`，父容器为 WRAP；控件不随列宽拉伸。
- 筛选标签、控件值、操作按钮、表头、数据、状态、行操作和分页的可见字体均为 `12px`。
- Header Cell 数量 = `columns.length`；Row 数量 = `data.length`；Content Cell 数量 = `data.length × columns.length`。
- Header 与数据行使用相同列宽数组。选择列开启时 Selection Cell 数量 = `data.length + 1`。
- 选择列固定 `40px`；操作列等于操作内容宽度加右侧 `20px`，其表头和行内容均右对齐。
- 业务列按 `leftPadding + intrinsicContentWidth + visualTrailingGap` 计算，不得全部机械等宽；其中 `intrinsicContentWidth` 取该列表头与所有可见数据内容的最大宽度。
- 回读每个业务列“最长可见内容右边缘 → 下一列左边缘”的视觉尾部留白差值不超过 `1px`，且表头、所有数据行的列宽数组完全一致。
- 所有列宽总和等于表格可视宽度；1366px 基准画板应回读为 `1078px`，不得产生隐藏空白列或侵占操作列右侧 `20px`。
- Header Selection Cell 根背景绑定 `背景色/--qifu-bg-color-canvas`。
- Pagination 的父容器宽度等于表格可视宽度，内部为右对齐 `MAX`；共享 Shell 的分页 Slot 为 `MIN`，最终几何回读距离表格白色承载面右侧 `20px`。
- 上一页箭头向左、下一页箭头向右，页码递增且当前页唯一选中。
- 分页控件顶部距最后一行数据底部 `12px`，且不存在母版默认空行造成的额外留白。
- 页面中不存在裸 Text 覆盖组件、截图表格、手绘菜单、隐藏真实组件或跨平台 Shell。

## Release blockers

- PASS 12px 动态表格完整属性回读：5 列、2 行、10 个 Content Cell、26 个可见文本全部为 12px；分页右间距回读为 20px。
- PASS 17 个一级菜单图标全部完成映射；个人信息与消息中心已由正式菜单实例确认最终显示为 16px × 16px。
- PASS 纠偏后的完整页面结构与整页截图：测试画板节点 `5838:9056`，尺寸 1366px × 768px；唯一选中菜单与当前页签均为 `个人信息`，选中 Icon 为电销主题色且在滚动视口中可见；无独立操作栏；标题默认隐藏；左侧操作顺序为主按钮 → 次按钮，距左侧和顶部均为 20px；表格左右 20px；分页距最后一行数据底部 `12px`、右间距 20px，左右箭头方向正确。

当前无技术 blocker。用户确认本轮回归页前，Skill 仍保持 `BLOCKED readiness=draft`；确认后才允许切换为 ready。
