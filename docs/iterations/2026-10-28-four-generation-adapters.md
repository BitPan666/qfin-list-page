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

## 后续阶段

阶段02补金毓盟、电销普通Create/Edit抽屉，先明确56/208与56/200背景边界、默认标签排列及控件，再做真实样本验收。阶段03做完整回归、审查、交接与跨仓库提交配对。未完成项不标ready。

## 按时间恢复与Figma回退

在对应仓库运行 `python3 scripts/iteration_timeline.py --repo . --before '<带时区的ISO时间>'`，核对selected.sha和restoreCommand；命令在新目录/新codex恢复分支打开旧代码，不覆盖当前工作。正式撤销用审核后的git revert生成新的回退提交，按依赖由新到旧处理，不强推main、不移动备份。

Figma回退独立于Git：详见同目录 `2026-10-28-four-adapters-figma.json` 的sourceId/backupId、mutatedNodeIds与restoreTypography。先保留当前Figma状态；恢复组件文字的原textStyleId及字体/字号/行高/字距等字段，或从对应可编辑组件副本恢复；新增回归画板可单独移除。新增样式只在确认无其他引用后删除。不能仅回滚Git就声称Figma已恢复。原电销菜单5763:1753和智能运营菜单6158:1989未修改；3650:998为智客星已明确使用的共享菜单，只有记录中的文字样式绑定维护。

本仓库来源于列表插件；详细Figma变更与可编辑副本JSON在配对qifu-skills同名分支的docs/iterations中维护。
