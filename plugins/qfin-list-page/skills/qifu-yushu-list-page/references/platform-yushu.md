# 毓数平台导航基线

## 目录

- [适用范围](#1-适用范围)
- [导航模式与输入契约](#2-导航模式与输入契约)
- [顶部导航](#3-顶部导航)
- [默认侧栏菜单预设](#4-默认侧栏菜单预设)
- [默认侧栏图标映射](#5-默认侧栏图标映射)
- [组装规则](#6-组装规则)
- [输入解析示例](#7-输入解析示例)

## 1. 适用范围

当前标准数据表格页默认以毓数平台为基准。用户明确指定其他平台时，不套用本文件的菜单名称；先读取对应平台参考，缺少参考时仅询问会改变页面框架的导航信息。

平台规格使用以下字段：

```text
platform=yushu
navigationMode=yushuPreset|custom；未填默认 yushuPreset
headerActive    数据资产 | 自助查询 | 数据开发 | 指标管理 | QBI
sideActive      当前页面所在的侧栏菜单
sideActiveLevel 1 | 2 | 3；固定等于 sidePath.length
sideExpanded[]  当前展开的父菜单；固定等于 sidePath 中除最后一项外的祖先
sideAncestorsActive[] 当前页的祖先菜单；固定等于 sideExpanded[]
sidePath[]      从一级菜单到当前页面的完整路径
```

`sideActive` 固定为 `sidePath` 最后一项并决定唯一当前菜单。只有当前路径祖先可以进入 `sideExpanded` 与 `sideAncestorsActive`；其他一级菜单即使有子集也必须收起，其他二级菜单即使有子集也只显示箭头、不展开三级菜单。

## 2. 导航模式与输入契约

### 2.1 默认模式

`navigationMode=yushuPreset` 或用户未填写导航模式时，使用本文件第 4、5 节的毓数默认菜单树和图标映射。用户只需给出 `sidePath`，该路径必须存在于默认树；不存在时停止并请用户改用自定义模式或确认真实父级，不能把新文案自动追加为一级菜单。

### 2.2 自定义模式

`navigationMode=custom` 时，提示词只提供业务输入，Skill 负责生成层级、箭头、展开与选中状态。PageSpec 必须包含：

```text
customSideMenu.level1[]:
  label
  iconComponentName   完整、唯一的真实组件名，格式 Icon/<system>/<purpose>
  hasChildren         true|false

customSideMenu.activeLevel1Children[]:
  label
  hasChildren         true|false

customSideMenu.activeLevel2Children[]:
  label               sidePath 为三级时必填；否则为空
```

解析与完整性规则：

1. `sidePath` 只能有 1–3 段，最后一段是唯一 `sideActive`，段数即 `sideActiveLevel`。
2. `sidePath[0]` 必须在 `level1[]` 中恰好出现一次；路径超过一级时，该项 `hasChildren=true`。
3. 当前一级菜单的全部可见二级项放入 `activeLevel1Children[]`；每项都必须填写 `hasChildren`，用于决定是否显示展开箭头。
4. 路径超过二级时，`sidePath[1]` 必须在 `activeLevel1Children[]` 中恰好出现一次且 `hasChildren=true`；其全部可见三级项放入 `activeLevel2Children[]`，并且 `sidePath[2]` 必须存在其中。
5. 未位于当前路径的一级菜单只需提供 `hasChildren`，始终保持收起，不要求填写其二、三级内容。
6. 未位于当前路径的二级菜单即使 `hasChildren=true` 也保持收起，不要求填写其三级内容。
7. 每个一级 `iconComponentName` 必须在目标组件库中按完整名称精确匹配到一个 ComponentNode，并通过 SideMenuItem-V2 的 `icon 图标` INSTANCE_SWAP 写入；名称缺失、同名多解或交换失败均停止报告，不使用 Node ID 提示词、不模糊匹配、不绘制替代图标。

## 3. 顶部导航

使用真实组件：

- 组件集：`Navigation / HeaderMenu / Yushu Header-V2`
- 节点 ID：`3639:1529`
- 发布 Key：`13dd3304a68853196f2a683bba7ebd034e2928ee`
- 属性：`activeMenu 当前菜单`
- 画板宽度：1366px；放入宽屏页面时横向填充，保持 48px 高。

固定内容：

- 左侧 Logo；
- 菜单顺序：数据资产、自助查询、数据开发、指标管理、QBI；
- 四个中文顶部菜单文案统一使用 `PingFang SC / Regular / 14px`；不得用 `Inter` 渲染中文。若 Yushu Header-V2 实例继承了 Inter，在当前页面实例内覆盖字体但保持实例关系，并截图确认“数据资产 / 自助查询 / 数据开发 / 指标管理”均完整显示，不得只显示末尾单字或简称。
- 右侧功能图标顺序：帮助、通知、申请工单、问题上报；
- 头像使用毓数默认头像；
- 用户名固定为 `panyue`；
- 用户名右侧保留下拉箭头。

用户指定顶部入口时设置对应 `activeMenu 当前菜单`。未指定时：

1. 根据页面业务推断入口；
2. 无可靠映射时默认 QBI；
3. 不因侧栏菜单名称擅自新增顶部菜单。

## 4. 默认侧栏菜单预设

当前已确认的一级结构：

```text
探索分析
智能分析
├── 智能探查
└── 智能报表
仪表板
图表管理
在线Excel
数据集
数据源
订阅管理
├── 订阅计划
└── 群组管理
权限管理
├── 用户授权
└── 角色授权
归因配置
```

结构属性：

| 菜单 | Level | Has Submenu | 默认展开 | 已确认子项 |
| --- | ---: | --- | --- | --- |
| 探索分析 | 1 | False | — | — |
| 智能分析 | 1 | True | False | 智能探查、智能报表 |
| 智能探查 | 2 | False | — | — |
| 智能报表 | 2 | False | — | — |
| 仪表板 | 1 | False | — | — |
| 图表管理 | 1 | False | — | — |
| 在线Excel | 1 | False | — | — |
| 数据集 | 1 | False | — | — |
| 数据源 | 1 | False | — | — |
| 订阅管理 | 1 | True | False | 订阅计划、群组管理 |
| 订阅计划 | 2 | False | — | — |
| 群组管理 | 2 | False | — | — |
| 权限管理 | 1 | True | False | 用户授权、角色授权 |
| 用户授权 | 2 | False | — | — |
| 角色授权 | 2 | False | — | — |
| 归因配置 | 1 | False | — | — |

默认树中所有一级菜单初始均为收起。只有 `sidePath` 经过的祖先展开：页面位于任一二级菜单时只展开其一级父菜单；父菜单使用祖先激活样式，不出现绿色背景和指示条，但文字、图标和展开箭头均为主题色。

## 5. 默认侧栏图标映射

图标使用奇富本地图标组件，显示尺寸为 16×16。默认预设优先使用下表节点 ID 或发布 Key，并回读真实 main component；表中保留的是当前已盘点的发布名称。组件库若按 `Icon/<system>/<purpose>` 改名，节点失效时必须重新精确发现并更新映射，不凭语义猜测新名称。

| 一级菜单 | 图标组件 | 节点 ID | 发布 Key |
| --- | --- | --- | --- |
| 探索分析 | `Icon/dashboard` | `2312:176` | `cddd55e261b7284efe5494d80e3c2dbf09998bd5` |
| 智能分析 | `1.通用/Icon图标/QBI/智能问数`（组件卡片标签 `icon-icon_zhinengfenxi`） | `3721:11165` | `04c1d64632ac2521859af7ac7c7944e433e7c243` |
| 仪表板 | `Icon/yibiaoban1` | `2422:108` | `6a427095b3dceb7ec1bc607d8fd8a48f05113049` |
| 图表管理 | `Icon/table` | `2312:226` | `a1fd6e8cf04cc27cd41ba569c2dc5c6179f89e09` |
| 在线Excel | `Icon/xianshangexcel` | `2422:102` | `ab07f8c04fc81477141d1ad1a9abf3a70710fdb5` |
| 数据集 | `Icon/flow-manage` | `2423:444` | `b7831e070308984a7cff8e645596c627969e9973` |
| 数据源 | `Icon/shuju` | `2312:130` | `7694e996fbaa935b8cf853cea903ae1d560134bd` |
| 订阅管理 | `Icon/manage` | `2312:248` | `5099bcf783cfb7d636ee2d8bbfa721cdae565820` |
| 权限管理 | `Icon/quanxianguanli` | `2422:111` | `48a797b2fddf5e3636d610221a02772dd2584868` |
| 归因配置 | `Icon/gongdanliucheng` | `2423:82` | `8fa63bc0c95f2d7f21479b6377eaa7d578405634` |

二级和三级菜单不显示业务图标，只保留文本、层级缩进和必要的展开箭头。

## 6. 组装规则

使用真实 `Navigation / SideMenu / SideMenuItem-V2` 实例逐项组装，不创建固定业务大组件：

1. 宽度固定为 200px；一级菜单高 44px，二、三级菜单高 40px。
2. 每个实例按 `component-invocation-contract.md` 动态解析 `Label`、`Level`、`Has Submenu`、`State` 的真实 Key，写入后立即回读；不得假设展示名称就是完整可写 Key。
3. 一级菜单将 `showIcon 显示图标` 设为 `true`。默认模式通过本文件映射的节点 ID / 发布 Key 解析图标；自定义模式通过 `iconComponentName` 的完整唯一名称解析图标；两者都必须通过 `icon 图标` INSTANCE_SWAP 写入并回读，不得覆盖嵌套节点或绘制替代图标。
4. 二、三级菜单保持纯文本层级，不显示业务图标；`Has Submenu=True` 时仅保留组件自带的展开箭头。
5. `sideActive` 是唯一的当前页菜单并使用 `State=Selected`；如果它是无子菜单叶子，则显示绿色选中背景与右侧指示条。
6. `sideExpanded` 中的路径祖先设置 `expanded 展开=True` 并插入其已确认或已配置子项；所有不在当前路径的一级、二级父项设置为 `False`。不能为了展示更多菜单而额外展开。
7. 页面落在二级或三级菜单时，从 `sidePath` 排除 `sideActive` 得到 `sideAncestorsActive`。所有祖先都使用 `State=Selected` 且保持 `expanded 展开=True`，呈现白底、文字/一级图标/展开箭头主题绿；这表示祖先路径高亮，不表示父菜单是当前页。
8. 不在 `sideAncestorsActive` 中的菜单必须保持 `State=Default` 和收起；不能为了改变箭头方向、展示子集或沿用母版默认状态而设为绿色或展开。
9. 菜单区域使用垂直 Auto Layout。侧栏整体填满 Header 以下高度；菜单滚动区 `layoutGrow=1`、裁切内容并允许纵向滚动。
10. 底部固定保留 `collapse-button`：使用 200×40px 横向 Auto Layout 容器，顶部 1px 分割线，左内边距 20px；内部 `Icon/shouqi` 使用组件节点 `2423:450`，固定为 16×16px、垂直居中且 `layoutSizingHorizontal=FIXED`。只有底部容器横向填充侧栏，图标实例不得设为 `FILL` 或直接 resize 到侧栏宽度；其中心线应与上方一级菜单图标一致。滚动只作用于菜单区域，不让收起按钮随菜单滚走。
11. 静态画板需要展示完整菜单时允许增加画板高度；不得压缩菜单项高度，也不得让菜单覆盖底部收起按钮。
12. Label、图标或状态写入失败时停止，不创建 `Navigation Text Overlay`、裸文字或替代图标。所有一级菜单图标不得保持同一个默认 INSTANCE_SWAP。

### 6.1 各级菜单状态视觉矩阵（P0）

每个可见 SideMenuItem 都必须同时核对结构状态和最终可见样式，不能只看 `State`、`expanded` 或 INSTANCE_SWAP 回读：

| 菜单角色 | `State` / `expanded` | 背景与指示 | 文字 | 一级图标 | 展开箭头 |
| --- | --- | --- | --- | --- | --- |
| 当前页叶子（一级、二级或三级） | `Selected`；无子菜单 | 绿色选中背景与右侧指示条 | 主题绿 | 一级叶子有图标时为主题绿；二、三级不显示业务图标 | 不显示 |
| 当前路径一级祖先 | `Selected` / `True` | 白底，无当前页右侧指示条 | 主题绿 | 主题绿 | 主题绿，并呈展开方向 |
| 当前路径二级祖先 | `Selected` / `True` | 白底，无当前页右侧指示条 | 主题绿 | 不显示业务图标 | 主题绿，并呈展开方向 |
| 非当前路径一级、二级、三级菜单 | `Default`；有子菜单时 `False` | 白底，无选中背景和右侧指示条 | 中性色 | 一级为中性色；二、三级不显示业务图标 | 有子菜单时为中性色，并呈收起方向 |

一级图标完成 INSTANCE_SWAP 后，必须继续读取并检查实例内最终可见的图标 paint 或绑定语义变量。父项 `State=Selected`、文字和箭头变绿，不代表 swap 后图标已经继承主题色；图标仍为黑色或其他中性色时本项判 `FAIL`。若现有图标母版不能通过合法组件能力呈现选中主题色，按组件能力缺口或执行失败报告，不以页面级固定色覆盖、遮罩或替代图标修正。

## 7. 输入解析示例

输入：

```text
在毓数平台的权限管理 > 用户授权下新增用户授权列表页，顶部位于 QBI。
```

解析：

```text
platform=yushu
headerActive=QBI
sidePath=[权限管理, 用户授权]
sideActive=用户授权
sideExpanded=[权限管理]
sideAncestorsActive=[权限管理]
```

输入：

```text
在订阅管理 > 群组管理新增群组管理列表页。
```

解析：

```text
platform=yushu
headerActive=QBI（未提供且无可靠业务映射时的默认值）
sidePath=[订阅管理, 群组管理]
sideActive=群组管理
sideExpanded=[订阅管理]
sideAncestorsActive=[订阅管理]
```

输入：

```text
在智能分析 > 智能报表增加报表任务列表。
```

解析：

```text
platform=yushu
headerActive=QBI（未提供且无可靠业务映射时的默认值）
sidePath=[智能分析, 智能报表]
sideActive=智能报表
sideExpanded=[智能分析]
sideAncestorsActive=[智能分析]
```

自定义输入：

```text
导航模式：自定义菜单
当前菜单路径：资源管理 > 角色管理 > 数据权限
一级菜单：
- 资源管理，图标 Icon/yushu/ziyuanguanli，有子菜单
当前一级菜单的二级菜单：
- 用户管理，有子菜单
- 角色管理，有子菜单
- 组织管理，无子菜单
当前二级菜单的三级菜单：功能权限、数据权限、菜单权限
```

解析：

```text
navigationMode=custom
sidePath=[资源管理, 角色管理, 数据权限]
sideActive=数据权限
sideActiveLevel=3
sideExpanded=[资源管理, 角色管理]
sideAncestorsActive=[资源管理, 角色管理]
visibleLevel2=[用户管理, 角色管理, 组织管理]
visibleLevel3=[功能权限, 数据权限, 菜单权限]
```
