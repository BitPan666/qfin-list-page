# 五平台列表资产基础迭代

记录时间：2026-10-28T22:56:10+08:00。仓库 `BitPan666/qfin-list-page`，工作分支 `codex/five-platform-foundation-20261028`。本轮基线 `df21008eb2a489d4b105992b21ddb7def8386d5c`；远端备份分支 `backup/before-five-platform-iteration-20261028-224916` 指向该基线。配对的 shared 迭代位于 `BitPan666/qifu-skills` 同名分支，基线 `cae1b393564ee40bd3e870607324e1442e0636f8`；两个仓库检查点分别提交、分别恢复。

## 本轮边界

新增载荷内 `references/platform-assets.json`、资产说明、离线验证器与 28 个变异测试。Plugin 0.1.1 → 0.1.2；router 载荷 0.1.0 → 0.1.1。毓数 1.3.3、金毓盟 1.0.0、电销 1.0.0 保持不变。router 的原 SKILL、提示模板、路由验证器和元数据均未改动；新增资产登记没有扩展原三平台路由。

智能运营为已核查 FRAME 外壳，使用独立菜单母组件集 `6158:1989`；空白内容 RECTANGLE 只允许后续在可编辑副本中创建容器，不能按原生 Slot 操作或重建外壳。智客星为 Candidate，保留 Header 实际 `Items=0`、50 个可见文本样式缺口、历史模板的毓数 Header 冲突。两者均为 `pending-adapter`。本轮没有生成新页面、修改 Figma、更新安装缓存，也不宣称五平台页面已通过验收。

## 源码检查点与验证

| 阶段 | 证据 |
| --- | --- |
| 迭代前 | 上述基线 SHA 与远端 backup 分支 |
| RED | 先运行新资产测试：28/28 因缺少验证器而失败；`list-assets-red.log` |
| GREEN | 新资产测试 28/28；`list-assets-green.log` |
| 完整回归 | root 41、router 37、毓数 20、金毓盟 44、电销 9，共 151；全部通过 |
| 契约 | router、三子 Skill、资产 CLI 校验全部通过；版本清单一致 |

本机本轮日志位于 `/private/tmp/five-platform-iteration-20261028/list-*.log`，不是持久发布附件。可从源码重跑下列命令；资产 CLI 接受 `--registry PATH`，不需要 Figma 或网络。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/qfin-list-page/skills/qfin-list-page/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 plugins/qfin-list-page/skills/qfin-list-page/scripts/validate_router.py
PYTHONDONTWRITEBYTECODE=1 python3 plugins/qfin-list-page/skills/qfin-list-page/scripts/validate_platform_assets.py
# 对 yushu / jinyumeng / dianxiao 各自执行：
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/qfin-list-page/skills/qifu-yushu-list-page/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 plugins/qfin-list-page/skills/qifu-yushu-list-page/scripts/validate_skill_contract.py plugins/qfin-list-page/skills/qifu-yushu-list-page
```

三个子 Skill 的完整 Git tree 与基线完全一致（含 VERSION）：

| 子 Skill | 基线 tree SHA | 文件数 |
| --- | --- | --- |
| 毓数 | `59efce8fe43faaf1d571cc14fa94621151f53c72` | 11 |
| 金毓盟 | `587bdbab45cbff4c4c4bd69147a1884aa0200657` | 14 |
| 电销 | `0412162890a8a321d10eb6f9ac4e983f5f80e8da` | 13 |

发布元数据按现有 `VERSION` / `versions.json` / `plugin.json` 一致性方案更新。既有 `release.py` 要求只存在目标组件改动，本轮跨组件文档与资产基础迭代不满足其输入边界，未绕过该保护或让脚本改写子 Skill。

## 按时间安全恢复

先用 `git log --date=iso-strict --format='%h %aI %s'` 选定已提交的检查点。正式撤销使用 `git revert`，保留迭代历史；将下面命令中的 `CHECKPOINT_SHA` 替换为核对过的本轮提交 SHA，并先提交或保存当前未提交工作：

```bash
git show --stat CHECKPOINT_SHA
git revert CHECKPOINT_SHA
```

仅需查看或继续迭代前版本时，在新目录创建恢复分支，不改动现有工作目录或远端分支：

```bash
git worktree add -b restore/list-before-20261028-224916 ../qfin-list-page-restore-20261028 df21008eb2a489d4b105992b21ddb7def8386d5c
```

共享时间线查询工具可选择当前分支祖先检查点并输出恢复建议：

```bash
python3 scripts/iteration_timeline.py --repo .
python3 scripts/iteration_timeline.py --repo . --before '2026-10-28T22:49:16+08:00'
```

默认输出当前分支时间线；`--before` 必须包含时区。JSON 包含检查点 SHA、提交时间、`dirtyWorktree` 与 `restoreCommand`；核对后自行执行该命令，它在新目录和新分支打开历史版本。查询工具只读，没有 `--apply` 或 `--json` 参数，不执行 reset、强推、覆盖目录或自动回退。本轮只运行查询，没有执行真实仓库返回的恢复命令。新增 3 个临时 Git 仓库测试覆盖时间筛选、无检查点、缺少时区及脏工作区保持不变；配合 root 测试共 41 项通过。跨仓库恢复应按相同阶段配对检查点，不复用另一个仓库的 SHA。

## 已推送的配对检查点

以下时间均为 Asia/Shanghai（UTC+08:00），SHA 已从 GitHub 回读，两个仓库各自的远端 tree 与本机生成的 tree 完全一致。

| 阶段 | qifu-skills | qfin-list-page |
| --- | --- | --- |
| 01 时间线工具 | `9379438b725f3f80f2e1cb9eb15520515247580f` · 2026-10-28T23:16:08+08:00 | `f8a4f745bf2d7b326d7c7999cabe37ecc880c288` · 2026-10-28T23:16:17+08:00 |
| 02 五平台基础配置 | `c345e20c34a44398f7543322595737ebadad90ce` · 2026-10-28T23:17:29+08:00 | `e3778311340888af0aaddcbdbd4e70d483cc505e` · 2026-10-28T23:17:40+08:00 |
| 03 核验记录 | 见本文件当前版本所属提交 | 见本文件当前版本所属提交 |

最终本地复跑：qifu-skills 53 项、qfin-list-page 151 项，共 204 项单元测试全部通过；另外资产、路由、Skill、主题、插件载荷和 release/sync 契约通过。独立复核提出的三项 P2 均修复并复核通过。GitHub Actions 查询未返回本分支运行记录，不能将本地通过称为远端 CI 通过。

阶段 03 仅更新交接/计划/验证记录，不修改运行时规则。若需恢复阶段 01，后续基础配置尚未存在；恢复阶段 02 包含完整本轮配置。按时间查询各自分支的实际提交时间，并以本表配对，避免两个提交间的秒差造成跨仓库版本错配。
