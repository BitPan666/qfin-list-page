# 电销平台基线

## 身份与来源

- 固定身份：`platform=dianxiao`。
- 组件库文件：`奇富科技中后台组件库-新`，file key `gTV3VdC6a5e9vpkRHIZSXA`。
- 规则来源：用户确认的 Frame 2、正式电销菜单母版及同文件真实组件。
- 主题色：`#009E73`；默认导航文字和图标：`#262626`；顶层分类分割线：`#EBEBEB`。

## 顶部 Header

Header 固定使用 `Navigation / HeaderMenu / Dianxiao Header`（节点 `5824:4491`），包含 CiFU 品牌、`客户销售平台 - 借条`、已签到状态、小蜜开关、空闲状态、外呼设置、企微、消息和用户头像。组件尺寸 `1366 × 56px`、左右内边距 `20px`、背景透明并承接页面底层背景。业务提示词不得改写或拆散这组固定内容，除非用户明确提出平台级变更。

## 顶层分类

- 顶层固定为 `全部菜单` 和 `收藏菜单`。
- 两组之间用 `#EBEBEB` 分割线分隔。
- `全部菜单` 展示平台一级菜单树；`收藏菜单` 只展示用户提示词明确提供的收藏项。

## 一级菜单预设

顺序固定，不得增删或重排：

1. 主面板
2. 工作管理
3. 项目管理
4. 名单管理
5. 策略管理
6. 录音解读
7. 监控管理
8. 机器人管理
9. 营销管理
10. 品质管理
11. 查询管理
12. 触达管理
13. 系统管理
14. 异常管理
15. 新人成长
16. 个人信息
17. 消息中心

已确认的一级图标组件：

| 菜单 | 图标组件 | 节点 |
| --- | --- | --- |
| 主面板 | `Icon/dianxiao/zhumianban` | `5756:11` |
| 工作管理 | `Icon/dianxiao/gongzuoguanli` | `5759:19212` |
| 项目管理 | `Icon/dianxiao/xiangmuguanli` | `5756:16` |
| 名单管理 | `Icon/dianxiao/mingdanguanli` | `5756:21` |
| 策略管理 | `Icon/dianxiao/celueguanli` | `5810:20` |
| 录音解读 | `Icon/dianxiao/luyinjiedu` | `5810:30` |
| 监控管理 | `Icon/dianxiao/jiankongguanli` | `5810:40` |
| 机器人管理 | `Icon/dianxiao/jiqirenguanli` | `5810:50` |
| 营销管理 | `Icon/dianxiao/yingxiaoguanli` | `5756:36` |
| 品质管理 | `Icon/dianxiao/pinzhiguanli` | `5756:46` |
| 查询管理 | `Icon/dianxiao/chaxunguanli` | `5756:51` |
| 触达管理 | `Icon/dianxiao/chudaguanli` | `5810:60` |
| 系统管理 | `Icon/dianxiao/xitongguanli` | `5756:61` |
| 异常管理 | `Icon/dianxiao/yichangguanli` | `5756:41` |
| 新人成长 | `Icon/dianxiao/xinrenchengzhang` | `5810:74` |
| 个人信息 | `Icon/dianxiao/gerenxinxi` | `5810:84` |
| 消息中心 | `Icon/dianxiao/xiaoxizhongxin` | `5749:18758` |

以上两个图标已从正式菜单实例反向回读确认：图标母组件画板为 `24px × 24px`，作为 `SideMenuItem` 的 Instance swap 后固定显示为 `16px × 16px`。生成时只校验菜单实例中的最终尺寸，不修改图标母组件画板尺寸。

## 菜单尺寸与状态

- 菜单 Auto Layout 固定宽度 `200px`，菜单项高度 `40px`。
- 一级 Icon 固定 `16px × 16px`，距左侧 `20px`，与标题间距 `8px`。
- 默认一级标题与 Icon 均为 `#262626`。
- 任何选中且有 Icon 的菜单项，Icon 必须与选中文字一起解析为电销主题色；不得因 Instance swap 或旧实例 override 保留为默认深色。
- 有子集一级选中：标题、Icon 变为 `#009E73`，箭头由向下变为向上；不增加叶子选中白底。
- 无子集一级选中：使用 `188px × 40px` 白色背景，标题与 Icon 为主题色。
- 二级有子集：文字与一级标题左对齐；选中仅文字为 `#009E73` 且箭头向上。
- 二级无子集选中：白色背景、主题色文字、Medium 字重。
- 三级继承二级叶子规则，标题相对二级向右 `24px`。

实际生成时以最新 `Navigation / Dianxiao SideMenu / SideMenuItem` 母版视觉为最终事实源；本节用于验证母版是否仍符合用户确认规则。

## 层级组装

- 提示词使用 `一级菜单 > 二级菜单 > 三级菜单` 表达当前路径。
- 一级菜单固定；提示词决定当前一级下需展示的二级同级项，以及当前二级下需展示的三级同级项。
- 只展开当前路径祖先；当前叶子唯一选中。
- 系统内页签选中项必须与当前叶子菜单名称一致。
- `1366px × 768px` 等短视口中不得删减固定一级菜单；使用菜单滚动视口让当前选中项保持可见，`全部菜单` 与 `收藏菜单` 主分类保持固定。

## 平台隔离

允许复用共享基础组件及毓数已经验证的“动态组装方法”，禁止复用毓数或金毓盟的 Header、侧栏、平台 Shell、平台 Token 模式和固定菜单数据。
