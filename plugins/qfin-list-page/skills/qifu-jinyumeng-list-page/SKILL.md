---
name: qifu-jinyumeng-list-page
description: Use when explicit requests concern Qifu Jinyumeng list pages, their confirmed rules, component mappings, audits, or readiness-gated Figma work.
---

# Qifu Jinyumeng List Page

## Overview

This is the platform-isolated Jinyumeng list-page skill. Its fixed identity is `platform=jinyumeng` and its current maturity is `readiness=draft` with one bounded `acceptance_trial` write path.

The draft may record and audit confirmed evidence, including the Jinyumeng header/sidebar, internal tabs, mode-aware shared buttons, filter adapters, page Shells, feedback components, and Jinyumeng Table family. Formal business-page writes remain blocked; only the exact acceptance trial below is authorized.

## Readiness gate

在 `readiness=ready` 前，除受限验收试生成外，生成或修改 Figma 页面请求必须停止并报告缺失项。平时只允许只读检查、规则录入、映射补全、契约校验和回归验证。

- DEFERRED 反馈状态：Empty、Loading、Error 不进入首轮正常数据列表页验收，也不阻塞本轮 `acceptance_trial`。
- CONFIRMED 完整组件映射：当前列表页范围内的 Header、Sidebar、Tabs、Button、Filter、Shell、Table、Pagination 与反馈组件均已登记；不得替换或回退。
- PENDING 完整验收：完整页面的实例关系、视觉回读与通过标准尚未闭环。

## Bounded acceptance trial

Only treat a request as `acceptance_trial` when every condition below is true:

1. The user explicitly invokes this Skill and Figma, requests a complete-page structure readback and screenshot check, and targets the existing Page `测试qifu-jinyumeng-list-page skill`, node `5037:8717`.
2. The requested page uses 正常数据状态. Empty, Loading, and Error are excluded.
3. 只新建一个顶层验收画板 inside that Page. New descendants may be assembled only inside this frame.
4. 不得修改、删除或覆盖该 Page 中任何已有节点, component master, variable, style, or any node outside the new acceptance frame.
5. The trial uses only mapped Jinyumeng or explicitly shared-basic component instances and keeps the page at `readiness=draft` after execution.
6. Any component resolution, property, Instance swap, Slot, readback, or screenshot failure returns `FAIL`; do not hand-draw a replacement and do not broaden the write scope.

All other writes, including any formal business Page, remain prohibited: 正式业务 Page 继续 BLOCKED.

不得回退到 `qifu-yushu-list-page`、`qifu-list-page`，禁止手绘占位，也不得借用其他平台的规则、组件、节点 ID 或视觉细节。未知信息一律标记为 `PENDING` 或 `BLOCKED`，不得猜测。

Blocked response:

```text
BLOCKED readiness=draft platform=jinyumeng
Missing: PENDING 完整验收；request does not satisfy the bounded acceptance_trial contract.
Confirmed rules may be audited, but no Figma generation or modification was attempted.
```

## Reference routing

Read only the references relevant to the request:

- [Page rules](references/page-rules.md): confirmed top header, content surfaces, internal tabs, filter-region layout, list-operation placement, dynamic table composition, typography, and responsive behavior.
- [Component map](references/component-map.md): confirmed Jinyumeng header/sidebar, internal Tag tabs, mode-aware shared Button, filter adapters, page Shells, feedback components, Jinyumeng Table family, and icon mappings.
- [Component invocation contract](references/component-invocation-contract.md): instance-only invocation boundary and unresolved writes.
- [Structural validation](references/structural-validation.md): checks that are already measurable and remaining release blockers.
- [Platform baseline](references/platform-jinyumeng.md): platform identity, source evidence, navigation policy, and isolation rules.

Run `scripts/validate_skill_contract.py` after every change. A validator failure is a release block, not permission to infer missing details.

## Exit condition

Only change `readiness=draft` to `readiness=ready` after the bounded acceptance trial passes and the user accepts its evidence. The draft remains fail-closed for every write outside the exact trial contract.
