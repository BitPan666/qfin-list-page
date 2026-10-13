---
name: qfin-list-page
description: Use when creating, updating, or auditing a standard QFIN desktop data list page for the Yushu, Jinyumeng, or Dianxiao platform and the request must be routed to exactly one platform-specific Skill.
---

# QFIN List Page Router

This Skill is the single entry point for standard QFIN desktop data list-page creation, update, and audit requests. It selects one platform Skill and does not contain or combine platform implementation rules.

## Route map

| `platform` | Explicit names | Child Skill |
| --- | --- | --- |
| `yushu` | `yushu`, `毓数` | [`qifu-yushu-list-page`](../qifu-yushu-list-page/SKILL.md) |
| `jinyumeng` | `jinyumeng`, `金毓盟` | [`qifu-jinyumeng-list-page`](../qifu-jinyumeng-list-page/SKILL.md) |
| `dianxiao` | `dianxiao`, `电销`, `电销平台` | [`qifu-dianxiao-list-page`](../qifu-dianxiao-list-page/SKILL.md) |

There is no default platform. Never default to Yushu or infer a platform from visual similarity.

## RoutingContext

Before routing, retain this context without rewriting the user's request:

- `platform`: canonical platform value when resolved;
- `intent`: `create`, `update`, or `audit`;
- `target`: optional target file or Figma Page supplied by the user;
- `rawRequest`: the complete, unmodified user request;
- `evidence`: the explicit field, explicit platform name, or confirmed target context used for selection.

## Routing procedure

1. Confirm that the request is for a standard QFIN desktop data list page and that its intent is create, update, or audit.
2. Resolve the platform in this order: an explicit `platform` field; otherwise one unique explicit platform name; otherwise one unique platform confirmed by the target file/Page context.
3. If no supported platform is resolved, or more than one is present, stop with the applicable routing error below. Do not guess.
4. Resolve the selected route against this Skill directory. If its `SKILL.md` is absent, stop with `CHILD_SKILL_MISSING`; there is no fallback.
5. Load exactly one child Skill. Read that child `SKILL.md` completely, and resolve every later relative reference against the selected child directory.
6. Pass the unmodified raw request to the child together with the RoutingContext. Stop applying parent generation rules after handoff.
7. The child owns PageSpec, execution, and validation after handoff.
8. Preserve child readiness and native status verbatim. Do not upgrade `PASS`, `FAIL`, `BLOCKED`, draft, acceptance-trial, or readiness wording.
9. Return the child result together with `selectedPlatform`, `selectedSkill`, and `routingEvidence`. These routing fields must not weaken, reinterpret, or replace the child result.

## Fail-closed routing errors

- `PLATFORM_REQUIRED`: no explicit or uniquely confirmed supported platform is available. Ask the user to choose 毓数、金毓盟或电销.
- `PLATFORM_CONFLICT`: the request or confirmed context identifies more than one supported platform. Ask the user to select exactly one.
- `UNSUPPORTED_PLATFORM`: an explicit platform value is present but is not `yushu`, `jinyumeng`, or `dianxiao`. Stop without substituting another platform.
- `CHILD_SKILL_MISSING`: the selected child `SKILL.md` cannot be resolved. Stop; no fallback to another child is allowed.

## Boundary

This router must not define platform component IDs, navigation structures, menu definitions, PageSpec fields, Figma generation instructions, or platform-specific validation rules. Those remain entirely inside the selected child Skill.
