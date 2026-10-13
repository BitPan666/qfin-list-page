# Platform Jinyumeng baseline

## Fixed identity

`platform=jinyumeng`

## Confirmed evidence

- Target file: 奇富科技中后台组件库-新.
- Source page: `SideMenu 侧边菜单`, node `3161:10805`.
- Reference layout: `Frame 1`, node `4856:1408`, width `1366px`.
- The page shell uses a light-blue platform background. Top navigation and the sidebar sit on that background; content regions are carried by white surfaces.
- Right-side white surfaces keep 20px from the sidebar and 20px from the viewport right edge.
- The internal tab bar, standalone or table-integrated list actions, and the basic xlarge Jinyumeng Table family now have confirmed page and component contracts.
- Jinyumeng Input, Select, DatePicker, DateRange, Filter Item, the three-layer list-page Shell, Loading, and Empty/Error component identities now have confirmed mappings.
- The filter region now has a confirmed responsive composition: fixed-width Filter Items are centered in dynamically equalized columns, and the query/reset/expand group occupies one additional Filter Item Slot after the visible filters.
- The confirmed Jinyumeng Header is transparent, `56px` high, and contains the fixed brand lockup, notification entry, and user area; only the account name is editable.
- The right-side list page may use the screenshot's broad region order only as a draft Jinyumeng information-architecture hypothesis. It must be confirmed within this platform and never authorizes importing another platform's rules, component IDs, or tokens.

## Navigation policy

- The existing `JYM-SideMenuItem` component set covers first-, second-, and third-level menu items.
- The currently mapped sidebar menu is the complete first-level 线上平台菜单 preset.
- Business prompts provide the hierarchy below each first-level menu as `一级菜单 > 二级菜单 > 三级菜单`; second- and third-level siblings follow the prompt and reuse `JYM-SideMenuItem`.
- Each first-level menu icon must map to the corresponding 真实 `Icon/jinyumeng/*` 组件 already present in the component library.
- 禁止手绘、猜测或用通用占位图标替代 a known online menu icon.
- Expand the active ancestor path required by the requested current menu; do not invent unprovided lower-level menu labels.

## Platform isolation

- Jinyumeng rules live only in this skill package.
- Changes here must not modify or loosen the stable Yushu skill.
- Shared-basic components are allowed only when explicitly mapped; platform-specific fallbacks are forbidden.

## PENDING release blockers

- PENDING complete-page instance readback, screenshot comparison, and acceptance evidence.
- 反馈状态标记为 DEFERRED from the first normal-data acceptance trial; it is not a current release blocker.
- 不得猜测 any missing platform resource or behavior.

Formal platform execution remains `BLOCKED`; only the exact bounded `acceptance_trial` in SKILL.md may write to Figma.
