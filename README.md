# qfin-list-page

一个用于 QFIN 标准桌面端数据列表页的 Codex Plugin。用户只安装一次，即可同时获得统一入口和三个平台的独立生成能力。

## 包含的 Skill

Plugin 内含四个彼此独立的 Skill：

- `qfin-list-page`：统一路由入口，只判断目标平台并选择一个子 Skill；
- `qifu-yushu-list-page`：毓数平台列表页能力；
- `qifu-jinyumeng-list-page`：金毓盟平台列表页能力；
- `qifu-dianxiao-list-page`：电销平台列表页能力。

日常使用时只调用 `$qfin-list-page`，不直接调用三个子 Skill 名称。路由层不会合并或改写平台规则，平台确认后只加载一个对应的子 Skill。

## 新电脑安装：从 GitHub 获取

适用于首次安装的电脑。QFIN List Page 提供生成规范；实际读写 Figma 需要另行安装并授权 Figma 插件。当前源码版本为 **0.1.2**，包含毓数 1.3.3、金毓盟 1.0.0、电销 1.0.0。

### 方式一：让 Codex 协助安装

安装并登录 Codex 后，新建对话，粘贴：

```text
请从 https://github.com/BitPan666/qfin-list-page 添加插件市场，
安装 QFIN List Page，并核对安装版本。
请区分“添加插件源”和“完成插件安装”；如果需要界面操作，请告诉我具体步骤。
```

安装完成后，在插件目录安装并连接 Figma，使用有目标设计文件编辑权限的账号授权。然后新建一个 Codex 新任务，在输入框通过 @ 选择 Figma 和 QFIN List Page。

### 方式二：终端安装

需要电脑上已有可用的 Codex CLI；先运行 `codex --version`。若提示找不到命令，先按 [Codex CLI 官方安装说明](https://developers.openai.com/codex/cli) 安装 CLI，或使用上面的对话方式。

```bash
codex plugin marketplace add https://github.com/BitPan666/qfin-list-page.git --ref main
codex plugin add qfin-list-page@qfin-list-page
```

第一条只添加插件源，第二条才安装插件。也可在添加源后，到 Codex 插件目录选择 QFIN List Page 点击安装。安装后新建任务；若插件列表未刷新，重启 Codex。

本仓库公开，拉取插件无需取得私有仓库权限；Figma 文件的访问和编辑权限仍独立控制。不要复制其他电脑的账号凭据或授权文件。

### 确认安装成功

- `codex plugin list` 能找到 QFIN List Page，确认其已安装/启用。
- 新对话的 @ 菜单可以选到 QFIN List Page 和 Figma。
- 请求生成时明确平台、目标 Figma 文件、目标 Page 和业务需求。
- 目标 Page 不限定测试 Page；创建与更新以用户指定目标为准。

开发者也可以从本地仓库安装：

```bash
codex plugin marketplace add /absolute/path/to/qfin-list-page
codex plugin add qfin-list-page@qfin-list-page
```

如果此前配置了同名本地源，先用 `codex plugin marketplace list` 核对来源；确认需要切换后移除该源，再添加上述 GitHub 地址，避免刷新到旧的本地目录。

安装机制参考 [OpenAI 插件文档](https://developers.openai.com/plugins/build/plugins)。

## 使用方式

业务提示词只需提供平台、目标文件、Page、导航、筛选、列、操作和数据要求。布局、间距、尺寸、组件及验收遵循平台 Skill；有特殊需求再显式覆盖。

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

## 五平台资产基础登记（0.1.2）

[资产注册表](plugins/qfin-list-page/skills/qfin-list-page/references/platform-assets.json) 记录 2026-10-28 已核查的节点、内容装配边界与平台 Mode；[资产说明](plugins/qfin-list-page/skills/qfin-list-page/references/platform-assets.md) 解释字段和限制。当前生成入口仍为上述三个平台。智客星、智能运营均登记为 `pending-adapter`，不能通过注册表启用路由或替代为其他平台。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  plugins/qfin-list-page/skills/qfin-list-page/scripts/validate_platform_assets.py
# 也可使用 --registry /absolute/path/to/platform-assets.json 校验候选副本
```

该命令只做离线资产事实校验。新增页面尚未生成或验收；旧智客星模板不能作为已验证默认值，智能运营应保留 Frame 外壳并在副本中创建内容容器。通过 `python3 scripts/iteration_timeline.py --repo . --before '2026-10-28T22:49:16+08:00'` 查询带时区时间点的源码检查点与新恢复分支建议；查询不会修改工作区。版本分支、测试记录和按时间恢复方式见[本轮迭代记录](docs/iterations/2026-10-28-five-platform-foundation.md)。

## 维护原则

本仓库是四个 Skill 的唯一可编辑源。本地已安装目录和 Codex 缓存只是生成物，不在其中直接修改文件。

修改单个平台 Skill 时：

1. 只编辑本仓库内对应的子 Skill，不同步手改其他子 Skill，也不需要修改 Plugin 外壳；
2. 运行该子 Skill 的测试和契约校验；
3. 运行统一路由测试、路由校验和 Plugin 校验，确认改动没有破坏路由与打包边界；
4. 发布时更新受影响 Skill 的 `VERSION`，并按语义化版本更新 `plugins/qfin-list-page/.codex-plugin/plugin.json` 中的 `version`；
5. 推送 GitHub 后，让使用方刷新 marketplace、重装 Plugin，并开启新任务。

GitHub 发布后，在需要更新的电脑执行以下命令。刷新 marketplace 仅更新源快照，随后重新安装 Plugin 才会使用新版本：

```bash
codex plugin marketplace upgrade qfin-list-page
codex plugin remove qfin-list-page@qfin-list-page
codex plugin add qfin-list-page@qfin-list-page
```

本地开发如果需要强制绕过旧缓存，请使用一个新的 patch `version` 作为 `cachebuster`，再执行 remove/add。不要在既有本地 Plugin 更新循环中手工修改 marketplace JSON；该文件也是仓库受控配置。

## 版本管理流程总览

`release.py`、`rollback_skill.py` 和 `install_version.py` 默认都是 dry-run，只有显式使用 `--apply` 才会修改仓库文件或本地 Plugin 安装状态。Git 标签是唯一正式历史来源；不要直接编辑 Plugin 缓存，也不从缓存反向覆盖仓库。

### 正常发布流程

1. 只修改目标 Skill，并运行它的测试与契约校验。
2. 先运行 `python3 scripts/release.py ...` dry-run，核对组件、版本、Changelog 和校验命令。
3. 确认后加 `--apply`，检查实际差异并完成全量验证。
4. 人工提交代码，再人工创建 Git 标签；脚本不自动推送 GitHub。
5. 使用方重新安装后，新建 Codex 任务让新 Plugin 与 Skill 被完整加载。

### 单 Skill 恢复流程

1. 用 `python3 scripts/rollback_skill.py --skill <alias> --to <tag>` 预览目标 Skill 的历史差异。
2. 加 `--apply` 后只恢复目标行为，保留当前 `VERSION`，并用备份和非目标哈希防止跨 Skill 污染。
3. 再用 `release.py --component <alias> --bump patch` 发布更高的新版本，不复用旧版本号。

### 整个 Plugin 临时降级流程

1. 用 `python3 scripts/install_version.py --tag <tag>` 预览历史版本和恢复方案。
2. 加 `--apply` 后从 detached worktree 安装完整历史 Plugin，然后新建 Codex 任务验证。
3. 止损结束后运行 `python3 scripts/install_version.py --restore-current --apply`，恢复当前仓库版本，再新建 Codex 任务。
4. 长期修复仍需在 `main` 上产生一个新的补丁版本，不移动也不覆盖旧标签。

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
