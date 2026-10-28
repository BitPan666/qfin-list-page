# 五平台资产事实（2026-10-28）

`platform-assets.json` 是上一基础检查点的历史离线资产登记，包含当时的三平台路由事实；当前路由以父Skill的五平台表为准。资产快照不因新增Adapter被追溯改写。仅登记新增平台不会创建子 Skill、启用路由或证明生成通过。原三平台 Skill 的规则与版本保留；本轮没有修改 Figma。

| 平台 | 核查外壳 / 内容 | Header 来源 | 菜单母组件集 | 运行时 |
| --- | --- | --- | --- | --- |
| 毓数 | COMPONENT `3478:657`，1248×397，**仅列表内容** | COMPONENT_SET `3639:1529`，变体 1366×48 | `3650:998`，观测到 200×44、200×40 | 既有独立子 Skill |
| 金毓盟 | COMPONENT `5022:16`，1366×1024 | COMPONENT `4993:1440`，1366×56 | `4746:46261`，208×48，24 变体 | 既有独立子 Skill |
| 电销 | COMPONENT `5829:31`，1366×768 | COMPONENT `5824:4491`，1366×56 | `5763:1753`，200×40；MenuRoot `5762:1537` | 既有独立子 Skill |
| 智客星 | Candidate FRAME `5468:3233`；手工参考 `5408:13969`，均 1366×768 | COMPONENT_SET `5517:2109`，变体 1366×48 | 候选明确复用 `3650:998` | `pending-adapter` |
| 智能运营 | FRAME `6155:1851`，1366×768 | FRAME `6148:32454`，1366×48 | **独立** `6158:1989`，200×40，24 变体，Level 1/2，当前 17 实例 | `pending-adapter` |

Header 的 `width` / `height` 对 COMPONENT_SET 表示 Header 变体尺寸，不是组件集在画布上的排版边界。菜单 `ownerId` 表示真实母组件集，不从实例名、属性键后缀或视觉相似性推断归属。智能运营保留 `Label#5763:0` 等历史键，同时真实 owner 为 `6158:1989`；不能因此换成电销母版。

内容装配按平台登记：毓数组合平台导航与内容 Shell 的原生 Slot；金毓盟内容 `5022:2` 有 tabs/filter/action/table Slot，电销内容 `5829:15` 有 tabs/filter/table Slot。智能运营 `6148:34365` 是位于 `(216,102)`、尺寸 1134×633 的空白 **RECTANGLE**，不是 SLOT；后续应克隆可编辑 Frame 副本，在副本中创建内容容器，保留外壳及 Tabs FRAME `6156:1989`。空白内容不构成重建外壳的理由。

智客星候选仍有 50 个可见文本样式缺口；Header 实际属性是 `Items=0`，实例名的 `Items=5` 不能覆盖回读值。历史 `4892:34812` 名称写 1440，实际为 1366×768，且 Header 仍引用毓数 `3639:1529`，因此 `eligibleDefault=false`。候选与手工参考均不能在本轮升级为 `validated-template`。

基础集合 `VariableCollectionId:9:8` 中核查到毓数 `9:6`、金毓盟 `4717:0`、电销 `5722:0`、智能运营 `2158:0`。智客星没有专属 Mode；登记 `modeId=null` 与 `inherit-verified-template-bindings`，另记候选观测继承值 `9:6`，这不授权为其设置毓数显式 Mode，也不构成跨平台兜底。现有历史 Token 全量快照未被本登记覆盖。

运行 `python3 scripts/validate_platform_assets.py`（相对本 Skill 目录），或加 `--registry PATH` 检查副本。验证器固定本次核查的来源、类型、尺寸、状态和内容策略，拒绝跨平台替换和候选误升级；不连 Figma，不验证未来页面。`audit.evidenceSha256` 关联原只读证据文件，属于溯源元数据，不是运行时联网校验。将来修改固定事实需要新的核查和版本迭代。

当前新增两子Skill为preflight-required，均已建立独立生成规则与计划器；逐次结果仍须结构和截图验收。历史表中的pending-adapter描述仅对应基础迭代当时状态。
