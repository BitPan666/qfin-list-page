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
