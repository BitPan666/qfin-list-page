# Component invocation contract

## Confirmed top-header invocation

1. Resolve `Navigation / HeaderMenu / Jinyumeng Header` from node `4993:1440`.
2. Create one instance, keep height `56px`, stretch only its width, and set the containing shell to `金毓盟/Light`.
3. Set `accountName 用户名称` through its TEXT property; brand, notification, avatar, and arrow remain the component's fixed nested resources.
4. Read back the main component, `accountName 用户名称`, transparent fill, `20px` left/right padding, and nested instance ancestry.

## Confirmed sidebar invocation

1. Resolve `JYM-SideMenuItem` from node `4746:46261`.
2. Create or reuse an instance; do not rebuild the item from text, rectangles, and vectors.
3. Set `Level`, `Has Submenu`, and `State` only to documented variant values.
4. Set the text property to the online menu label.
5. For a first-level menu, set the Instance swap icon to the verified `Icon/jinyumeng/*` component mapped to that online menu.
6. Read back the instance main component, variant values, label, and icon component before accepting the result.

## Platform isolation

- Component resolution must stay inside approved Jinyumeng or shared-basic resources.
- No Yushu list-page component, ID, rule, or fallback may be invoked.
- Missing mappings return `BLOCKED`; they never authorize hand drawing.

## Confirmed page-shell invocation

1. Resolve `Templates / Jinyumeng / List Page Shell` from node `5022:16`.
2. Keep its real exposed `Navigation / HeaderMenu / Jinyumeng Header`, `Templates / Jinyumeng / Workspace Shell` (`5022:8`), and `Templates / Jinyumeng / Content Shell` (`5022:2`) instances.
3. Populate `sidebarSlot 侧边导航插槽`, `tabsSlot 系统内页签插槽`, `filterSlot 筛选区插槽`, `actionSlot 独立操作栏插槽`, and `tableSlot 表格区插槽` through the exposed nested Slots; never detach the shell chain.
4. Set `showActionBar 显示独立操作栏=false` when actions live above the table or no standalone action row is requested; otherwise keep it true and populate the action Slot.
5. Read back List Page Shell → Workspace Shell → Content Shell ancestry, every requested Slot child, `showActionBar 显示独立操作栏`, and the containing `金毓盟/Light` mode.

## Confirmed filter-component invocation

1. Resolve `Data Display / Jinyumeng / Filter Item` from component set `5011:62`.
2. Select `display 显示形式=直接筛选框` for an unlabeled control, or `带标题筛选项` for a label-plus-control group. Set `label 标题` only for the titled form.
3. Resolve the requested control from `Entry / Jinyumeng / Input` (`5010:19`), Select (`5010:7028`), DatePicker (`5010:7039`), or DateRange (`5010:7055`) and append its real instance to `controlSlot 筛选控件插槽`.
4. Each adapter exposes an inner base control as a 暴露的嵌套实例. Set business values and supported state properties on that exposed instance; the outer adapter intentionally has no duplicate component properties.
5. Keep the control at `240 × 32`. Read back the adapter main component, nested main component, business properties, `--qifu-radius-4`, and `边框/--qifu-border-color-default` bindings.
6. Read `filterSlotWidth` from the real Content Shell Slot and measure the widest rendered Filter Item outer width as `itemSlotWidth`. Resolve the equal-cell grid with the formulas in page-rules.md; do not substitute fixed horizontal padding, a fixed gap, or hard-coded breakpoints.
7. Append the operation group immediately after the visible Filter Items as one virtual item Slot. 查询、重置、展开/收起不得拆分或分别换行; the entire group moves to the next cell when the current row is full.
8. When the filters plus operation group exceed two rows, collapsed composition keeps `2 × columnCount - 1` filters and the operation group in the last cell of row two. Expanded composition restores all filters and repositions the same group with the modulo formula.

## Confirmed internal-tab invocation

1. Resolve `Data Display / Tag / Tag` from node `3178:9659`.
2. For an unselected tab, use outline/default/medium/square with icon and close disabled.
3. For the selected current page, use outline/primary/medium/square with the mapped icon and close enabled.
4. Set the label through the text property and read back the main component and variant values.

## Confirmed list-action invocation

1. Resolve `Base / Button / Button` from node `2381:2318`.
2. Use component `2381:788` for an outline secondary action and component `2381:482` for a primary action.
3. Keep buttons as instances. The prompt controls whether the instances are placed in the standalone 52px action row or above the table, and whether they align left or right.
4. Ensure ordinary rectangular buttons resolve `组件/Button/--qifu-button-radius` to `--qifu-radius-4` under `金毓盟/Light`.

## Confirmed Jinyumeng Table invocation

1. Resolve `Data Display / Jinyumeng Table / Shell` from node `4975:9829`; do not call any pre-existing Table Shell as a fallback.
2. Select component `4975:9830` when a selection column is required, or `4975:9855` when it is not.
3. Keep `size 尺寸=xlarge 超大 48px` and `type 类型=basic 基础` unchanged.
4. Replace business columns through the Shell header and row Slot properties. Preserve real nested instances of the Jinyumeng Header Cell, Row, Content Cell, Content Text, and Selection Cell sets.
5. Keep pagination in `paginationSlot 分页插槽` unless the prompt explicitly requests no pagination or a separately approved replacement.
6. The optional table title and list-action buttons are page-level composition outside the Shell. Do not add them as detached layers inside the component instance.
7. Ensure the containing Jinyumeng page uses `金毓盟/Light`, then read back the Shell main component, selection property, child component ancestry, row height, and screenshot.

### Dynamic column assembly

Input is `columns[]`, `data[]`, `rowActions[]`, `tableSelection`, and pagination. Build inside-out in this order:

```text
Content Text / Tag / Action Content-V2
→ Jinyumeng Content Cell.contentSlot
→ Jinyumeng Row.cellsSlot
→ Jinyumeng Shell.rowsSlot

Jinyumeng Header Cell
→ Jinyumeng Shell.headerSlot
```

1. Create 每列 1 个 Jinyumeng Header Cell, so the Header Cell count is `columns.length`.
2. For each record, create one Jinyumeng Row and 每行每列 1 个 Jinyumeng Content Cell in the exact `columns[]` order.
3. Use Content Text for ordinary values, Tag for semantic status, and Action Content-V2 for the action column. Do not insert bare text or buttons directly into a cell Slot.
4. Compute a semantic width array once, then apply 同一列宽数组 to the Header Cell and every corresponding Content Cell. Preserve the semantic alignment and overflow rules from page-rules.md.
5. With `tableSelection=true`, use the Shell selection-on component and preserve one Header Selection Cell plus one Selection Cell for every data row. Bind the Header Selection Cell background to `背景色/--qifu-bg-color-canvas`; the checkbox 方框本体保持白色. With false, use the selection-off component and create none.
6. For `rowActions[]` counts 1–4, set `action1 文案`…`action4 文案`, the matching visibility Booleans, and `dangerAction 危险项`. More than four actions require a mapped more-actions capability or remain BLOCKED.
7. Keep Pagination in `paginationSlot`; after all Slot writes, set `requiredTableHeight = headerSlot.height + rowsSlot.height + paginationSlot.height` and resize the Shell/container so no row or pagination is clipped.
8. Read back instance ancestry, counts, column order, widths, selection count, action properties, Tag properties, total height, and screenshot before accepting the table.

### Header Cell and Pagination properties

- For each Header Cell, set `headerText 表头文案` from `columns[].title`. Set `showSort 显示排序` and `showFilter 显示筛选` only from explicit column capabilities; both are false otherwise. When sorting is enabled, set and read back `sortState 排序状态` from the mapped preferred components.
- Resolve the nested `Navigation / Pagination / Pagination` in `paginationSlot`. Set `pageCount 页数`, `current 当前页`, `total 总数`, `pageSize 每页条数`, and the three visibility Booleans from PageSpec. Keep the Shell default instance when these values match; otherwise update the real nested instance without detaching it.
- Put Pagination in a full-width Auto Layout bar with `primaryAxisAlignItems=MAX` and resolve `paginationRight = tableRight = tableSurfaceRight - 20px`. If the inherited Slot is wider than the table, set the effective right padding to `paginationSlot.width - table.width`; never position a Hug-width Pagination by an x coordinate.
- Read back semantic direction and numeric order after overrides: 上一页箭头向左, 下一页箭头向右, numeric pages ascending left-to-right, and only `current 当前页` selected. For current page 2 of 8, require `← 1 2（当前页）3 4 5 … 8 →`.

## Confirmed feedback-component invocation

1. Resolve `Data Display / Loading / Loading` from node `3268:29` for a loading state; use `content 内容`, `size 尺寸`, and `text 提示文案` from PageSpec. Use Spinner `3267:8` only when an icon-only loading indicator is explicitly required.
2. Resolve `Data Display 数据展示 / Empty 空状态 / Empty` from node `3621:45` for empty and error feedback. Use `status 状态=noData 暂无数据` for empty data, `networkError 网络错误` for network failure, or `error 失败` for a generic failure.
3. Set `description 描述`, `showDescription 显示描述`, and `showAction 显示操作` only from explicit PageSpec content.
4. Keep these feedback elements as real instances. 反馈状态的页面内布局为 DEFERRED; do not invoke them in the first normal-data acceptance trial or infer whether title, actions, table header, or pagination remains visible.

## 写入失败与恢复

- 缺少必需输入或映射时返回 BLOCKED；未解决信息标记 PENDING。
- PROPERTY_NOT_FOUND、PROPERTY_AMBIGUOUS、PROPERTY_WRITE_FAILED、PROPERTY_READBACK_MISMATCH、INSTANCE_SWAP_FAILED、SLOT_WRITE_FAILED 和 POSTCONDITION_FAILED 返回 FAIL；记录节点 ID、属性 Key、期望与实际值。
- 遵循 figma-use 的 safeToRetryWithoutCanvasRead：true 时修正后重试；false 时先读取画布再进行定点恢复。保留已成功内容，不扩大修改范围。
- 每个实例写后回读，完成结构验收后截图检查；不得猜测调用结果或用手绘内容绕过失败。
