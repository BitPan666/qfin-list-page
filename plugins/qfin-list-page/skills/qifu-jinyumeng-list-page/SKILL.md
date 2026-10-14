---
name: qifu-jinyumeng-list-page
description: Use when explicit requests concern Qifu Jinyumeng list pages, their confirmed rules, component mappings, audits, or readiness-gated Figma work.
---

# Qifu Jinyumeng List Page

## Overview

This platform-isolated skill creates, updates, and audits standard Jinyumeng list pages with real component instances. Fixed identity: `platform=jinyumeng`.

## 正式使用与目标位置

当前 `readiness=ready`，已由用户明确授权正式使用。允许在用户指定的 Figma 文件和目标 Page 中创建、更新或审计标准列表页，不限定测试 Page，不要求 acceptance_trial。

- 目标 Page 由用户指定；指定名称不存在时可新建同名 Page。缺少或存在同名歧义时先确认，不默认写入第一个 Page。
- 未特别说明时，桌面端画板默认宽 `1366px`、高 `768px`；用户明确指定尺寸或高度随内容调整时，以用户要求为准。溢出处理见 Page rules。
- 创建时新增独立画板；更新时仅修改用户明确指定的页面节点。保护无关已有内容，不擅自修改组件母版、变量或样式。
- 每次仍需完成组件解析、属性与实例关系回读、结构检查及整页截图；只有结构和视觉均为 PASS 才交付完成。
- 必需信息缺失返回 BLOCKED；组件调用或验收失败返回 FAIL，记录具体节点和原因，不手绘替代。
- 正式启用表示用户授权使用，不替代每次任务的实际验收，不宣称未经执行的测试已经通过。

CONFIRMED 完整组件映射：Header、Sidebar、Tabs、Button、Filter、Shell、Table、Pagination 与反馈组件均已登记。正常数据状态可正式生成。DEFERRED 反馈状态：Empty、Loading、Error 的未确认页面行为仍需针对需求补齐，不阻塞正常列表页。

不得回退到 `qifu-yushu-list-page`、`qifu-list-page`，禁止手绘占位。未知信息记录 PENDING，不得猜测其他平台资源。

## Reference routing

Read only the references relevant to the request:

- [Page rules](references/page-rules.md): confirmed top header, content surfaces, internal tabs, filter-region layout, list-operation placement, dynamic table composition, typography, and responsive behavior.
- [Component map](references/component-map.md): confirmed Jinyumeng header/sidebar, internal Tag tabs, mode-aware shared Button, filter adapters, page Shells, feedback components, Jinyumeng Table family, and icon mappings.
- [Component invocation contract](references/component-invocation-contract.md): instance-only invocation boundary and unresolved writes.
- [Structural validation](references/structural-validation.md): checks that are already measurable and remaining release blockers.
- [Platform baseline](references/platform-jinyumeng.md): platform identity, source evidence, navigation policy, and isolation rules.

Run `scripts/validate_skill_contract.py` after every change. A validator failure is a release block, not permission to infer missing details.

## Delivery

返回 Skill 版本、目标 Page 与画板链接、组件解析及属性回读摘要、结构与视觉 PASS/FAIL、真实缺口与输入假设。readiness=ready 不自动代表单次页面验收通过。
