# Page rules

## Confirmed source

User-confirmed rules and read-only inspection of the `SideMenu 侧边菜单` page, including the 1366px example frame.

## Page shell and content surfaces

- 未特别说明时，桌面端画板默认宽 `1366px`、高 `768px`。用户明确指定其他尺寸或高度按完整内容调整时，以用户要求为准；仅指定其中一个维度时，另一维度保留默认值。
- 默认固定视口下，内容超高通过业务内容区内部纵向滚动承载；筛选展开不撑高外层画板，不压缩字体、控件或表格行高。保留完整内容与可滚动到达的分页，不以裁切隐藏内容代替滚动；分页是否固定按用户要求处理。
- 表格 Shell 的完整内容高度与外层画板视口高度分别计算，完整内容高度不得反向撑大固定视口。

- The platform shell uses a light-blue background. The top navigation and sidebar sit directly on this platform background.
- The right-side business regions use a 白色内容承载面. This includes the filter region, an optional standalone list-operation region, and the table region.
- Every right-side content surface starts at 侧边栏右侧 `20px` and ends at 视口右侧 `20px`.
- The system internal tab bar sits above the filter region on its own white surface. Use the confirmed 系统内页签栏 component states; do not redraw selected or unselected tags.

## Top header

- Use `Navigation / HeaderMenu / Jinyumeng Header`; the fixed structure is 品牌锁定区、通知入口、用户区.
- Header 高度固定 `56px`, uses 左右内边距 `20px`, and keeps a 透明背景 so the platform light-blue background remains visible.
- The page-level background texture stays outside the Header component. Do not place the texture, a white surface, or an opaque replacement inside the Header.
- Only `accountName 用户名称` is business-editable in the current component. Brand, notification, avatar, and arrow remain the mapped nested resources.

## System internal tabs

- Unselected tabs use the shared Tag component with outline/default/medium/square, without icon and without close button.
- The selected current-page tab uses outline/primary/medium/square, with the confirmed icon and close button enabled.
- Tab labels come from the requested open pages. Do not substitute business labels that were not provided.
- The selected current-page tab label must equal the currently selected sidebar menu label.

## Filter region

- The filter region sits on a white surface; the wider page background is platform-specific light blue.
- Compose filters with the mapped `Data Display / Jinyumeng / Filter Item` and Jinyumeng Input, Select, DatePicker, or DateRange adapters; do not hand-draw controls.
- A filter field is composed of an optional label plus a control. The control itself uses 控件本体固定宽度 `240px` and fixed height `32px`; it must not stretch with the page width.
- In the titled Filter Item, the label width is fixed at `76px` and the label is right-aligned.
- Filter controls use 圆角 `4px`: bind their stroke to `边框/--qifu-border-color-default` and every corner to `--qifu-radius-4`.
- Buttons in the filter action area resolve `组件/Button/--qifu-button-radius` to `--qifu-radius-4` under `金毓盟/Light`.
- The white filter surface uses 垂直内边距 `28px` above the first row and below the last row.
- Multiple filter rows use 行间距 `20px`.
- Filters use an 等宽槽位网格. There is no fixed horizontal gap or fixed horizontal surface padding; the available width is divided evenly across the current columns while every real Filter Item keeps its intrinsic fixed width.
- Let `filterSlotWidth` be the actual available width of `filterSlot 筛选区插槽`, and let `itemSlotWidth` be the widest rendered Filter Item outer width required by the current fields. Resolve `columnCount = max(1, floor(filterSlotWidth / itemSlotWidth))`, then resolve `cellWidth = filterSlotWidth / columnCount`.
- Center each fixed-width Filter Item inside its equal-width cell. The cell's residual width therefore becomes dynamic left/right breathing room; do not add another fixed horizontal gap or fixed surface inset.
- At a `1366px` page width the actual filter Slot resolves to 每行 `3` 个槽位; wider pages may resolve to 每行 `4–5` 个 while each control body remains `240px`. Responsive behavior changes `columnCount`, not control width.
- 查询、重置、展开/收起 form one operation group. 操作组作为一个完整槽位 and uses the same `itemSlotWidth` as a Filter Item; place it immediately after the last visible filter and never split its buttons across grid cells.
- With one-based coordinates, resolve `actionRow = floor(visibleFilterCount / columnCount) + 1` and `actionColumn = visibleFilterCount % columnCount + 1`. In the `1366px` three-column case, `2 个筛选项` place the operation group in 第 1 行第 3 列; `3 个筛选项` move it to 下一行第 1 列. Apply the same modulo rule for every other count.
- Treat the operation group as one additional layout slot when testing the two-row limit. If `filterCount + 1 > 2 × columnCount`, show 展开/收起. In the collapsed state set `visibleFilterCount = 2 × columnCount - 1`, so filters plus the operation group occupy exactly two rows and the operation group sits in the last cell. In the expanded state set `visibleFilterCount = filterCount` and place the operation group after all filters with the same formula.

## Evidence clarification

In the inspected example, the input control is 240px wide while the label-plus-control group is wider. Therefore “240px 筛选项” is interpreted as the control body, not the entire labeled group.

## List-operation region

- List actions may occupy a standalone white row or sit inside the table surface above the header. The user prompt decides which composition is required.
- A standalone operation row uses 独立操作栏高度固定 `52px`.
- Standalone actions use 左右内边距 `20px`. Buttons may be 左对齐或右对齐 according to the prompt.
- When actions sit at the 表格上方, keep the same `20px` left or right inset inside the table surface.
- The action-group Auto Layout spans the full available toolbar width. For right-aligned actions set `primaryAxisAlignItems=MAX`; for left-aligned actions set `primaryAxisAlignItems=MIN`.
- Do not use a Hug 宽度容器 moved with an x coordinate to imitate left or right alignment. Alignment must remain correct when the table surface width changes.
- Do not automatically add an empty standalone action row when the request places all actions with the table.

## Table region

- The table surface uses white. The table may have a title or omit it; 表格标题可选.
- When present, the table title is `16px` and Semibold.
- Use only the confirmed 基础类型表格 for Jinyumeng list pages.
- Table 单元格高度固定 `48px`, represented by `size 尺寸=xlarge 超大 48px`.
- Header text uses `#595C72`, Medium, `14px`.
- Data-row text uses `#121736`, Regular, `14px`.
- Selection-column presence is controlled by the Jinyumeng Table Shell `selection 选择列` property. Do not hand-build a checkbox column.
- With selection enabled, the Header Selection Cell background binds `背景色/--qifu-bg-color-canvas`, matching every other Header Cell. The checkbox 方框本体保持白色 and preserves its existing border so the control remains visible.
- Pagination remains inside the Shell pagination slot unless the prompt explicitly requests no pagination or a mapped replacement.
- Pagination is right-aligned to the table content edge with `paginationRight = tableRight = tableSurfaceRight - 20px`. Use a full-width Auto Layout container with `primaryAxisAlignItems=MAX`; when the inherited pagination Slot is wider than the table, its effective right padding equals `paginationSlot.width - table.width` instead of using a fixed offset.
- Pagination directions are semantic and fixed: 上一页箭头向左 and 下一页箭头向右. Numeric pages increase from left to right. For the confirmed 8-page acceptance example with current page 2, the visible order is `← 1 2（当前页）3 4 5 … 8 →`; page 1 is the first number and only page 2 uses the selected state.

### Dynamic columns and widths

- For a `1366px` list page whose goal is 整体效果, 整体效果验收默认使用 `5–8` 个业务字段. 选择列不计入 this count; keep only representative name, ID, role/status, and operation fields unless the prompt explicitly requests a larger data contract.
- Build columns from `columns[]`. Header and every data row use the same column order and 表头与每行使用同一列宽数组; do not use `SPACE_BETWEEN` to fake alignment.
- Width resolution is deterministic: first use an explicit `columns[].width`. For every remaining non-elastic column, measure 表头与样例单元格内容的最大固有宽度 plus the real component padding. Give all 剩余宽度 to the long-text 弹性列, split equally when several elastic columns exist.
- If no elastic column exists, distribute remaining width equally across name columns; if none exist, give it to the last non-action column. If intrinsic widths already exceed the surface, keep them 不压缩 and set the scroll container's 内容总宽度 to their sum.
- 序号与短 ID use narrow stable widths. 名称 uses a readable medium width. 长文本 and URLs take the elastic width, use 单行省略, and require a Tooltip or detail entry when the full value matters.
- 数字 are 右对齐. 日期时间 and 状态 use stable widths. 操作 is 右对齐 with a `20px` right inset; the header aligns to the first visible action.
- The width array must cover the complete visible table width. When the semantic minimum widths exceed the available surface, use confirmed horizontal 横向滚动 instead of shrinking typography, cell height, or action gaps.
- Row operations use the mapped Action Content-V2. Table status values use the mapped shared Tag under `金毓盟/Light`.

## Deferred scope

- DEFERRED Empty、Loading、Error placement and their surrounding title/action/table/pagination visibility rules. They are outside the first normal-data acceptance trial and do not block it.
- Do not generate or evaluate a feedback state until a later explicit requirement confirms that scope.
- 不得猜测 any deferred feedback-state behavior.

正式列表页可按用户指定目标创建；每次执行完整结构与视觉验收。
