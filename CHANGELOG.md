# Changelog

## 0.2.0 - 2026-10-28

- Add independent Zhikexing and SmartOps list adapters 0.1.0 with per-run preflight and read-only plan CLIs.
- Router 0.2.0 covers all five platforms and preserves child readiness.
- Version/release/rollback tools recognize six current components and retain four-component historical release support.
- Original Yushu, Jinyumeng and Dianxiao child trees remain unchanged.

## 0.1.2 — 2026-10-28

- Router payload `0.1.0` → `0.1.1`：新增五平台离线资产注册、验证器和变异测试；运行时仍仅路由毓数、金毓盟、电销。
- 智客星保持 Candidate，智能运营登记已核查 Frame；两者均为 `pending-adapter`，没有新增生成验收。
- 三个子 Skill 的全部文件和版本保持原样。源码时间线及恢复方式见 `docs/iterations/2026-10-28-five-platform-foundation.md`。

## 0.1.1 — 2026-10-14

- 同步本次已验证的本地 Skill 修订：毓数 1.3.3、金毓盟 1.0.0、电销 1.0.0。
- 金毓盟与电销启用正式使用，目标 Page 由用户指定。
- 金毓盟未特别说明时默认画板 1366×768，支持用户明确覆盖尺寸。
- README 补充新电脑安装、Figma 独立授权、版本核对和更新流程。
- 本次为一次性回收已验证的安装缓存修改；后续以仓库源码作为唯一维护源。

## 0.1.0 - 2026-10-14

- Plugin: `0.1.0`.
- `qfin-list-page`: `0.1.0`.
- `qifu-yushu-list-page`: `1.3.2`.
- `qifu-jinyumeng-list-page`: `0.7.2`.
- `qifu-dianxiao-list-page`: `0.1.0`.
- Added dry-run-first release, single-Skill recovery, and historical Plugin installation tooling without changing any Skill tree.
- Baseline tag: `v0.1.0` (created after the version-management implementation is validated).
