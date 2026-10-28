# 每次生成验收

- source为6155:1851的克隆，1366×768；Header48、侧栏200、Tabs及渐变保留，原源节点不变。
- 所有业务菜单的mainComponent真实owner为6158:1989，正好一个当前叶子Selected；祖先展开，其他项收起。
- 空白RECTANGLE只在副本被内容Frame取代；内容边界216,102,1134,633，内部按auto-layout排布，无溢出。
- 表头列数、每行单元格数、选择列与PageSpec一致，列不机械等宽，分页可见且计数正确。
- 所有可见文字绑定批准样式；组件内部缺口不能靠实例字体覆盖掩盖。主题Mode2158:0、语义色实际回读，不能仅比对名称。
- 构建ComponentResolutionManifest、TextStyleResolutionManifest，读后核对公开属性/Slot及实例关系。
- 整页截图检查菜单、筛选、表格、分页、长文本与空态，无裁切、重叠或占位残留。

结构与截图分别返回PASS/FAIL，最终完成需两者均PASS。preflight-required不是ready保证；未完成样式预检时返回BLOCKED并保留可回退副本。
