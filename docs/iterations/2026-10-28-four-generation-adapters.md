# 四项生成适配迭代时间线

开始：2026-10-28T23:33:28+08:00；执行跨午夜，后续实际提交时间按Git记录。

两个仓库工作分支：codex/five-platform-adapters-20261028；备份：backup/before-five-platform-adapters-20261028-233328。基线：qifu-skills 386ce28bfc3e5ad4a22c5847752aa5be22b80e2b；qfin-list-page 1e3c4b185328e97ec3a724415e540ef5249c62f2。原main、基础迭代和两组旧备份保留。

## 阶段01：新增两列表

- 列表插件0.2.0、router0.2.0，新增智能运营/智客星两个独立子Skill0.1.0，状态preflight-required。动态PageSpec与只读计划器拒绝旧来源、外平台菜单/Mode、重复字段和缺失目标，不把批量按钮当选择列。
- 当前六组件版本管理可读；旧四组件发布tag仍可安装恢复。扩展release/rollback别名，保持原三子Skill内容不变。
- shared1.4.0，旧列表入口1.4.1，detail及插件1.5.2；修正旧4892与固定4+1/SLOT禁写冲突。详情未新增平台能力。
- Figma已保留四个源画板可编辑备份：Page6183:2，副本6183:3、6183:50、6183:310、6183:750。针对实际使用的12个组件变体另留备份后补文字样式绑定；保持原字体/字重/字号/行高，新增8个复用Text Style。智能运营Header三个页级文字只在输出副本补绑定，原Frame仍保留页级缺口。
- 真实列表样本：智能运营6185:7863、智客星6189:8141。两者均1366×768，3个Header Cell、3行、9个Content Cell、无选择列；菜单真实owner和唯一选中叶子、智客星Header Items=0、源/副本resolved品牌值一致均回读PASS。最终提交后截图分别确认文案、页签、表格、分页无裁切，视觉PASS。它们不是空态/多选/所有控件的验收。
- 8个新增智能运营计划测试、8个智客星测试、7个版本兼容测试均先RED后GREEN；router旧测试按五平台目标更新并先RED后GREEN。消费场景复核确认两子Skill规则和CLI可执行；试稿夹具只证明固定回归请求，不能替代每次真实页面验收。
- 本阶段完整复跑：列表174项、qifu53项单元测试通过。历史asset snapshot记录原审计观察与当时三路由，不追溯改写；当前五路由以router为准。

## 阶段02：两平台普通抽屉

- drawer 1.7.0、shared 1.4.1、detail及自包含插件1.5.3；detail仅同步shared载荷，未新增详情平台。
- 金毓盟和电销已开放限定Create/Edit为preflight-required：1366×768、640宽、Input/Select/DateRange/Textarea；Simple Create单区≤6字段、Sectioned Create为2–3区≤15字段，Edit保留初值。金毓盟top标签/56 Header/208侧栏/64 Footer；电销left标签/56 Header/200侧栏/52 Footer，无actionSlot。
- 只读计划器消费注册表的readiness、操作、控件、宽度、标签及viewport。AUTO背景归一化为本平台真实背景，EXISTING_LIST_PAGE必须给验证来源；TEMPLATE、STRUCTURE_PREVIEW与未支持组合明确阻塞。25项CLI测试先RED后GREEN；独立审查发现的两项P2已修复并复核关闭。
- Figma四个真实样本：金毓盟Create6197:8368、Edit6204:10171；电销Create6205:11709、Edit6205:14118。全部背景/菜单真实owner、主题、滚动Body、固定Footer、零缺失Text Style及最终截图PASS。样本均为四字段的分组表单，其他合法字段请求仍须按实际规则组装并逐次验收，不把固定回归夹具当通用生成器。
- 针对原资产文字样式缺口，先保存组件可编辑副本再修复，原before、变量绑定、源/副本ID完整记录于Figma JSON。缺失的PingFang SC Semibold在4968:8898维护为实际实例已解析的同族Bold，保留600字重变量；原始可编辑副本6202:10164位于测试Page3497:651的(34332,1800)。这项字体维护不是生成时自动替换字体许可。
- 电销背景新增两个独立12px筛选组件6214:14907/6214:14913，仅Default Placeholder，公开value文本；共享14px表单母版保留。恢复138处历史实例对批准Text Style的关联，先确认字体、字号、行高相同，不改字体字段。电销菜单仅进行自身样式维护，有独立备份，始终未拿来适配智能运营菜单6158:1989。

## 阶段03：回归与复核

qifu最终78项单元测试通过（root3、旧列表20、抽屉46、详情9）；qfin阶段01完整174项通过，此后运行代码未变化，最终新子Skill契约和独立复核通过。合计252项。repo、Portable、多平台契约、detail载荷、同步dry-run/临时目录实装/符号链接安全、抽屉独立发布构建全部通过。detail载荷检查首次遇到本次unittest生成的__pycache__，清理生成缓存后复查PASS，未把缓存打包。

四项Skill消费场景全部GREEN；抽屉最终独立消费运行18次CLI（4正例、14反例）。全分支审查通过，两项真实P2经测试修复关闭。仍未开放缺失详情平台，也未宣称15种平台×页面组合全部完成。列表的空态/多选和抽屉复杂控件、其他宽度/标签布局需后续独立迭代。

## 配对提交

| 阶段 | qifu-skills | qfin-list-page |
| --- | --- | --- |
| 本轮基线 | 386ce28bfc3e5ad4a22c5847752aa5be22b80e2b | 1e3c4b185328e97ec3a724415e540ef5249c62f2 |
| 01 两列表 | 71b07c1276b5f163c76c164c9080d247c258fa60 | b44877a6b056cf220f4fb0a3e5655a6c542c2257 |

阶段01时间：2026-10-29T00:24:29+08:00（qifu）；另一仓库以Git提交时间为准。阶段02和最终记录的配对SHA在后续记录提交补入，本文件所在提交是当前记录检查点，不填写自身SHA。

## 按时间恢复与Figma回退

在对应仓库运行 `python3 scripts/iteration_timeline.py --repo . --before '<带时区的ISO时间>'`，核对selected.sha和restoreCommand；命令在新目录/新codex恢复分支打开旧代码，不覆盖当前工作。正式撤销用审核后的git revert生成新的回退提交，按依赖由新到旧处理，不强推main、不移动备份。

Figma回退独立于Git：详见同目录 `2026-10-28-four-adapters-figma.json` 的sourceId/backupId、mutatedNodeIds与restoreTypography。先保留当前Figma状态；恢复组件文字的原textStyleId及字体/字号/行高/字距等字段，或从对应可编辑组件副本恢复；新增回归画板可单独移除。新增样式只在确认无其他引用后删除。不能仅回滚Git就声称Figma已恢复。阶段01时电销菜单尚未维护；阶段02仅对电销自身菜单/文字样式维护并保留备份。智能运营独立菜单6158:1989未用电销菜单替代。3650:998为智客星明确复用的共享菜单，按JSON记录回退文字样式。缺失旧字体的原始可编辑副本独立保留，不能承诺当前字体环境可加载该字体。

本仓库来源于列表插件；详细Figma变更与可编辑副本JSON在配对qifu-skills同名分支的docs/iterations中维护。
