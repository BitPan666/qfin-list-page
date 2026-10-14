# Structural validation

## Draft checks already available

- 无明确尺寸覆盖时，外层画板回读为 `1366px` × `768px`；有覆盖时按用户指定值验收，未指定的维度仍使用默认值。用户明确要求高度随完整内容调整时，允许自适应高度。
- 固定视口下，筛选展开前后外层尺寸保持不变；超高业务内容具有内部纵向滚动，末行与分页可滚动到达，字体、控件和行高保持规范。

- The top header resolves to `Navigation / HeaderMenu / Jinyumeng Header`, node `4993:1440`; it is `56px` high, transparent, uses `20px` horizontal padding, and keeps the fixed brand/notification/user structure.
- Sidebar items resolve to `JYM-SideMenuItem` and preserve `Level`, `Has Submenu`, `State`, label, and icon Instance swap properties.
- First-level online menu icons resolve to real `Icon/jinyumeng/*` components.
- Filter control bodies remain `240px` wide when the page width changes.
- Filter controls resolve to `Entry / Jinyumeng / Input` (`5010:19`), Select (`5010:7028`), DatePicker (`5010:7039`), or DateRange (`5010:7055`).
- Filter Items resolve to `Data Display / Jinyumeng / Filter Item`, node `5011:62`; titled items preserve the `76px` right-aligned label and real `controlSlot 筛选控件插槽` content.
- Filter controls bind `边框/--qifu-border-color-default` and `--qifu-radius-4`; filter buttons resolve `组件/Button/--qifu-button-radius` to `4px` under `金毓盟/Light`.
- The white filter surface has `28px` top and bottom padding.
- Filter rows have `20px` vertical separation.
- At the `1366px` reference width, three filter controls fit per row; wider examples may show four or five without stretching the controls.
- The filter surface uses an equal-cell grid: `columnCount = max(1, floor(filterSlotWidth / itemSlotWidth))` and `cellWidth = filterSlotWidth / columnCount`. Filter Items keep their intrinsic widths and are centered in their cells; no fixed horizontal gap or horizontal surface inset is added.
- 筛选项与操作组按同一列宽数组定位. The operation group follows the last visible filter as one indivisible Slot; its read-back row and column equal the documented modulo formulas.
- In the three-column reference, two filters place the operation group at row one/column three, while three filters place it at row two/column one.
- When collapsed, the filters plus operation group occupy at most two rows, `visibleFilterCount = 2 × columnCount - 1`, and 展开/收起 is visible inside the operation group. Expanded composition contains all requested filters before that same group.
- Every right-side white content surface keeps `20px` from the sidebar and `20px` from the viewport right edge.
- The page root resolves to `Templates / Jinyumeng / List Page Shell`, node `5022:16`, and preserves nested Workspace Shell `5022:8` and Content Shell `5022:2` ancestry.
- Requested sidebar, tabs, filter, action, and table content exists inside the mapped Slots. `showActionBar 显示独立操作栏` matches the requested composition.
- The system internal tabs resolve to `Data Display / Tag / Tag`, node `3178:9659`; selected and unselected states match the confirmed variant contracts.
- A standalone list-operation surface is `52px` high. Its Button instances use `20px` horizontal inset and the requested left or right alignment.
- Table-integrated actions keep the same `20px` inset above the table.
- 操作组 Auto Layout 宽度 = 工具栏可用宽度. A right-aligned group reads back `primaryAxisAlignItems=MAX` (右对齐回读 `MAX`); a left-aligned group reads back `primaryAxisAlignItems=MIN` (左对齐回读 `MIN`). A Hug-width action frame positioned by x coordinate fails validation.
- A present table title is `16px` Semibold; an omitted title leaves no placeholder title layer.
- The table resolves to `Data Display / Jinyumeng Table / Shell`, node `4975:9829`, with only basic type and xlarge 48px size.
- Shell rows and cells measure `48px`. Header text is `#595C72`, Medium, `14px`; row text is `#121736`, Regular, `14px`.
- The Shell selection property resolves to component `4975:9830` for on or `4975:9855` for off. Nested rows, cells, and selection cells remain real Jinyumeng Table instances.
- With selection on, the Header Selection Cell fill reads back `背景色/--qifu-bg-color-canvas`; the nested checkbox 方框本体保持白色. Data-row Selection Cells do not inherit the header canvas background.
- The resulting component tree and containing page resolve the existing `金毓盟/Light` mode.
- Header Cell 数量 = columns.length.
- For a `1366px` overall-effect acceptance trial, 可见业务字段数为 `5–8`; the selection column is validated separately and is not included in this count.
- Row 数量 = data.length, and Content Cell 数量 = data.length × columns.length.
- Header and every data row use the same ordered width array; long text follows the confirmed overflow rule and numeric/action columns use their confirmed alignment.
- With selection on, Selection Cell 数量 = data.length + 1; with selection off, the count is zero.
- For 1–4 row actions, each action cell resolves to `Data Display / Table / Cell Content / Action Content-V2`, node `3678:8875`, and its visible property count equals the PageSpec action count.
- Every visible table status uses the real Tag instance with `medium/square` and the requested semantic theme.
- Shell height satisfies `requiredTableHeight = headerSlot.height + rowsSlot.height + paginationSlot.height`; Jinyumeng header, rows, and cells remain `48px` and pagination is not clipped.
- A visible pagination resolves to `Navigation / Pagination / Pagination`, node `3698:482`; `pageCount`, current page, totals, page size, and visibility properties read back to PageSpec.
- Pagination geometry satisfies `paginationRight = tableRight = tableSurfaceRight - 20px`; its full-width containing Auto Layout reads back `primaryAxisAlignItems=MAX`.
- Pagination reads back 上一页箭头向左 and 下一页箭头向右. Numeric pages increase left-to-right and exactly one item matches the selected current page; the current-page-2/8 acceptance example is `← 1 2（当前页）3 4 5 … 8 →`.
- Loading feedback resolves to `Data Display / Loading / Loading`, node `3268:29`, or Spinner `3267:8` for an explicitly icon-only indicator.
- Empty and error feedback resolves to `Data Display 数据展示 / Empty 空状态 / Empty`, node `3621:45`, with the requested `status 状态`, description, and action visibility properties.

## 每次交付验收

- 目标 Page ID 由用户指定；不得硬编码测试 Page。
- 创建前记录已有节点，只新增所需画板；更新只触及用户授权目标，保护无关节点。
- 依次执行组件解析、属性类型/值域/回读、实例关系、数量、主题、几何及分页检查；失败记录节点、期望值、实际值和原因。
- 结构 PASS 后截图检查整页；分别返回 structuralValidation、visualValidation 的 PASS 或 FAIL。
- 缺少输入返回 BLOCKED；未执行的检查记录 PENDING。不得猜测或伪造验收结果。
- 反馈状态仍为 DEFERRED，按具体需求补齐未确认行为；不阻塞正常数据页。
