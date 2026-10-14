# qfin-list-page

一个用于 QFIN 标准桌面端数据列表页的 Codex Plugin。用户只安装一次，即可同时获得统一入口和三个平台的独立生成能力。

## 包含的 Skill

Plugin 内含四个彼此独立的 Skill：

- `qfin-list-page`：统一路由入口，只判断目标平台并选择一个子 Skill；
- `qifu-yushu-list-page`：毓数平台列表页能力；
- `qifu-jinyumeng-list-page`：金毓盟平台列表页能力；
- `qifu-dianxiao-list-page`：电销平台列表页能力。

日常使用时只调用 `$qfin-list-page`，不直接调用三个子 Skill 名称。路由层不会合并或改写平台规则，平台确认后只加载一个对应的子 Skill。

## 从 GitHub 安装

将下面的 `owner/qfin-list-page` 替换为实际 GitHub 仓库地址：

```bash
codex plugin marketplace add owner/qfin-list-page --ref main
codex plugin add qfin-list-page@qfin-list-page
```

完成安装后，请新建一个 Codex 新任务再使用，让新的 Plugin 与 Skill 发现结果完整生效。

开发者也可以从本地仓库安装：

```bash
codex plugin marketplace add /absolute/path/to/qfin-list-page
codex plugin add qfin-list-page@qfin-list-page
```

## 使用方式

推荐从 [`prompt-template.md`](plugins/qfin-list-page/skills/qfin-list-page/references/prompt-template.md) 复制完整提示词。目标平台是必填项；如果平台缺失、冲突或不支持，路由会停止并要求确认，不会默认选择毓数。

三个最小示例：

```text
@figma
使用 $qfin-list-page 为毓数平台生成客户管理列表页，筛选项、表格列和操作要求如下：……
```

```text
@figma
使用 $qfin-list-page 为金毓盟平台生成渠道订单列表页，目标文件与 Page 如下：……
```

```text
@figma
使用 $qfin-list-page 为电销平台更新线索分配列表页，保留现有导航并按以下字段调整：……
```

## 维护原则

本仓库是四个 Skill 的唯一可编辑源。本地已安装目录和 Codex 缓存只是生成物，不在其中直接修改文件。

修改单个平台 Skill 时：

1. 只编辑本仓库内对应的子 Skill，不同步手改其他子 Skill，也不需要修改 Plugin 外壳；
2. 运行该子 Skill 的测试和契约校验；
3. 运行统一路由测试、路由校验和 Plugin 校验，确认改动没有破坏路由与打包边界；
4. 发布时更新受影响 Skill 的 `VERSION`，并按语义化版本更新 `plugins/qfin-list-page/.codex-plugin/plugin.json` 中的 `version`；
5. 推送 GitHub 后，让使用方刷新 marketplace、重装 Plugin，并开启新任务。

GitHub 发布后的更新命令：

```bash
codex plugin marketplace upgrade qfin-list-page
codex plugin remove qfin-list-page@qfin-list-page
codex plugin add qfin-list-page@qfin-list-page
```

本地开发如果需要强制绕过旧缓存，请使用一个新的 patch `version` 作为 `cachebuster`，再执行 remove/add。不要在既有本地 Plugin 更新循环中手工修改 marketplace JSON；该文件也是仓库受控配置。

## 准备新版本

`release.py` 只接受已声明且实际发生修改的组件。所有公开命令默认是 dry-run；只有显式加上 `--apply` 才会写入版本文件。

先预览版本变化、Changelog 和校验命令：

```bash
python3 scripts/release.py \
  --component yushu \
  --bump patch \
  --note "统一筛选区规则"
```

确认预览无误后再写入发布元数据并执行校验：

```bash
python3 scripts/release.py \
  --component yushu \
  --bump patch \
  --note "统一筛选区规则" \
  --apply
```

脚本不会自动提交、打标签或推送。校验通过后需要人工检查差异，然后手工执行：

```bash
git add <reviewed-files>
git commit -m "release: qfin-list-page v0.1.1"
git tag -a v0.1.1 -m "qfin-list-page plugin v0.1.1"
```

是否推送提交与标签始终由维护者手工决定。

## 只恢复一个 Skill

已发布的单个 Skill 出现问题时，先从一个正式 Git 标签预览将要恢复的行为：

```bash
python3 scripts/rollback_skill.py --skill yushu --to v0.1.0
```

确认文件增删、内容和权限位差异后再执行：

```bash
python3 scripts/rollback_skill.py --skill yushu --to v0.1.0 --apply
```

apply 会先备份到 `.qfin-backups/<timestamp>/`，只恢复目标 Skill 的行为文件，并保留当前 `VERSION`。完成后必须按脚本输出的 `release.py --component <alias> --bump patch` 命令发布一个更高的新版本，不能复用历史版本号。

## 临时安装整个 Plugin 的历史版本

整个 Plugin 需要临时止损时，先预览指定正式标签的四个组件版本、安装命令和自动恢复方案：

```bash
python3 scripts/install_version.py --tag v0.1.0
```

确认后才执行历史安装：

```bash
python3 scripts/install_version.py --tag v0.1.0 --apply
```

脚本会在 `.release-worktrees/<tag>` 建立 detached worktree，校验完整历史快照后才切换 marketplace 和 Plugin。任一 Codex 命令失败时会自动恢复原仓库安装。安装成功后必须新建 Codex 任务验证。

恢复当前 `main` 仓库版本：

```bash
python3 scripts/install_version.py --restore-current
python3 scripts/install_version.py --restore-current --apply
```

历史 worktree 不会被脚本自动删除，也不会影响其他 worktree。恢复当前版本并人工确认后，可按脚本输出的精确 `git worktree remove .release-worktrees/<tag>` 命令清理指定目录。

## 完整验证

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s plugins/qfin-list-page/skills/qfin-list-page/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 \
  plugins/qfin-list-page/skills/qfin-list-page/scripts/validate_router.py

UV_CACHE_DIR=/private/tmp/qfin-uv-cache PYTHONDONTWRITEBYTECODE=1 \
  uv run --with pyyaml python \
  /Users/panyue/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/qfin-list-page/skills/qfin-list-page

UV_CACHE_DIR=/private/tmp/qfin-uv-cache PYTHONDONTWRITEBYTECODE=1 \
  uv run --with pyyaml python \
  /Users/panyue/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/qfin-list-page
```

三个平台子 Skill 的测试、契约版本和原样导入结果见 [`docs/import-integrity-2026-10-13.md`](docs/import-integrity-2026-10-13.md)。
