// Executable Figma regression fixture; loads only the registered SmartOps shell.
// Creates a separate editable trial. Run through figma-use, never a browser.
const page = await figma.getNodeByIdAsync('3497:651');
await figma.setCurrentPageAsync(page);
const trialName = 'Trial / 20261028-233328 / 智客星 / 加微链接';
const existing = page.children.find(n => n.name === trialName);
if (existing) return {status: 'EXISTS', nodeId: existing.id};
const source = await figma.getNodeByIdAsync('5468:3233');
const variantIds = {input:'3406:853', button:'2381:2318', header:'3350:5950', row:'3391:6043', cell:'3373:6047', text:'3368:6021', pagination:'3698:39216'};
const components = {};
for (const [key,id] of Object.entries(variantIds)) {
  let n = await figma.getNodeByIdAsync(id);
  if (n.type === 'COMPONENT_SET') n = n.children.find(c => c.type === 'COMPONENT' && (key === 'input' ? c.name.includes('M 默认尺寸') && c.name.includes('Placeholder') && c.name.includes('Default') : c.name.includes('base 基础') && c.name.includes('medium') && c.name.includes('n/a') && c.name.includes('normal')));
  if (!n || n.type !== 'COMPONENT') throw new Error('COMPONENT_MISSING: '+key);
  components[key] = n;
}
const fonts = new Map();
for (const n of [source,...Object.values(components)]) for (const t of n.findAllWithCriteria({types:['TEXT']})) for (const s of t.getStyledTextSegments(['fontName'])) fonts.set(JSON.stringify(s.fontName),s.fontName);
await Promise.all([...fonts.values()].map(f=>figma.loadFontAsync(f)));
const created = [];
function remember(n) {created.push(n.id);return n;}
function frame(name,direction,w,h) {const n=remember(figma.createAutoLayout(direction));n.name=name;n.resize(w,h);n.primaryAxisSizingMode='FIXED';n.counterAxisSizingMode='FIXED';n.fills=[];return n;}
function instance(key) {return remember(components[key].createInstance());}
function prop(n,prefix,value) {const entries=Object.entries(n.componentProperties).filter(([k])=>k.startsWith(prefix));if(entries.length!==1)throw new Error('PROPERTY_MISSING:'+prefix);n.setProperties({[entries[0][0]]:value});if(n.componentProperties[entries[0][0]].value!==value)throw new Error('PROPERTY_READBACK:'+prefix);}
function slot(n,prefix) {const s=n.findAllWithCriteria({types:['SLOT']}).filter(x=>x.name.startsWith(prefix));if(s.length!==1)throw new Error('SLOT_MISSING:'+prefix);for(const c of [...s[0].children])c.remove();return s[0];}
const out=remember(source.clone());page.appendChild(out);out.name=trialName;
out.x=Math.max(0,...page.children.filter(n=>n.id!==out.id).map(n=>n.x+n.width))+120;out.y=200;
const surface=out.findOne(n=>n.type==='FRAME'&&n.name==='Page Surface');
if(!surface)throw new Error('CONTENT_SOURCE_MISSING');
for(const c of [...surface.children])c.remove();
const content=frame('Content / 加微链接','VERTICAL',1134,600);surface.appendChild(content);content.fills=[];content.paddingLeft=24;content.paddingRight=24;content.paddingTop=24;content.paddingBottom=24;content.itemSpacing=20;
for(const i of out.findAllWithCriteria({types:['INSTANCE']})){const m=await i.getMainComponentAsync();if(m?.parent?.id==='3178:9659'){const key=Object.keys(i.componentProperties).find(k=>k.startsWith('text#'));if(key){const value=i.componentProperties[key].value;if(value==='未选中菜单')prop(i,'text#','客户添加');if(value==='选中菜单')prop(i,'text#','加微链接');}}if(m?.parent?.id==='2381:2318'){const key=Object.keys(i.componentProperties).find(k=>k.startsWith('text 文案'));if(key&&i.componentProperties[key].value==='新建任务')prop(i,'text 文案','新建链接');}}
const businessTabs={'任务管理':'链接管理','触发式任务':'加微链接','任务模板':'渠道统计','临时分配':'分配记录'};
for(const t of out.findAllWithCriteria({types:['TEXT']})){if(!t.id.startsWith('I')&&businessTabs[t.characters]){for(const seg of t.getStyledTextSegments(['fontName']))await figma.loadFontAsync(seg.fontName);t.characters=businessTabs[t.characters];}}
const collection=await figma.variables.getVariableCollectionByIdAsync('VariableCollectionId:9:8');
// Preserve candidate inheritance: never force the Yushu mode.
const headerOwners=[];for(const i of out.findAllWithCriteria({types:['INSTANCE']})){const m=await i.getMainComponentAsync();if(m?.parent?.id==='5517:2109')headerOwners.push(m.parent.id);if(m?.parent?.id==='3639:1529')throw new Error('FOREIGN_HEADER');}
if(headerOwners.length!==1)throw new Error('HEADER_READBACK');
const filter=frame('Filter / 链接名称','HORIZONTAL',1086,32);content.appendChild(filter);filter.itemSpacing=12;
const input=instance('input');filter.appendChild(input);input.resize(240,32);prop(input,'value 文本','请输入链接名称');prop(input,'prefixIcon',false);
const query=instance('button');filter.appendChild(query);prop(query,'text 文案','查询');
const reset=instance('button');filter.appendChild(reset);prop(reset,'variant 类型','outline 描边');prop(reset,'text 文案','重置');
const table=frame('Table / 三列任务数据','VERTICAL',1086,176);content.appendChild(table);
const head=frame('Header / Columns','HORIZONTAL',1086,44);table.appendChild(head);
const widths=[470,240,376], titles=['链接名称','链接状态','创建时间'];
for(let i=0;i<3;i++){const n=instance('header');head.appendChild(n);n.resize(widths[i],44);prop(n,'headerText',titles[i]);prop(n,'showSort',false);prop(n,'showFilter',false);}
const values=[['官网咨询入口','启用','2026-10-28 10:00'],['活动加微入口','草稿','2026-10-27 15:30'],['门店服务入口','停用','2026-10-26 09:20']];
for(const valuesRow of values){const row=instance('row');table.appendChild(row);row.resize(1086,44);const cells=slot(row,'cellsSlot');cells.resize(1086,44);for(let i=0;i<3;i++){const cell=instance('cell');cells.appendChild(cell);cell.resize(widths[i],44);const target=slot(cell,'contentSlot');const txt=instance('text');target.appendChild(txt);prop(txt,'value 文案',valuesRow[i]);}}
const footer=frame('Pagination / Right','HORIZONTAL',1086,32);content.appendChild(footer);footer.primaryAxisAlignItems='MAX';
const pagination=instance('pagination');footer.appendChild(pagination);prop(pagination,'total 总数','共 3 项数据');prop(pagination,'showJumper',false);prop(pagination,'showPageSize',false);
const texts=out.findAllWithCriteria({types:['TEXT']});
const missing=texts.filter(t=>!t.textStyleId||t.textStyleId===figma.mixed).map(t=>({id:t.id,text:t.characters,parent:t.parent.id,parentType:t.parent.type}));
return {status:missing.length?'STYLE_GAPS':'STRUCTURE_CREATED',createdNodeIds:created,nodeId:out.id,sourceId:source.id,contentId:content.id,rows:values.length,columns:titles.length,modeId:out.explicitVariableModes[collection.id],missingTextStyles:missing};
