# 智能运营平台与组件

来源Frame6155:1851，1366×768；Header6148:32454高48；菜单6158:1989宽200、项高40、Level1/2；Tabs6156:1989位于216,48，1134×38。内容矩形6148:34365位于216,102，1134×633。独立菜单与电销5763:1753不能互换。

主题集合VariableCollectionId:9:8，Mode2158:0。品牌语义基础颜色拓展/brand/default当前核验#1969F1；色值用于读后校验，写入使用语义变量绑定。源7处未绑定样式保留为源缺口，不因本轮新增Adapter删除历史事实。

共享组件：Input3406:853、Select2859:2820、DateRange2967:30327、Button2381:2318、FilterBar3473:36837、FilterItem3802:107、TableShell3433:8257、HeaderCell3350:5949、Row3393:6352、ContentCell3376:33871、Text3368:6025、Action3678:8875、Tag3178:9659、Pagination3698:482。组件集必须选真实合法变体，再createInstance；不把组件集当组件实例化。用组件名及key回读确认来源，不推测失效ID。

列表内容来源可以组合这些共享组件；不能从其他平台画板复制Header、菜单、Shell或固定业务数据。布局Frame容器不是发布组件。表格/筛选/分页内容按PageSpec动态填充，分页计数与data/state一致；rows为空时生成明确空态。

## 页级文字样式

本轮补齐保持原MiSans字体/字重/字号/行高的Platform Typography样式：Header标题16/24 Medium `S:f9daf042d61786b1e7f4a5b9cd7fce9cfeb58344,`，徽标10/16 Regular `S:13c62444a2c582d0519ff78ce9b14e2f4d887ed0,`，用户14/22 Regular `S:4403f8d541eaa622e2f6501abd27b6fc2947da90,`。克隆源外壳后只给对应页级Frame文字绑定；不在实例内覆盖字体。找不到样式必须重新发现并比对精确字体属性，不能只用近似名称替换。共享Tag、Input和Button受影响变体已单独备份后在组件本身补绑定，节点与恢复字段记录在本轮Figma时间线。源Frame的页级未绑定项仍保留，不能误称全部源资产已修复。
