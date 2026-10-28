// Executable Figma regression fixture; loads only the registered SmartOps shell.
// Creates a separate editable trial. Run through figma-use, never a browser.
const page = await figma.getNodeByIdAsync('3497:651');
await figma.setCurrentPageAsync(page);
const trialName = 'Trial / 20261028-233328 / 智能运营 / 模板策略';
const existing = page.children.find(n => n.name === trialName);
if (existing) return {status: 'EXISTS', nodeId: existing.id};
const source = await figma.getNodeByIdAsync('6155:1851');
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
const pageStyleMap={'借条':'S:f9daf042d61786b1e7f4a5b9cd7fce9cfeb58344,','99+':'S:13c62444a2c582d0519ff78ce9b14e2f4d887ed0,','panyue':'S:4403f8d541eaa622e2f6501abd27b6fc2947da90,'};
for(const t of out.findAllWithCriteria({types:['TEXT']})){if(!t.id.startsWith('I')&&pageStyleMap[t.characters])await t.setTextStyleIdAsync(pageStyleMap[t.characters]);}
const tabs=out.children.find(n=>n.name==='Tabs / 工作区导航');
for(const i of tabs.findAllWithCriteria({types:['INSTANCE']})){if(Object.keys(i.componentProperties).some(k=>k.startsWith('text#'))){const value=Object.entries(i.componentProperties).find(([k])=>k.startsWith('text#'))[1].value;if(value==='未选中菜单1')prop(i,'text#','运营计划');if(value==='未选中菜单2')prop(i,'text#','策略实验');}}
const menus=[];
for(const i of out.findAllWithCriteria({types:['INSTANCE']})){const m=await i.getMainComponentAsync();if(m?.parent?.id==='6158:1989'){const p=i.componentProperties;const label=Object.entries(p).find(([k])=>k.startsWith('Label'))[1].value;const level=p.Level.value;const activeParent=level==='1'&&label==='运营计划';const activeLeaf=level==='2'&&label==='模板策略';prop(i,'State',activeParent||activeLeaf?'Selected':'Default');prop(i,'expanded 展开',activeParent?'True':'False');menus.push({id:i.id,label,level,state:i.componentProperties.State.value,expanded:i.componentProperties['expanded 展开'].value});}}
if(menus.filter(m=>m.level==='2'&&m.state==='Selected'&&m.label==='模板策略').length!==1)throw new Error('NAVIGATION_READBACK');
const blank=out.children.find(n=>n.type==='RECTANGLE'&&n.name==='Content / 空白内容区');
if(!blank)throw new Error('CONTENT_SOURCE_MISSING');
const content=frame('Content / 模板策略','VERTICAL',1134,633);out.appendChild(content);content.x=216;content.y=102;content.fills=blank.fills;content.cornerRadius=blank.cornerRadius;content.paddingLeft=24;content.paddingRight=24;content.paddingTop=24;content.paddingBottom=24;content.itemSpacing=20;blank.visible=false;
const collection=await figma.variables.getVariableCollectionByIdAsync('VariableCollectionId:9:8');
out.setExplicitVariableModeForCollection(collection,'2158:0');
const filter=frame('Filter / 策略名称','HORIZONTAL',1086,32);content.appendChild(filter);filter.itemSpacing=12;
const input=instance('input');filter.appendChild(input);input.resize(240,32);prop(input,'value 文本','请输入策略名称');prop(input,'prefixIcon',false);
const query=instance('button');filter.appendChild(query);prop(query,'text 文案','查询');
const reset=instance('button');filter.appendChild(reset);prop(reset,'variant 类型','outline 描边');prop(reset,'text 文案','重置');
const table=frame('Table / 三列动态数据','VERTICAL',1086,176);content.appendChild(table);
const head=frame('Header / Columns','HORIZONTAL',1086,44);table.appendChild(head);
const widths=[470,240,376], titles=['策略名称','策略状态','创建时间'];
for(let i=0;i<3;i++){const n=instance('header');head.appendChild(n);n.resize(widths[i],44);prop(n,'headerText',titles[i]);prop(n,'showSort',false);prop(n,'showFilter',false);}
const values=[['新客欢迎策略','启用','2026-10-28 10:00'],['沉睡客户唤醒','草稿','2026-10-27 15:30'],['权益到期提醒','启用','2026-10-26 09:20']];
for(const valuesRow of values){const row=instance('row');table.appendChild(row);row.resize(1086,44);const cells=slot(row,'cellsSlot');cells.resize(1086,44);for(let i=0;i<3;i++){const cell=instance('cell');cells.appendChild(cell);cell.resize(widths[i],44);const target=slot(cell,'contentSlot');const txt=instance('text');target.appendChild(txt);prop(txt,'value 文案',valuesRow[i]);}}
const footer=frame('Pagination / Right','HORIZONTAL',1086,32);content.appendChild(footer);footer.primaryAxisAlignItems='MAX';
const pagination=instance('pagination');footer.appendChild(pagination);prop(pagination,'total 总数','共 3 项数据');prop(pagination,'showJumper',false);prop(pagination,'showPageSize',false);
const texts=out.findAllWithCriteria({types:['TEXT']});
const missing=texts.filter(t=>!t.textStyleId||t.textStyleId===figma.mixed).map(t=>({id:t.id,text:t.characters,parent:t.parent.id,parentType:t.parent.type}));
return {status:missing.length?'STYLE_GAPS':'STRUCTURE_CREATED',createdNodeIds:created,nodeId:out.id,sourceId:source.id,contentId:content.id,rows:values.length,columns:titles.length,modeId:out.explicitVariableModes[collection.id],missingTextStyles:missing};
