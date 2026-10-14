# Component map

## Confirmed top header

- Base Spec: `Jinyumeng Header / Base Spec / v1`, node `4993:1437`.
- Reusable component: `Navigation / HeaderMenu / Jinyumeng Header`, node `4993:1440`.
- The component is `1366 × 56`, transparent, and uses the existing `金毓盟/Light` mode.
- Fixed nested resources are the brand lockup, `Icon/basic/xiaoxitongzhi`, `Icon/jinyumeng/touxiang`, and `Icon/basic/Down-small`.
- Editable property: `accountName 用户名称` (TEXT). Do not detach the component or replace its fixed resources with hand-drawn layers.

## Confirmed sidebar item

- Component set: `JYM-SideMenuItem`.
- Component-set node: `4746:46261` on the `SideMenu 侧边菜单` page.
- Variant properties: `Level`, `Has Submenu`, and `State`.
- `Level` options are `1`、`2`、`3`.
- `Has Submenu` options are `True` and `False`.
- `State` options are `Default`、`Selected`、`Hover`、`Disabled`.
- The matrix contains 共 `24` 个变体.
- Editable properties include the menu label and an icon Instance swap property.
- Instance width is fixed by the component at the sidebar width; instances must not be detached or redrawn.
- JYM-SideMenuItem 最新母版是视觉状态的唯一事实源. Resolve `Level`, `Has Submenu`, and `State` to a live instance and let the current master define fills, typography, icon colors, arrows, and selected treatment.
- 不得在 Skill 中硬编码旧的颜色、字重或选中效果. If the master changes, new list-page compositions must inherit it without a Skill revision.

## Confirmed sidebar composition

- Sidebar-content frame: `Navigation / JYM Sidebar Content`, node `4873:1201`.
- Sidebar items in the inspected example are real instances of `JYM-SideMenuItem`, not hand-built replicas.
- First-level icon mappings observed in the example include:
  - 工具箱 → `Icon/jinyumeng/gongjuxiang`
  - 线索分发引擎 → `Icon/jinyumeng/xiansuofenfayinqing`
  - 我的客户 → `Icon/jinyumeng/wodekehu`
  - 待办管理 → `Icon/jinyumeng/daibanguanli`
  - 数据管理 → `Icon/jinyumeng/shujubaobiao`
  - 公海池 → `Icon/jinyumeng/gonghaichi`
  - 业务管理 → `Icon/jinyumeng/yewuguanli`
  - 组织管理 → `Icon/jinyumeng/zuzhiguanli`
  - 合规监管 → `Icon/jinyumeng/heguiguanli`
  - 投放结算 → `Icon/jinyumeng/toufangjiesuan`
  - 标签管理 → `Icon/jinyumeng/biaoqianguanli`
  - 知识管理 → `Icon/jinyumeng/zhishiguanli`
  - KPI管理 → `Icon/jinyumeng/kpiguanli`

## Filter components

- `Entry / Jinyumeng / Input`, node `5010:19`.
  - Exposes the nested `Input / Base-V2` instance and its `value 文本`, prefix/suffix icon, count, clearable, `size 尺寸`, `content 内容`, and `state 状态` properties.
- `Entry / Jinyumeng / Select`, node `5010:7028`.
  - Exposes the nested `Select / Base` instance and its value, clearable, searchable, prefix/suffix icon, tag, `mode 模式`, `size 尺寸`, and `state 状态` properties.
- `Entry / Jinyumeng / DatePicker`, node `5010:7039`.
  - Exposes the nested DatePicker instance and its `placeholder 提示`, `value 文本`, `clear 清空`, `size 尺寸`, `state 状态`, and `filled 填充` properties.
- `Entry / Jinyumeng / DateRange`, node `5010:7055`, with the same exposed property contract for a date range.
- All four adapters keep the control body at `240 × 32`, use `金毓盟/Light`, bind every corner to `--qifu-radius-4`, and bind the stroke to `边框/--qifu-border-color-default`.
- `Data Display / Jinyumeng / Filter Item`, component set `5011:62`.
  - `display 显示形式` options are `直接筛选框` and `带标题筛选项`.
  - TEXT property: `label 标题`.
  - SLOT property: `controlSlot 筛选控件插槽`.
  - The control Slot remains `240 × 32`; the titled variant uses a fixed `76px` label that is 右对齐.
- Filter Items accept only the mapped Jinyumeng adapters in the control Slot. 不得猜测 or substitute a Yushu input component.

## Confirmed Jinyumeng page shells

- `Templates / Jinyumeng / Content Shell`, node `5022:2`.
  - SLOT properties: `tabsSlot 系统内页签插槽`, `filterSlot 筛选区插槽`, `actionSlot 独立操作栏插槽`, and `tableSlot 表格区插槽`.
  - BOOLEAN property: `showActionBar 显示独立操作栏`.
- `Templates / Jinyumeng / Workspace Shell`, node `5022:8`.
  - SLOT property: `sidebarSlot 侧边导航插槽`.
  - Its exposed nested Content Shell carries the four content Slots and `showActionBar 显示独立操作栏`.
- `Templates / Jinyumeng / List Page Shell`, node `5022:16`.
  - Its exposed Header, Workspace Shell, and Content Shell instances preserve the complete Header → Workspace → Content ancestry.
  - Business sidebar, tabs, filters, optional standalone actions, and table content enter only through the mapped nested Slots.

## Confirmed system internal tabs

- Reusable component set: `Data Display / Tag / Tag`, node `3178:9659`.
- Observed unselected instance: node `4902:2195`, using outline/default/medium/square with icon off and close button off.
- Observed selected current-page instance: node `4902:2065`, using outline/primary/medium/square with icon on and close button on.
- Set text, icon visibility, close visibility, and the documented variant properties through the instance. Do not detach or redraw the Tag.

## Confirmed shared list-action buttons

- Reusable component set: `Base / Button / Button`, node `2381:2318`.
- Secondary outline action: component `2381:788`.
- Primary base action: component `2381:482`.
- Ordinary rectangular variants bind `组件/Button/--qifu-button-radius`: 毓数/Light and 智能运营/Light alias `--qifu-radius-2`, while 金毓盟/Light aliases `--qifu-radius-4`. Pure-icon and round-icon geometry remains unchanged.
- Button placement belongs to page composition. The component itself must remain an instance.

## Confirmed Jinyumeng Table family

- Base Spec: `Jinyumeng Table / Base Spec / v1`.
- `Data Display / Jinyumeng Table / Header Cell`: set `4968:8897`, xlarge component `4968:8898`.
  - TEXT: `headerText 表头文案`.
  - BOOLEAN: `showSort 显示排序`, `showFilter 显示筛选`.
  - INSTANCE_SWAP: `sortState 排序状态`.
- `Data Display / Jinyumeng Table / Content Text`: set `4972:8909`, 14px component `4972:8910`.
- `Data Display / Jinyumeng Table / Content Cell`: set `4972:8914`, xlarge component `4972:8915`.
- `Data Display / Jinyumeng Table / Selection Cell`: set `4972:53985`, xlarge component `4972:53986`.
- `Data Display / Jinyumeng Table / Row`: set `4972:54013`, xlarge component `4972:54014`.
- `Data Display / Jinyumeng Table / Shell`: set `4975:9829`.
  - `selection 选择列=on 显示`: component `4975:9830`.
  - `selection 选择列=off 隐藏`: component `4975:9855`.
- The table family exposes only `size 尺寸=xlarge 超大 48px` and `type 类型=basic 基础`. Content cells and rows keep their Slot properties; the Shell keeps header, rows, and pagination slots.
- In the selection-on Shell, the Header Selection Cell background uses `背景色/--qifu-bg-color-canvas`; its nested checkbox 方框本体保持白色. Data-row Selection Cells keep the normal white row background.
- All Jinyumeng Table sets use the existing `金毓盟/Light` mode. They do not replace or mutate any existing Table component.

## Confirmed shared table content

- Row-operation component set: `Data Display / Table / Cell Content / Action Content-V2`, node `3678:8875`. Its generic component path and mode-aware basic semantic link color establish it as a 共享基础表格内容组件, not a platform-owned component.
- Its text properties are `action1 文案` through `action4 文案`; Boolean properties `showAction2 显示动作2` through `showAction4 显示动作4` control 1–4 visible actions.
- `dangerAction 危险项` options are `None 无`, `Action1 动作1`, `Action2 动作2`, `Action3 动作3`, and `Action4 动作4`. All non-danger actions resolve to 金毓盟主题色 when the containing page uses `金毓盟/Light`.
- 表格状态 Tag reuses `Data Display / Tag / Tag`, node `3178:9659`; list-table status uses `variant=light`, `size=medium`, `shape=square`, icon off, and close off.
- Theme mapping is closed: 成功/启用=`success`, 失败/禁用=`danger`, 等待=`warning`, 运行/处理中=`primary`, 中性=`default`. An unknown semantic remains BLOCKED instead of receiving a guessed theme.

## Confirmed shared pagination

- Pagination component set: `Navigation / Pagination / Pagination`, node `3698:482`.
- The Jinyumeng Shell's default nested instance is component `3698:483`, `size 尺寸=medium 默认`, `pageCount 页数=6+ 多页`.
- Relevant properties are `pageCount 页数`, `current 当前页`, `total 总数`, `pageSize 每页条数`, `jump 跳转页`, `jumpTotal 跳转总页数`, `showTotal 显示总数`, `showPageSize 显示每页条数`, and `showJumper 显示快速跳转`.
- Pagination remains a shared nested instance inside the Jinyumeng Shell `paginationSlot`; do not detach it or replace it with a platform copy.
- Its visual contract is 上一页箭头向左, 下一页箭头向右, ascending numeric pages, and one selected current page. The confirmed current-page-2 example reads `← 1 2（当前页）3 4 5 … 8 →`.

## Confirmed shared feedback components

- `Data Display / Loading / Spinner`, component set `3267:8`, provides `size 尺寸=small/medium/large`.
- `Data Display / Loading / Loading`, component set `3268:29`.
  - TEXT property: `text 提示文案`.
  - `content 内容` options: icon, text, and icon+text.
  - `size 尺寸` options: small, medium, and large.
- `Data Display 数据展示 / Empty 空状态 / Empty`, component set `3621:45`.
  - BOOLEAN properties: `showDescription 显示描述`, `showAction 显示操作`.
  - TEXT property: `description 描述`.
  - `status 状态` options: `noData 暂无数据`, `building 建设中`, `networkError 网络错误`, `success 成功`, and `error 失败`.
  - `size 尺寸` options: small, medium, and large.
- These are shared-basic feedback components. Their component identities are closed; page-level placement remains governed by page-rules.md.

The component map is complete for the current Jinyumeng list-page scope. 正式写入按用户指定目标执行，并逐次完成布局与整页验收。
