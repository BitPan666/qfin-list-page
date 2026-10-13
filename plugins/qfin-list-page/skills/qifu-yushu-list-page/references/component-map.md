# 奇富组件映射与缺口

## 目录

- [来源](#1-来源)
- [调用边界](#2-调用边界)
- [页面骨架与导航](#3-页面骨架与导航)
- [筛选与动作](#4-筛选与动作)
- [表格、状态与分页](#5-表格状态与分页)
- [Table Shell V2 Slot 替换后的逐层同步](#table-shell-v2-slot-替换后的逐层同步强制)
- [已确认缺口](#6-已确认缺口)
- [运行时缺口记录格式](#7-运行时缺口记录格式)

## 1. 来源

- 组件库文件：`奇富科技中后台组件库 新`
- 文件 Key：`gTV3VdC6a5e9vpkRHIZSXA`
- 本映射盘点日期：2026-08-18

节点 ID 用于同文件创建实例；发布 Key 用于其他文件导入。若节点已重建，按精确组件集名称重新发现，并更新本映射。

## 2. 调用边界

本文件回答“选择哪个组件”。真实属性 Key、属性类型、INSTANCE_SWAP、Slot 写入顺序和回读规则以 [组件调用契约](component-invocation-contract.md) 为准；交付门禁以 [页面结构化验收契约](structural-validation.md) 为准。

表格中的属性名是稳定逻辑名称，不保证等于 Figma 运行时返回的完整 Key。创建实例后必须读取 `componentProperties` 动态解析；禁止把 `Label#2405:0` 等当前内部后缀固化为长期接口。

## 3. 页面骨架与导航

| 用途 | 组件集 | 节点 ID | 发布 Key | 关键属性 |
| --- | --- | --- | --- | --- |
| 顶部菜单 | `Navigation / HeaderMenu / HeaderMenu` | `2525:2226` | `b2b586e04aa149f802fb6b4fad502ef7f25c276e` | `Icon`、`Logo`、`Items=1..8`、4 个 Action Icon swap |
| 毓数顶部菜单 V2 | `Navigation / HeaderMenu / Yushu Header-V2` | `3639:1529` | `13dd3304a68853196f2a683bba7ebd034e2928ee` | `activeMenu 当前菜单=QBI/数据资产/自助查询/数据开发/指标管理`；固定 Logo、右侧图标、头像和 `panyue` |
| 顶部菜单项 | `Navigation / HeaderMenu / HeaderMenuItem` | `2525:1111` | `af3b9a17fd68b4a6b9943e91369d864ef9cb4126` | `Icon`、`State=Default/Selected/Hover/Disabled` |
| 侧边菜单 | `Navigation / SideMenu / SideMenu` | `2406:461` | `0e8b19f82f0b069b5f68e1a7140087532de52167` | `Selected Case` 6 种结构 |
| 侧边菜单项 V2 | `Navigation / SideMenu / SideMenuItem-V2` | `3650:998` | `cee1612d682da5860d488abc732321c3fd15ad44` | 36 个有效变体；`Label` 已全部接线；`Level=1/2/3`、`Has Submenu`、`State`、`expanded 展开=False/True` 均可按 PageSpec 配置；一级菜单支持 `icon 图标`、`showIcon 显示图标`，可通过真实 Icon ComponentNode 做 INSTANCE_SWAP；有子菜单的 `State=Selected` 用于祖先路径高亮（白底，文字/图标/箭头主题绿），无子菜单的 `State=Selected` 用于当前页选中 |
| 侧边菜单项（原版兼容） | `Navigation / SideMenu / SideMenuItem` | `2405:81` | `d3804303308830deced4bad8d4369b6ddff2d3f1` | 仅兼容旧页面；新页面改用 V2 |
| 选项卡 | `Navigation / Tabs / Tabs` | `2695:4651` | `501fcf9f50619e0680ec6886b657356cc0b3d991` | `type`、`size`、`item=2..5`、`active=1..5` |
| 选项卡项 | `Navigation / Tabs / TabItem` | `2695:3345` | `a314f0d8db2719a4bfb79ca6e594d8cd3101df40` | `type=line/card/pill`、`size`、`state` |
| 普通列表内容外壳 V2 | `Templates / List Page Shell-V2` | `3478:657` | `6e26dad1245c1a7445593586454d6b2c73ff5433` | `pageHeaderSlot`、`filterBarSlot`、`tableSlot`、`showPageHeader`、`showFilterBar`；三个 Slot 使用内容高度 |

本文件只记录组件解析与实现限制。页面结构和 List Action Bar 组合方式以 `page-rules.md` 为准；毓数默认菜单与自定义导航输入语义以 `platform-yushu.md` 为准。需要自定义业务文案、层级、子集或图标时按调用契约动态解析属性：契约声明存在但当前写入失败属于执行失败；只有核对母版后确认未暴露该能力，才记录组件缺口。

## 4. 筛选与动作

| 用途 | 组件集 | 节点 ID | 发布 Key | 关键属性 |
| --- | --- | --- | --- | --- |
| Checkbox | `录入组件 / Checkbox / Base` | `2939:1619` | `c333aa369828e3ac2b048d86c7f0de4f49f84f55` | `label`、`showLabel`、`size`、`selected`、`state` |
| CheckboxGroup | `录入组件 / CheckboxGroup / Base` | `2939:3229` | `423d78d13afdd2570f3fdd9e4b9a78632e60326f` | `size`、`direction`、`count`、`selection`、`state` |
| Select | `录入组件 / Select / Base` | `2859:2820` | `1684c11d727996e0a41ebee921cf15444e395d8d` | `value`、`mode`、`size=SM/MD/LG`、`state`、prefix/clear/search/suffix/tag 布尔属性 |
| SelectOption | `录入组件 / SelectOption / Base` | `2956:3075` | `b21f458276a4d340edf099edcd70979ea63fcb91` | `label`、`secondary`、`mode`、`size`、`state` |
| SelectMenu | `录入组件 / SelectMenu / Base` | `2956:4351` | `bbe51d5f5b4c50cb008555542075bc06b03b66cb` | `mode`、`size`、`count=3/5/8` |
| Input | `录入组件 / Input / Base-V2` | `3406:853` | `f6965b0cf3ba42edbcf5117df75815cb1c2f83cc` | `value 文本`、prefix/suffix/clear/count 布尔属性、`size=S/M`、`content=Placeholder/Value`、`state=Default/Hover/Focus/Disabled/Error` |
| Search | `录入组件 / Search / Base` | `2981:26533` | `01521850eb1471295750388e5f4fd4489f420a1b` | `trigger=Icon/Button`、`size=S/M/L`、`state`、`filled`、`placeholder 文案`、`value 文案` |
| Cascader | `录入组件 / Cascader / Base` | `2956:6810` | `2f2cc0098d70676c0c578ee2cea223b4fb590890` | `path`、`mode`、`size`、`state`、prefix/clear/search/suffix/tag 布尔属性 |
| DatePicker | `录入组件 / DatePicker / Input / Date` | `2967:29996` | `bc43d0df1a94ac7bbd4ac1e09e0539a5e4ff7b11` | `placeholder`、`value`、`clear`、`size`、`state`、`filled` |
| DateRange | `录入组件 / DatePicker / Input / DateRange` | `2967:30327` | `b11b9b940a5a173c6e97e37be9be4a028f9bd633` | `placeholder`、`value`、`clear`、`size`、`state`、`filled` |
| Button | `Base / Button / Button` | `2381:2318` | `392ccbc18826879de80cd0b10e5c995db5184d69` | `text`、`icon`、`variant=base/outline/dash/text/link`、`size`、`icon type`、`state` |
| 筛选项 V2 | `Data Display / Filter Item-V2` | `3802:107` | `fb86bfd8dd7f66b3b6c6d1a8420462b5bd943b71` | `display 显示形式=直接筛选框/带标题筛选项`、`size 尺寸=28px/32px`、`label 标题`、`controlSlot 筛选控件插槽`；标题分别为 12px/14px、`#565656`，标题与控件原生间距 0px；小屏非日期控件可统一缩至 180px，父行优先 4 项并均分项间剩余空间 |
| 筛选工具栏 V2 | `Data Display / Filter Bar-V2` | `3473:36837` | `23e9770f30375f5dcb0d10b7cf102b9ac72d98e7` | 5 个 Slot：常用筛选、更多筛选、快捷条件、查询操作、主操作；`expanded 展开=false/true × trigger 触发方式=实时触发/按钮触发` 共 4 个变体；布尔属性为 `showQuickFilters`、`showPrimaryAction` |

### Input V2 使用原则

新建列表页统一使用 `录入组件 / Input / Base-V2`，通过 `size 尺寸`、`content 内容`、`state 状态` 和 `value 文本` 设置输入框。需要图标或辅助能力时使用 `prefixIcon 前置图标`、`suffixIcon 后置图标`、`clearable 清空`、`count 字数` 布尔属性；不得继续拼接旧版独立 Input 组件。

旧版独立 Input 保留在文件中以兼容已有画板，但不再作为新页面的默认引用。

### 32px 常规大规格映射

标准数据表格页默认使用以下统一高度映射：

| 页面语义 | 组件属性值 | 实际高度 |
| --- | --- | ---: |
| Filter Item V2 | `size 尺寸=32px` | 32px |
| Input V2 | `size 尺寸=M 默认尺寸` | 32px |
| Select | `size 尺寸=LG 大尺寸` | 32px |
| Button | `size 尺寸=large 大尺寸` | 32px |

“常规大规格”是页面 Skill 的统一称呼，不改动各组件现有属性命名。仅在用户明确要求紧凑模式时改用小尺寸。

Input V2 的 `M 默认尺寸` 已是原生 32px：16px 图标垂直居中于 y=8，20px 文本垂直居中于 y=6。生成后仍需检查 Filter Bar 的 Row 与 Slot 同为 32px、垂直居中且不裁切，但不再对 Input 实例做额外高度覆盖。

## 5. 表格、状态与分页

| 用途 | 组件集 | 节点 ID | 发布 Key | 关键属性 |
| --- | --- | --- | --- | --- |
| 表格外壳 V2 | `Data Display / Table / Shell-V2` | `3433:8257` | `51894113014dc682f0fbb697f4cf5ad749a418a6` | `size`、`type`、`selection`；`headerSlot`、`rowsSlot`、`paginationSlot`；18 个变体的 paginationSlot 均为上下 12px、左右 0；选择列开关均保持 1248px 默认宽度 |
| 表头单元格 V2 | `Data Display / Table / Header Cell-V2` | `3350:5949` | `a86f55d1c20b3a7fc777ce3cdfdf04d1e25a1d48` | `headerText`、`showSort`、`showFilter`、`sortState`、`size`、`headerFont`、`divider` |
| 排序状态 V2 | `Data Display / Table / Sort Indicator-V2` | `3350:5919` | `674dbbff05ef4db76564858f7d4ef9f13e9c6003` | `state=default/asc/desc`，由 Header Cell-V2 的 `sortState` 切换 |
| 内容单元格 V2 | `Data Display / Table / Content Cell-V2` | `3376:33871` | `6c5b55855b91df1e13ca81fe8aefb65e9999ff3e` | `contentSlot`、`size`、`background`、`divider` |
| 数据行 V2 | `Data Display / Table / Row-V2` | `3393:6352` | `664e352544bee819c99b4de41284c9ac9d5d9901` | `cellsSlot`、`size`、`background`、`divider` |
| 选择单元格 V2 | `Data Display / Table / Selection Cell-V2` | `3418:34040` | `98d12bfe7f1002a9ded85775369e6f76b2a3531a` | 固定 48px，嵌套并暴露 Checkbox；`size`、`background`、`divider` |
| 文本内容 V2 | `Data Display / Table / Cell Content / Text-V2` | `3368:6025` | `51d09b477c04116ed5d16e1a19a0d1a926dae49f` | `value`、`contentFont=14px/12px` |
| 状态内容 V2 | `Data Display / Table / Cell Content / Status-V2` | `3491:8894` | `d903d3fb91e052ff713beafe22e72e39d3594fcb` | 仅兼容明确要求额外状态内容能力的页面；新列表页所有普通状态标签统一使用下方 Tag。若使用本组件，其内部真实 Tag 也必须可写并回读为 `medium/square`，否则判 `FAIL` |
| 操作内容 V2 | `Data Display / Table / Cell Content / Action Content-V2` | `3678:8875` | `eb3a6d86f44bbb9f4e811e23300898c3f9259deb` | `action1..4`、`showAction2..4`；`dangerAction=None/Action1/Action2/Action3/Action4`，支持 1–4 个紧凑操作且最多标记一个危险项 |
| 表头单元格 | `Data Display / Table / Header Cell` | `3234:7927` | `af0a8d220aa801d708a6eb5a5cec58686d3d1209` | `label`、sort/filter/asc/desc、`size`、`headerFont`、`divider` |
| 内容单元格 | `Data Display / Table / Content Cell` | `3234:8027` | `55ee73644b95fd0a20408a85eeefba5df69fa3ea` | `value`、`size`、`contentFont`、`background`、`divider`、`content=text/action` |
| 表格列 | `Data Display / Table / Column` | `3234:8271` | `3cc97b002d72777c8e0986fa80cd6f08859df023` | `type=basic/bordered/stripe`、`size`、`contentFont`、`content` |
| 固定整表 | `Data Display / Table / Table` | `3234:8525` | `f35bf5473bb6138c813aaac0cd1abb68b2ce0f21` | `type`、`size`、`contentFont` |
| 标签 | `Data Display / Tag / Tag` | `3178:9659` | `a804e46f1544bd11fe932da5a86f04ea18d65bda` | 所有列表状态标签：`variant=light`、`size=medium`、`shape=square`、`disabled=false`、icon=false、close=false；`theme` 按语义映射，成功/启用=`success`、失败/禁用=`danger`、等待=`warning`、运行/处理中=`primary`。规则适用于所有文案和状态数量，不仅限启用/禁用 |
| 空状态 | `Data Display / Empty / Empty` | `3447:134` | `4f33759f3944920ed616a87abb0cb67ed82aa4e1` | `status=NoData/NoResult/Network/NoPermission/Failed`、`size=S/M/L`、title/description 文本、描述/操作布尔属性 |
| 分页 V2 | `Navigation / Pagination / Pagination-V2` | `3698:482` | `57f5f847efd41f61f15c32aed8b2d4a48885f871` | `size=medium/small`；`pageCount=1/2/3/4/5/6+`；`showTotal`、`showPageSize`、`showJumper`；`total`、`current`、`pageSize`、`jump`、`endPage`、`jumpTotal` |
| 分页（旧版） | `Navigation / Pagination / Pagination` | `2597:2086` | `30f50ef8e07569627f467a7f9e025bdc896dcf77` | 保留完整 default/simple 与 32 个旧组合变体，仅兼容旧页面 |
| 加载状态 | `Data Display / Loading / Loading` | `3268:29` | `19c936c5a0383d80a984eb1ac4350daf39d89c81` | `text`、`content=icon/text/icon+text`、`size` |
| 危险操作确认 | `通知反馈 / Popconfirm / Popconfirm` | `3302:45015` | `4bbd515fd95cea014f8236e557ecda04f93c5608` | title/description 文案、icon/description/arrow、placement、theme |

新页面优先使用 V2 表格组件；原版 Header Cell、Content Cell、Column、固定 Table 与旧版 Pagination 只兼容旧页面。页面级列宽、状态、操作和分页决策以 `page-rules.md` 为准，具体变体与 Slot 同步按下节执行。

### Table Shell V2 Slot 替换后的逐层同步（强制）

Table Shell-V2 的 `size`、`type`、`selection` 只决定母版默认 Slot 内容。业务页面替换 `headerSlot` 或 `rowsSlot` 后，这些属性不会继续影响自定义 Header Cell-V2、Row-V2、Content Cell-V2 或 Selection Cell-V2。先记录唯一的 `TableStyleSpec`，再按下表逐层写入；不得依赖外壳变体自动传播。

| `TableStyleSpec` 维度 | Table Shell-V2 | Header Cell-V2 | Row-V2 | Content Cell-V2 | Selection Cell-V2 |
| --- | --- | --- | --- | --- | --- |
| `size` | 选择 `large 大 44px`、`medium 中 40px` 或 `small 小 36px` | 每个表头使用相同 `size` | 每行使用相同 `size` | 每个内容单元格使用相同 `size` | 表头与每行选择单元格使用相同 `size` |
| `type=basic 基础` | `type 类型=basic 基础` | `divider=horizontal` | `background=default`、`divider=horizontal` | `background=default`、`divider=horizontal` | 表头选择单元格绑定 `背景色/--qifu-bg-color-canvas`；数据行选择单元格 `background=default`、`divider=horizontal` |
| `type=bordered 边框线` | `type 类型=bordered 边框线` | `divider=both` | `background=default`、`divider=both` | `background=default`、`divider=both` | 表头选择单元格绑定 `背景色/--qifu-bg-color-canvas`；数据行选择单元格 `background=default`、`divider=both` |
| `type=stripe 斑马纹` | `type 类型=stripe 斑马纹` | `divider=horizontal` | 奇偶行按 `default/stripe` 交替，`divider=horizontal` | 跟随所属 Row 的 `background`，`divider=horizontal` | 表头选择单元格绑定 `背景色/--qifu-bg-color-canvas`；数据行选择单元格跟随所属 Row 的 `background`、`divider=horizontal` |
| `selection=off 隐藏` | `selection 选择列=off 隐藏` | 第一业务列直接开始 | 不插入选择单元格 | 不变 | 数量必须为 0 |
| `selection=on 显示` | `selection 选择列=on 显示` | 第一业务列前插入一个 Selection Cell-V2 | 每行第一业务列前插入一个 Selection Cell-V2 | 不变 | 总数必须为“数据行数 + 1”，并同步 `size/background/divider` |

同步顺序：

1. 设置 Table Shell V2 的 `size/type/selection`。
2. 替换 `headerSlot` 后，遍历全部 Header Cell-V2，并按同一个 `TableStyleSpec` 设置 `size/divider`；若显示选择列，表头 Selection Cell-V2 的根节点 `fills` 必须绑定 `背景色/--qifu-bg-color-canvas`，与其他表头单元格保持同色，不得沿用数据行的 surface 背景。这里只检查 Selection Cell 根背景，不把嵌套 Checkbox 方框自身的填充误判为表头背景。
3. 替换 `rowsSlot` 后，先设置每个 Row-V2，再遍历该行全部 Content Cell-V2；斑马纹背景必须同时写到 Row、Content Cell 和 Selection Cell-V2。
4. 按 `selection` 显式插入或移除选择单元格，不依赖 Shell 自动增删。
5. 独立配置 `paginationSlot`。Pagination-V2 不继承表格的 `size/type/selection`；先计算 `pageCount=ceil(total/pageSize)`，选择对应页数变体，再设置 `size`、三个区域布尔属性和文案属性。
6. 自定义行数与母版默认行数不一致时，变体切换会把 Table Shell 实例恢复为母版固定高度，但自定义 `rowsSlot` 仍保留真实内容高度，造成后续行与分页被外壳裁切。计算 `requiredTableHeight = headerSlot.height + rowsSlot.height + paginationSlot.height`，显式调整 Table Shell 实例高度，并确认外层 `tableSlot` 和 List Page Shell 随内容重新包裹。
7. 最后按节点类型统计并抽查属性：表头数等于列数，Row 数等于数据行数，每行 Content Cell 数等于业务列数，Selection Cell 数只允许为 0 或“数据行数 + 1”；同时检查 `paginationSlot.y + paginationSlot.height <= Table Shell.height`。

## 6. 已确认缺口

### P0：直接影响普通列表页自动生成

1. **Header Cell-V2 动作组起点对齐**
   - 现状：操作列动作组整体右对齐，但表头文字需要与动作组第一个文案的左边缘对齐；Header Cell-V2 未暴露该能力。
   - 当前回退：页面级 `Fallback / Header Cell / 操作 / Align to Action Group`，继承 Header Cell-V2 的背景、描边和文字样式，并使用与 Action Content-V2 相同宽度的内部对齐组。
   - 已验证限制：嵌套 Action Content 的文案属性可以持久化，但嵌套实例或内部 Frame 的几何宽度覆盖会在后续渲染恢复母版值，无法可靠用一个 `contentAlign` 变体承载任意动作文案宽度。
   - 后续方向：继续使用页面级精确回退；只有 Figma 支持持久化的数值宽度属性，或真实业务收敛出少量固定动作组宽度档位时，再组件化为 V2。

### P1：提升还原度和复用质量

2. **WorkspaceTabs / 可关闭页签**
   - 需要 selected、hover、disabled、closable、dirty/status dot、icon、item count 和 overflow。
   - 普通 Tabs 或 closable Tag 只能作为临时降级。

3. **Status / 紧凑状态点**
   - Status Content V2 内含五种 Tag 状态，但不作为新列表页普通状态标签的默认入口；普通状态仍直接使用 `Data Display / Tag / Tag` 并遵循全量 `medium/square` 契约。
   - 当前尚缺 `dot + text` 表现。需要 default/success/warning/error/disabled 语义与自定义文案；补齐前仅在 PageSpec 明确要求该额外能力时使用受限降级。

4. **页面外壳响应式宽度**
   - List Page Shell V2 与 Table Shell V2 的默认内容宽度为 1248px；选择列开关已不会导致跳宽。
   - 已验证 `1366 × 768` 页面可在 200px SideMenu、Content 外边距 12px、Page Surface 内边距 16px 下，将 List Page Shell 和 Table Shell 调整为 1110px。
   - 已在临时副本中验证：仅把根画板从 `1366 × 768` resize 为 `1920 × 1080` 时，Workspace 与 Content 会扩展，但 Page Surface 仍保持 1142px，List Page Shell 与 Table Shell 仍保持 1110px，不会自动使用宽屏剩余空间。
   - 生成 `1920 × 1080` 版本时必须显式把 Page Surface 调整为 `Content - 24px`，把 List Page Shell 与 Table Shell 调整为 `Page Surface - 32px`，并重新分配表头和所有数据行的列宽；不得只 resize 根画板。后续可考虑为页面外壳和表格增加响应式宽度属性。

5. **Action Content 更多操作**
   - Action Content V2 已支持 1–4 个动作、独立文案和单一危险项语义。
   - 超过 4 个操作时仍缺少原生 overflow；当前使用页面级更多菜单并记录缺口，后续根据真实场景再决定是否补 `More Actions-V2`。


6. **Pagination-V2 非首页逻辑**
   - 已解决：Skill 可根据 `total / pageSize` 计算 1 / 2 / 3 / 4 / 5 / 6+ 页，单页和少页不再显示多余页码。
   - 剩余限制：V2 默认展示第一页；当提示词明确要求当前页大于 1 时，仍不会自动重算选中位置、相邻页窗口和首末箭头状态。
   - 当前处理：普通列表默认首屏不记录缺口；只有明确生成非首页状态时，才使用页面级受控分页并记录缺口。

## 7. 运行时缺口记录格式

在页面右侧的 `Audit / Missing Components` 使用：

```text
Capability: WorkspaceTabs / closable
Scenario: 多任务工作区，当前页签可关闭并显示未读点
Fallback: Navigation / Tabs / Tabs + 独立关闭图标
Recommendation:
- item count: 1..N
- active item: 1..N
- closable: true/false
- status: none/dot/dirty
- overflow: none/scroll/more
```

只记录本次页面实际遇到的缺口，不把完整待办列表复制到每张页面。
