# 平台 Skill 导入完整性记录（2026-10-13）

## 结论

毓数、金毓盟、电销三个平台 Skill 均由现有本地安装目录完整复制进入 Plugin。最终核对结果为：文件集合一致、逐文件 SHA-256 一致、权限位一致；未修改任何平台 Skill 的内容。

运行环境：`Python 3.10.11`。

## 源与目标

| 平台 | 源目录 | Plugin 内目标目录 | 契约版本 |
| --- | --- | --- | --- |
| 毓数 | `/Users/panyue/.codex/skills/qifu-yushu-list-page` | `plugins/qfin-list-page/skills/qifu-yushu-list-page` | `1.3.2` |
| 金毓盟 | `/Users/panyue/.codex/skills/qifu-jinyumeng-list-page` | `plugins/qfin-list-page/skills/qifu-jinyumeng-list-page` | `0.7.2 (draft+acceptance_trial)` |
| 电销 | `/Users/panyue/.codex/skills/qifu-dianxiao-list-page` | `plugins/qfin-list-page/skills/qifu-dianxiao-list-page` | `0.1.0 (draft)` |

## 验证命令与结果

三个目标目录均执行以下检查，其中 `<skill>` 分别替换为三个 Skill 名称：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s "plugins/qfin-list-page/skills/<skill>/tests" -p 'test_*.py' -v

PYTHONDONTWRITEBYTECODE=1 python3 \
  "plugins/qfin-list-page/skills/<skill>/scripts/validate_skill_contract.py" \
  "plugins/qfin-list-page/skills/<skill>"

python3 scripts/compare_skill_trees.py \
  "/Users/panyue/.codex/skills/<skill>" \
  "plugins/qfin-list-page/skills/<skill>"
```

| Skill | 单元测试 | 契约校验 | 内容与权限比对 |
| --- | ---: | --- | --- |
| `qifu-yushu-list-page` | 20/20 PASS | `PASS qifu-yushu-list-page 1.3.2` | `PASS` |
| `qifu-jinyumeng-list-page` | 44/44 PASS | `PASS qifu-jinyumeng-list-page 0.7.2 (draft+acceptance_trial)` | `PASS` |
| `qifu-dianxiao-list-page` | 9/9 PASS | `PASS qifu-dianxiao-list-page 0.1.0 (draft)` | `PASS` |

## 过程备注

首次执行测试时，Python 在目标目录生成或刷新了 `__pycache__`，完整性工具正确识别出差异。随后没有手工修改子 Skill，而是从源目录重新整目录复制，并使用 `PYTHONDONTWRITEBYTECODE=1` 重新运行测试与校验；最终三个目录均再次获得 `PASS`。

## 仓库完成后的全量复验

完成路由、提示词模板和 README 后再次执行全量验证，结果如下：

| 检查 | 结果 |
| --- | --- |
| 仓库级测试 | 10/10 PASS |
| 路由 Skill 测试 | 9/9 PASS |
| 路由契约校验 | `PASS qfin-list-page 0.1.0` |
| 官方 Skill 校验器 | `Skill is valid!` |
| 官方 Plugin 校验器 | `Plugin validation passed` |
| 三个平台子 Skill 测试 | 20/20、44/44、9/9 PASS |
| 三个平台契约校验 | 全部 PASS |
| 三个平台源目录与仓库目录比对 | 三次 `PASS` |

全量复验同样设置 `PYTHONDONTWRITEBYTECODE=1`，因此没有改变已导入子 Skill 的内容。

## 本地 Plugin 迁移证据

2026-10-13 在迁移前再次完成全部验证，结果与上表一致。随后执行可恢复迁移：

- 四个旧独立安装已移动至 `/Users/panyue/.codex/skills-archive/qfin-list-page-pre-plugin-2026-10-13/`；每个归档目录的 `SKILL.md` 均存在。
- `/Users/panyue/.codex/skills/` 下不再存在 `qifu-list-page`、`qifu-yushu-list-page`、`qifu-jinyumeng-list-page`、`qifu-dianxiao-list-page`，因此不会与 Plugin 重复发现。
- 本地仓库 marketplace 注册结果：`marketplaceName=qfin-list-page`，`alreadyAdded=false`。
- Plugin 安装结果：`pluginId=qfin-list-page@qfin-list-page`，`version=0.1.0`，`installed=true`，`enabled=true`。
- Plugin 源指向本仓库的 `plugins/qfin-list-page`；安装缓存为 `/Users/panyue/.codex/plugins/cache/qfin-list-page/qfin-list-page/0.1.0`。
- 安装缓存中的 Skill 目录恰好为 `qfin-list-page`、`qifu-yushu-list-page`、`qifu-jinyumeng-list-page`、`qifu-dianxiao-list-page`。
- 安装后再次运行官方 Plugin 校验器，结果为 `Plugin validation passed`。

实际运行时的 Skill 发现需要在新的 Codex 任务中验证；本次迁移没有创建或修改任何 Figma 页面。

## 版本管理引入复验（2026-10-14）

版本管理以提交 `26051cf` 作为四个 Skill 树的业务内容基线。在实现 `versions.json`、`CHANGELOG.md`、发布、单 Skill 恢复和历史 Plugin 安装脚本后，执行：

```bash
git diff 26051cf -- \
  plugins/qfin-list-page/skills/qfin-list-page \
  plugins/qfin-list-page/skills/qifu-yushu-list-page \
  plugins/qfin-list-page/skills/qifu-jinyumeng-list-page \
  plugins/qfin-list-page/skills/qifu-dianxiao-list-page
```

命令无输出，证明四个 Skill 树没有变化。版本管理只增加仓库根级元数据、自动化脚本、测试和维护文档。

本次复验结果：

| 检查 | 结果 |
| --- | --- |
| 仓库级测试 | 36/36 PASS |
| 路由 Skill 测试 | 9/9 PASS |
| 路由契约校验 | `PASS qfin-list-page 0.1.0` |
| 官方 Skill 校验器 | `Skill is valid!` |
| 三个平台子 Skill 测试 | 20/20、44/44、9/9 PASS |
| 三个平台契约校验 | 全部 PASS |
| Codex CLI 本地 Plugin 解析 | `version=0.1.0`、`installed=true`、`enabled=true` |
| `versions.json` 与 Plugin/四个 Skill 版本一致性 | PASS |

当前 Codex 安装中仍有官方 `quick_validate.py` Skill 校验器，但不再提供之前使用的独立 `plugin-creator/scripts/validate_plugin.py`。因此本次 Plugin 有效性由仓库布局契约测试和 `codex plugin list --marketplace qfin-list-page --available --json` 的官方 CLI 解析结果共同确认。
