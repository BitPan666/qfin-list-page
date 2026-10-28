# 五个平台页面 Skill 交接入口

当前配对分支：`codex/five-platform-adapters-20261028`（两个仓库同名）。先读[本轮时间线](../iterations/2026-10-28-four-generation-adapters.md)，再核对远端增量与本地未提交文件。

本仓库列表插件0.2.0、router0.2.0，含五个平台独立子Skill。智能运营/智客星新子Skill0.1.0为preflight-required；原三子Skill保留。旧四组件tag安装/回退兼容，当前六组件版本状态已验证。

另一个仓库qifu-skills的同名分支提供drawer1.7.0、shared1.4.1、detail1.5.3及Figma源/副本完整回退JSON；金毓盟和电销限定普通Create/Edit已验收，缺失详情平台仍unsupported。六个Figma样例和252项测试结果见时间线。

所有修改继续使用独立codex迭代分支，修改前留时间戳备份；先保留Figma可编辑副本再改原资产。按时间恢复使用`python3 scripts/iteration_timeline.py --repo . --before '<含时区时间>'`，在新目录恢复，不覆盖当前内容。Git回退不等于Figma已恢复。

智能运营外壳6155:1851、独立菜单6158:1989继续保留，不用电销菜单适配。不要把候选、只读计划通过或固定回归样本视为所有业务页已验收。换电脑还需检查连接/运行环境，本机缓存、未推送文件和聊天不会自动同步。
