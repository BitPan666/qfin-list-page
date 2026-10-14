# 电销组件映射

## 来源与边界

- 目标文件：`奇富科技中后台组件库-新`，file key `gTV3VdC6a5e9vpkRHIZSXA`。
- 节点 ID 仅用于同文件实例化；失效时按精确组件名称重新发现。
- 平台专属 Header、SideMenu、Shell 不得由其他平台组件替代。

## 已确认导航组件

| 能力 | 组件 | 节点 | 状态 |
| --- | --- | --- | --- |
| 顶层菜单分类 | `Navigation / Dianxiao SideMenu / MenuRoot` | `5762:1537` | CONFIRMED |
| 业务菜单项 | `Navigation / Dianxiao SideMenu / SideMenuItem` | `5763:1753` | CONFIRMED |
| 顶部 Header | `Navigation / HeaderMenu / Dianxiao Header` | `5824:4491` | CONFIRMED |

`SideMenuItem` 覆盖 Level 1/2/3、是否有子集、Default/Selected/Hover/Disabled 和展开收起结构；一级通过 Instance swap 绑定 `Icon/dianxiao/*`。实际属性 Key 必须从实例 `componentProperties` 动态解析。

`Dianxiao Header` 为固定结构组件：`1366 × 56px`、左右内边距 `20px`、透明背景，显式使用 `电销/Light` 模式。左侧固定 CiFU 品牌与 `客户销售平台 - 借条`，右侧固定签到、小蜜开关、空闲状态、外呼设置、企微、消息和用户头像；当前不暴露业务可写属性，页面生成时直接实例化，不得拆散或重画。

## 已确认共享基础组件

| 能力 | 组件 | 节点 | 电销用法 |
| --- | --- | --- | --- |
| 内页签 | `Data Display / Tag / Tag` | `3178:9659` | 12px，默认/主题选中 |
| Input | `录入组件 / Input / Base-V2` | `3406:853` | 固定 `200px × 28px` |
| Select | `录入组件 / Select / Base` | `2859:2820` | 固定 `200px × 28px` |
| DatePicker | `录入组件 / DatePicker / Input / Date` | `2967:29996` | 固定 `200px × 28px` |
| DateRange | `录入组件 / DatePicker / Input / DateRange` | `2967:30327` | 固定 `200px × 28px` |
| Button | `Base / Button / Button` | `2381:2318` | 12px，电销主题模式 |
| Table Shell | `Data Display / Table / Shell-V2` | `3433:8257` | basic，动态 Slot |
| Header Cell | `Data Display / Table / Header Cell-V2` | `3350:5949` | `headerFont=12px`，已完成整表回读 |
| Row | `Data Display / Table / Row-V2` | `3393:6352` | 与 Shell 同尺寸/类型 |
| Content Cell | `Data Display / Table / Content Cell-V2` | `3376:33871` | 动态 contentSlot |
| Text content | `Data Display / Table / Cell Content / Text-V2` | `3368:6025` | `contentFont=12px` |
| Action content | `Data Display / Table / Cell Content / Action Content-V2` | `3678:8875` | 1–4 个操作；组件无字号属性，需对实例内可见操作文字覆盖为 12px 并回读 |
| Pagination | `Navigation / Pagination / Pagination` | `3698:482` | 12px；放入表格宽度容器，右侧 20px |

## 页面 Shell

| 能力 | 组件 | 节点 | 状态 |
| --- | --- | --- | --- |
| 电销 Content Shell | `Templates / Dianxiao / Content Shell` | `5829:15` | CONFIRMED |
| 电销 Workspace Shell | `Templates / Dianxiao / Workspace Shell` | `5829:24` | CONFIRMED |
| 电销 List Page Shell | `Templates / Dianxiao / List Page Shell` | `5829:31` | CONFIRMED |

`Content Shell` 固定为 `1118 × 668px`、垂直间距 `12px`，显式使用 `电销/Light`，只包含三个原生 Slot：

- `tabsSlot 系统内页签插槽`：`1118 × 38px`；
- `filterSlot 筛选区插槽`：`1118 × 104px`；
- `tableSlot 表格内容区插槽`：`1118 × 502px`，承载可选标题、列表操作、12px 动态表格与分页。

三个承载面均绑定 `背景色/--qifu-bg-color-surface` 与 `--qifu-radius-8`。不存在 `actionSlot` 或 `showActionBar`；禁止在实例中补画独立操作栏。

表格内容区规则：标题默认隐藏、可由提示词开启；操作按钮默认左对齐；左侧按钮组距白色承载面左侧和顶部均为 `20px`，按主按钮 → 次按钮排序；表格距白色承载面左右各 `20px`，因此 1366px 基准画板中的表格实际可视宽度为 `1078px`。

`Workspace Shell` 固定为 `1366 × 712px`：`200px sidebarSlot + 28px gap + 1118px Content Shell + 20px 右边距`。`List Page Shell` 固定为 `1366 × 768px`，由 `Dianxiao Header 1366 × 56px` 与 `Workspace Shell 1366 × 712px` 组成，并显式使用 `电销/Light` 模式。

不得直接调用毓数或金毓盟 Shell 充当电销 Shell；页面必须从以上三个电销专属组件解析并实例化。

## P0 组件 blockers

无。Header、SideMenu、17 个一级菜单图标、页面 Shell、筛选基础组件、12px 动态表格与分页均已完成真实组件映射。

Skill 为 `readiness=ready`，已获用户授权正式使用；每次仍需检查真实组件与页面。

## 12px 动态表格验证结论

- 已用真实 Table Shell、Header Cell、Row、Content Cell、Text、Tag、Action Content 与 Pagination 实例完成验证。
- 验证样本为 5 列、2 行、10 个内容单元格；26 个可见文本节点全部回读为 12px。
- Header Cell 使用 `headerFont=12px`；Text 使用 `contentFont=12px`；Tag 与 Pagination 原生为 12px。
- Action Content 当前没有字号属性。设置操作数量、文案与危险态后，必须加载实例内文本所需字体，再将每个可见操作 TEXT 覆盖为 12px、行高 20px，最后遍历整表文本回读。
- Table Shell 内部分页 Slot 的母版宽度可能仍为 1248px。页面表格宽度为 1078px 时，将分页 Slot 的 `primaryAxisAlignItems` 设为 `MIN`，在其内部放置宽 1078px、右内边距 20px、`MAX` 对齐的分页容器；验证回读右间距为 20px。
- 自定义数据行少于母版默认行数时，必须让分页紧跟真实 rows 内容，并保留 12px 顶距。若共享 Table Shell 的 Slot 几何不能在实例中覆盖，则使用仅负责布局的电销表格组装 Frame，内部 Header Cell、Row、Content Cell、Tag、Action Content 与 Pagination 仍全部使用真实实例；不得把该 Frame 冒充发布组件。
