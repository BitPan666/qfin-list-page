# qfin-list-page 版本管理与回退机制设计

日期：2026-10-14  
状态：已由用户确认

## 1. 背景

`qfin-list-page` 以一个 Codex Plugin 分发四个相互独立的 Skill：

- `qfin-list-page`：统一路由；
- `qifu-yushu-list-page`：毓数平台；
- `qifu-jinyumeng-list-page`：金毓盟平台；
- `qifu-dianxiao-list-page`：电销平台。

Plugin 是用户安装和更新的交付单位，Skill 是仓库内独立演进的能力单位。因此版本管理必须同时支持两类不同操作：

1. 只恢复一个 Skill，其他 Skill 保持不变；
2. 临时或永久恢复整个 Plugin 版本。

## 2. 目标

- 每个已发布 Plugin 版本都能还原其包含的四个 Skill 版本。
- 可以只恢复指定 Skill，且通过哈希证明未修改其他 Skill。
- 可以安装任意已有的 Plugin Git 标签，而不切换或破坏 `main` 工作区。
- 所有修改命令默认只预览，只有显式传入 `--apply` 才写入文件或安装状态。
- 发布、恢复和安装均执行相应测试与校验。
- 已发布版本号和 Git 标签不可复用、覆盖或重写。
- Plugin 仓库仍是唯一可编辑源；安装缓存和历史安装目录不可作为恢复源。

## 3. 非目标

- 不拆分成四个 Git 仓库。
- 不使用 Git submodule 或运行时远程依赖。
- 不在此次工作中修改三个平台 Skill 的业务内容。
- 不实现自动推送 GitHub、自动创建 Release 或无人值守发布。
- 不自动生成或修改 Figma 页面。

## 4. 总体模型

### 4.1 开发层：Skill 版本

每个 Skill 继续使用自身目录中的 `VERSION`：

| 组件 | 当前版本 |
| --- | --- |
| `qfin-list-page` | `0.1.0` |
| `qifu-yushu-list-page` | `1.3.2` |
| `qifu-jinyumeng-list-page` | `0.7.2` |
| `qifu-dianxiao-list-page` | `0.1.0` |

Skill 版本用于表达该组件自身的行为变化。修改哪个 Skill，只升级哪个 Skill。

### 4.2 交付层：Plugin 版本

`plugins/qfin-list-page/.codex-plugin/plugin.json` 中的 `version` 是用户安装的整体版本。任何需要分发给用户的 Skill 内容变化，都必须产生新的 Plugin 版本。

### 4.3 历史快照：Git 标签

每个正式 Plugin 版本对应一个不可变 Git 标签：

```text
v0.1.0
v0.1.1
v0.1.2
```

标签是完整 Plugin 回退和单 Skill 内容恢复的唯一正式历史来源。不得移动、覆盖或重新创建已发布标签。

## 5. 版本规则

### 5.1 Plugin 语义化版本

- `PATCH`：错误修复、提示词微调、单个平台规则修正；
- `MINOR`：增加向后兼容的新能力、新平台或新通用字段；
- `MAJOR`：调用方式、提示词结构或输入契约发生不兼容变化。

文档和测试记录的变化如果不影响 Plugin 分发内容，可以不升级 Plugin。

### 5.2 Skill 语义化版本

每个 Skill 独立遵循相同规则。发布脚本默认让 Plugin 使用与组件变化相同的升级级别；允许把 Plugin 升级级别调高，但不允许低于组件变化级别。

### 5.3 回退不复用旧版本号

如果毓数 `1.3.3` 有问题，需要恢复 `1.3.2` 的行为，则新发布版本为 `1.3.4`，并在变更记录中说明“恢复 1.3.2 行为”。正式发布不得把版本号从 `1.3.3` 改回 `1.3.2`。

临时安装历史 Git 标签不受此规则限制，因为它是在安装一个真实存在的旧快照，而不是创建新发布。

## 6. 仓库新增内容

```text
qfin-list-page/
├── CHANGELOG.md
├── versions.json
├── scripts/
│   ├── release.py
│   ├── rollback_skill.py
│   ├── install_version.py
│   └── versioning_lib.py
└── tests/
    ├── test_version_manifest.py
    ├── test_release.py
    ├── test_rollback_skill.py
    └── test_install_version.py
```

三个公开脚本分别服务于发布、单 Skill 恢复和整个 Plugin 历史版本安装。`versioning_lib.py` 只承载共享校验逻辑，不作为用户命令。

## 7. `versions.json`

`versions.json` 是当前提交对应的机器可读版本组合：

```json
{
  "schemaVersion": 1,
  "pluginVersion": "0.1.0",
  "components": {
    "qfin-list-page": "0.1.0",
    "qifu-yushu-list-page": "1.3.2",
    "qifu-jinyumeng-list-page": "0.7.2",
    "qifu-dianxiao-list-page": "0.1.0"
  }
}
```

校验规则：

- `pluginVersion` 必须等于 Plugin manifest 中的版本；
- 每个组件版本必须等于对应 `VERSION` 文件；
- 必须且只能包含四个组件；
- 所有版本必须是合法语义化版本。

历史组合不需要额外复制文件；它随 Git 标签一起保留。

## 8. `CHANGELOG.md`

`CHANGELOG.md` 是给维护者和使用者阅读的发布记录。每个 Plugin 版本记录：

- 发布日期；
- 修改的组件及新版本；
- 变更或回退原因；
- 明确未修改的组件；
- 对应 Git 标签。

回退记录必须说明恢复了哪个历史版本的行为，不能只写“修复问题”。

## 9. 自动化命令

### 9.1 `release.py`

用途：准备和验证新发布。

示例：

```bash
python3 scripts/release.py \
  --component yushu \
  --bump patch \
  --note "统一筛选区为带标题、按钮触发"
```

默认行为为 dry-run，只输出：

- 检测到的修改目录；
- 即将变化的 Skill 和 Plugin 版本；
- `versions.json` 与 `CHANGELOG.md` 预览；
- 将运行的测试和校验；
- 建议的 Git 标签。

只有追加 `--apply` 才允许写入版本文件、`versions.json` 和 `CHANGELOG.md`。脚本不自动提交、不自动打标签、不自动推送。完成验证后，由维护者检查差异，再手工提交并创建标签。

安全规则：

- 工作区存在无关未提交修改时停止；
- 声明的组件与实际修改目录不一致时停止；
- 新版本不大于已发布版本时停止；
- 任一测试或校验失败时停止，并保留可审查差异。

### 9.2 `rollback_skill.py`

用途：从正式 Git 标签只恢复一个 Skill。

示例：

```bash
python3 scripts/rollback_skill.py --skill yushu --to v0.1.0
```

默认 dry-run 输出目标 Skill 的文件差异、目标标签中的版本、其他三个 Skill 的当前哈希，以及将执行的测试。

`--skill` 接受 `router`、`yushu`、`jinyumeng` 或 `dianxiao`。`--apply` 执行以下步骤：

1. 要求工作区干净；
2. 将当前目标 Skill 复制到被 `.gitignore` 排除的 `.qfin-backups/<timestamp>/`；
3. 从目标标签恢复该 Skill 的行为文件，但保留当前 `VERSION`，避免回退过程复用旧版本号；
4. 重新计算所有非目标 Skill 的树哈希；
5. 如果非目标组件发生任何变化，立即停止并恢复备份；
6. 运行目标 Skill 的现有测试和契约校验；
7. 输出下一步 `release.py` 命令。

该脚本不升级版本、不提交、不发布。恢复后的工作区是一个等待发布的临时状态：行为来自目标标签，`VERSION` 仍是回退前版本。随后必须通过 `release.py` 将目标 Skill 和 Plugin 升级到新的正式补丁版本。

### 9.3 `install_version.py`

用途：临时安装整个 Plugin 的历史版本，不修改 `main`。

示例：

```bash
python3 scripts/install_version.py --tag v0.1.0
```

默认 dry-run 输出：

- 标签是否存在；
- 标签内 `versions.json` 的四个组件版本；
- 当前已安装 Plugin 版本；
- marketplace 和 Plugin 将发生的变化；
- 恢复当前版本的命令。

`--apply` 使用独立、可清理的 detached Git worktree 检出目标标签，然后：

1. 验证历史 Plugin、路由和 `versions.json`；
2. 移除当前 `qfin-list-page` Plugin 安装；
3. 将 marketplace 临时切换到历史 worktree；
4. 安装该标签中的 Plugin；
5. 检查版本、启用状态和四个 Skill 目录；
6. 提醒用户必须新建 Codex 任务测试。

如果安装失败，脚本重新注册原仓库 marketplace 并重新安装执行前版本。脚本提供 `--restore-current` 将安装来源恢复到当前 `main` 仓库。

## 10. 回退工作流

### 10.1 未提交的错误修改

先查看目标目录差异并生成备份，只恢复明确指定的文件或 Skill。不得使用 `git reset --hard`。

### 10.2 已提交但未发布

单一、隔离的错误提交使用 `git revert`。如果一个提交混合修改多个组件，则从最后一个稳定提交只恢复目标 Skill，并创建新的修复提交。

### 10.3 已发布的单 Skill 问题

```text
rollback_skill.py dry-run
        ↓
rollback_skill.py --apply
        ↓
人工检查恢复差异
        ↓
release.py dry-run
        ↓
release.py --apply
        ↓
全量验证、提交、创建新 Plugin 标签
```

### 10.4 已发布的整个 Plugin 问题

临时止损：

```text
install_version.py --tag <last-good-tag> dry-run
        ↓
install_version.py --tag <last-good-tag> --apply
        ↓
新建 Codex 任务验证
```

永久修复：在 `main` 上通过 `git revert` 或按标签恢复对应源文件，使用 `release.py` 发布新的补丁版本。旧标签保持不变。

## 11. 完整性与故障处理

- 单 Skill 恢复前后，为所有非目标 Skill 建立内容与权限位清单；
- 使用现有 `scripts/compare_skill_trees.py` 的 SHA-256 与权限位比较能力；
- 任何非目标差异都使操作失败；
- 任何测试失败都禁止创建发布标签；
- 不从 `/Users/panyue/.codex/plugins/cache/` 复制文件回仓库；
- 不直接编辑已安装 Plugin；
- 自动化脚本发生异常时保留备份、命令输出和工作区差异，便于人工恢复；
- 安装级回退失败时优先恢复原 marketplace 与原安装版本。

## 12. 测试与验收

实现必须覆盖以下场景：

1. `versions.json` 与四个 `VERSION`、Plugin manifest 完全一致；
2. dry-run 不产生任何文件、Git 或 Plugin 安装状态变化；
3. 单 Skill 恢复只改变目标目录；
4. 目标标签缺失、工作区不干净或组件名错误时失败关闭；
5. 非目标 Skill 哈希变化时自动停止；
6. 旧版本号复用或版本倒退时失败；
7. 历史 Plugin 安装使用 detached worktree，不切换 `main`；
8. 历史安装失败时能够恢复执行前安装；
9. 发布前运行仓库测试、路由测试、目标 Skill 测试和 Plugin 校验；
10. 三个平台 Skill 的业务内容在引入版本管理机制时保持不变。

## 13. 首次启用

版本管理功能完成并验证后：

1. 以当前四个组件版本生成首份 `versions.json`；
2. 在 `CHANGELOG.md` 中记录现有 `0.1.0` Plugin 基线；
3. 全量验证仓库与 Plugin；
4. 创建首个正式标签 `v0.1.0`；
5. 标签只在本地创建，不自动推送 GitHub；
6. 保持当前本地 Plugin 安装不变，除非用户明确要求重新安装。

## 14. 关键决策

- Plugin 是唯一安装单位，Skill 是独立开发与恢复单位；
- 单 Skill 的已发布回退采用“恢复旧行为、发布新版本”；
- 整个 Plugin 可以临时安装历史标签；
- Git 标签是正式历史来源，缓存和手工归档不是发布来源；
- 三个公开脚本均默认 dry-run；
- 自动化止于修改与验证，不自动提交、打标签或推送。
