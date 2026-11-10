import json,re,collections,html
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'funding-data.json').read_text()); cs=d['companies']; n=len(cs); ne=sum(len(c['events']) for c in cs)
old=(R/'index.html').read_text();css=old.split('<style>')[1].split('</style>')[0]
def amount(e):
 if e['amount'] is None:return '未拆分／未披露'
 return f"{e['currency']} {e['amount']/1e6:g}M"
md=f'''# OpenRaise · 2021 年以来 Seed–D 公司研究库

[可筛选展示板](https://42channel.github.io/doris/funding.html) · [CSV](funding.csv) · [结构化 JSON](funding-data.json) · [技术来源板](https://42channel.github.io/doris/)

截至 **{d['asOf']}**，收录 **{n} 家公司、{ne} 条历史符合轮次事件**。其中 {sum(c['evidenceStatus'].startswith('本次') for c in cs)} 家在本次检索一手来源，另有 {sum(c['evidenceStatus'].startswith('既有') for c in cs)} 家沿用已标注的既有一手来源快照。

{d['methodology']}

**覆盖边界：** {d['coverage']}

**更新状态：** {d['freshness']}

公司均为研究候选；公开收录不代表已联系、完成尽调或正式进入 OpenRaise 池。技术分类为研究归纳；金额不跨币种汇总，也不把多轮合计当单轮。当前状态未核验时明确保留“未全面核验”。

'''
for sector in ['模型与核心技术','AI Infra','Physical AI']:
 md+=f'## {sector}（{sum(c["direction"]==sector for c in cs)} 家）\n\n| 公司 | 技术方向 | 历史符合轮次／公告日期／原币金额 | 核验层／当前状态 | 口径备注 |\n|---|---|---|---|---|\n'
 for c in cs:
  if c['direction']!=sector:continue
  es='<br>'.join(f'[{e["round"]} · {e["date"]} · {amount(e)}]({e["sourceUrl"]})' for e in c['events'])
  notes='<br>'.join(dict.fromkeys(e['notes'] for e in c['events'] if e['notes']))
  md+='| '+' | '.join(str(x).replace('|','／').replace('\n',' ') for x in [c['name'],c['technology'],es,c['evidenceStatus']+'；'+c['status'],notes])+' |\n'
 md+='\n'
md+='## 待核验事件与公司线索\n\n部分公司已由其他事件进入上表，但以下事件本身不计入已确认事件数。尚无合格事件的公司也不计入上表公司数。\n\n| 公司 | 主线 | 待核验原因 | 线索 |\n|---|---|---|---|\n'
for p in d['pending']:md+=f'| {p["name"]} | {p["direction"]} | {p["reason"]} | [来源]({p["sourceUrl"]}) |\n'
md+='\n## 后续核验队列\n\n补齐中国及非英语市场一手融资公告；核对近两年新轮次与并购／上市状态；复核既有快照；补齐年／月精度事件的具体日期。未披露轮次保留为空。2021 年前的 Seed–D、2021 年后的 E+ 单独事件、债务融资和代币发行不计为合格 Seed–D 事件。公司只要存在窗口内其他合格事件即可保留，不因后来 E+ 或收购而删除。\n'
(R/'FUNDING.md').write_text(md)
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="OpenRaise 2021年以来Seed到D轮公司研究库：模型、AI Infra、Physical AI，逐条融资证据可追溯。"><title>OpenRaise · Seed–D 公司研究库</title><style>'''+css+'''
.hero{grid-template-columns:1.3fr 1fr}.hero h1{font-size:35px}.hero-right strong{font-size:48px}.chips{display:flex;gap:9px;flex-wrap:wrap;margin:20px 0}.chips span{background:#edf2e7;padding:6px 12px;border-radius:20px;font-size:12px}.status{color:#7f7454;font-size:11px}.event{margin-bottom:12px}.event:last-child{margin-bottom:0}.amount{display:block;color:#71806c;font-size:11px}.notes{max-width:290px;color:#7a836f;font-size:11px}.notes summary{cursor:pointer;color:#285842}.notes p{margin:8px 0}.tablewrap{max-height:850px}thead{position:sticky;top:0;z-index:1}td:first-child{min-width:210px}td:nth-child(3){min-width:220px}.toolbar label{display:grid;gap:3px;font-size:10px;color:#758478}.toolbar label input,.toolbar label select{font-size:12px;min-width:110px}.toolbar>input{align-self:end}.toolbar .btn{align-self:end}.alert{padding:12px 16px;background:#faf4e7;color:#8e7647;border-radius:6px;font-size:12px;margin-bottom:18px}.numbers a{color:#c6d3bf}.toplinks{display:flex;gap:12px;align-items:center}.linkline{margin:20px 0;font-size:12px}h2{font-size:18px}.hidden{display:none!important}@media(max-width:700px){.hero{grid-template-columns:1fr}.hero h1{font-size:28px}.toplinks{gap:8px;font-size:11px}.toolbar label{flex:1}.toolbar label select{max-width:none;width:100%}.toolbar .btn{flex:1}.tablewrap{max-height:650px}} </style></head><body>
<header><div class="brand">OpenRaise<span>PUBLIC RESEARCH OBSERVATORY</span></div><nav class="toplinks"><a href="./">技术来源板</a><a class="btn" href="https://github.com/42Channel/doris">GitHub ↗</a></nav></header>
<main class="wrap"><section class="hero"><div><span class="overline">MODELS · AI INFRA · PHYSICAL AI</span><h1>2021 年以来，<br><em>Seed–D 公司研究库。</em></h1><p>不限成立年份。按窗口内历史融资事件筛选，保留可回溯的公告、金额口径与未决问题。研究 → 联系 → 核验 → 手动入池。</p></div><div class="hero-right"><strong id="total"></strong><small>家研究候选公司</small><div class="numbers"><div><b id="eventTotal"></b><span>已收录历史事件</span></div><div><b>2021–2026</b><span>公告时间范围</span></div></div></div></section>
<div class="summary"><span id="freshness"></span><span>公开研究 · 无需登录 · 未自动入池</span></div><div class="chips" id="chips"></div>
<div class="alert">这是公开来源持续扩充版，尚未覆盖全球全部公司或每家公司的完整融资史。历史符合 Seed–D 不代表当前轮次、可投资状态或资金已逐笔交割。</div>
<div class="tabs"><button id="verifiedTab" class="active">历史符合事件</button><button id="pendingTab">待核验线索</button></div>
<div class="toolbar"><input id="q" aria-label="搜索公司、技术、投资方或备注" placeholder="搜索公司、技术、投资方或备注…"><label>研究主线<select id="direction"><option value="">全部主线</option><option>模型与核心技术</option><option>AI Infra</option><option>Physical AI</option></select></label><label class="eventfilter">历史轮次<select id="round"><option value="">Seed–D 全部</option><option>Seed</option><option>A</option><option>B</option><option>C</option><option>D</option></select></label><label class="eventfilter">公告年份<select id="year"><option value="">全部年份</option></select></label><label class="eventfilter">核验层<select id="layer"><option value="">全部证据层</option><option value="本次">本次一手来源核验</option><option value="既有">既有一手快照</option></select></label><button id="reset" class="btn">重置</button><button id="download" class="btn">导出当前结果 CSV ↓</button></div>
<div class="panel"><div class="tablewrap"><table><thead id="thead"></thead><tbody id="tbody"></tbody></table></div><div class="paging"><span id="count" aria-live="polite"></span><div><button id="prev">上一页</button><button id="next">下一页</button></div></div></div>
<p class="linkline"><a href="funding.csv" download>完整融资明细 CSV ↓</a>　<a href="funding-data.json" download>结构化 JSON ↓</a>　<a href="https://github.com/42Channel/doris/blob/main/FUNDING.md">GitHub 完整清单 ↗</a></p>
<section class="method"><h3>读表口径</h3><p id="methodology"></p><p>同轮扩展后总额、多轮合计、约数、披露下界分别标注；不跨币种求和。日期精度为年或月时保持原精度，不补造日期。当前状态仅对另附公开证据的项目作说明，其余保留待核验。</p><p>沿用的既有快照保留原证据层和截止日期；不是本次重新核验的结论。待核验页包含未披露轮次和仅有二级来源的线索；不计入主表的公司与事件统计。公开收录不代表已触达或进入 OpenRaise 正式池。</p><p>更新方式：修改 funding-data.json 后运行 python scripts/build-funding.py，重新生成展示与导出文件并提交 GitHub。当前未启用定时抓取。已有四份 Top100 来源清单保持原结构。</p></section><footer><span>OpenRaise · 42Channel / doris</span><span id="footerDate"></span></footer></main>
<script type="application/json" id="dataset">'''+json.dumps(d,ensure_ascii=False).replace('</','<\/')+r'''</script><script>
const D=JSON.parse(document.getElementById('dataset').textContent),$=id=>document.getElementById(id);let mode='verified',page=1,current=[];const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const link=(u,t)=>/^https:\/\//.test(u)?'<a href="'+esc(u)+'" target="_blank" rel="noopener noreferrer">'+esc(t)+' ↗</a>':esc(t);const amount=e=>e.amount==null?'未拆分／未披露':e.currency+' '+(e.amount/1e6).toLocaleString('en-US',{maximumFractionDigits:3})+'M';
$('total').textContent=D.companies.length;$('eventTotal').textContent=D.companies.reduce((n,c)=>n+c.events.length,0);$('freshness').textContent='本次检索 '+D.asOf+' · 既有快照 2026-11-08';$('footerDate').textContent='研究截止 '+D.asOf;$('methodology').textContent=D.methodology;$('chips').innerHTML=['模型与核心技术','AI Infra','Physical AI'].map(s=>'<span>'+s+' · '+D.companies.filter(c=>c.direction===s).length+' 家</span>').join('');for(let y=2026;y>=2021;y--){const o=document.createElement('option');o.value=String(y);o.textContent=String(y);$('year').appendChild(o)}
function render(){const q=$('q').value.trim().toLowerCase(),di=$('direction').value,ro=$('round').value,ye=$('year').value,la=$('layer').value;
document.querySelectorAll('.eventfilter').forEach(e=>e.classList.toggle('hidden',mode==='pending'));
if(mode==='verified'){current=D.companies.filter(c=>(!di||c.direction===di)&&(!la||c.evidenceStatus.startsWith(la))&&(!q||JSON.stringify(c).toLowerCase().includes(q))).map(c=>({...c,shown:c.events.filter(e=>(!ro||e.roundGroup===ro)&&(!ye||e.date.startsWith(ye)))})).filter(c=>c.shown.length);$('thead').innerHTML='<tr><th>公司／技术方向</th><th>研究主线／核验层</th><th>历史符合事件 · 原币金额</th><th>当前状态</th><th>证据口径与未决项</th></tr>';}else{current=D.pending.filter(c=>(!di||c.direction===di)&&(!q||JSON.stringify(c).toLowerCase().includes(q)));$('thead').innerHTML='<tr><th>公司／事件线索</th><th>研究主线</th><th>待核验原因</th><th>公开线索</th><th>备注</th></tr>';}
const pages=Math.max(1,Math.ceil(current.length/20));page=Math.min(page,pages);$('tbody').innerHTML=current.slice((page-1)*20,page*20).map(c=>mode==='verified'?'<tr><td><b>'+esc(c.name)+'</b><small>'+esc(c.id)+' · '+esc(c.technology)+'</small></td><td><span class="tag">'+esc(c.direction)+'</span><small>'+esc(c.evidenceStatus)+'</small></td><td>'+c.shown.map(e=>'<div class="event">'+link(e.sourceUrl,e.round+' · '+e.date)+'<span class="amount">'+esc(amount(e))+' · '+esc(e.amountBasis)+'</span></div>').join('')+'</td><td class="status">'+esc(c.status)+(c.statusSource?'<small>'+link(c.statusSource,'状态证据')+'</small>':'')+'<small>研究候选；尚未手动入池</small></td><td class="notes"><details><summary>查看 '+c.shown.length+' 条事件口径</summary>'+c.shown.map(e=>'<p><b>'+esc(e.round+' · '+e.date)+'</b><br>'+esc(e.notes||'按公开公告披露；非最新融资轮次断言')+'<br>'+esc(e.investors?'公告所列投资方：'+e.investors:'投资方名单未在本表补齐')+'<br>'+esc(e.evidenceLevel)+'<br>日期精度：'+esc(e.datePrecision)+'；核验截止 '+esc(e.checkedAt)+'</p>').join('')+'</details></td></tr>':'<tr><td><b>'+esc(c.name)+'</b></td><td>'+esc(c.direction)+'</td><td>'+esc(c.reason)+'</td><td>'+link(c.sourceUrl,'来源／核验入口')+'</td><td class="notes">'+esc(c.notes||'尚未计入已确认事件数')+'</td></tr>').join('')||'<tr><td colspan="5" class="empty">暂无符合条件的记录，请调整筛选。</td></tr>';
$('count').textContent=mode==='verified'?current.length+' 家公司 · '+current.reduce((n,c)=>n+c.shown.length,0)+' 条匹配事件 · '+page+'/'+pages+' 页':current.length+' 条待核验线索 · '+page+'/'+pages+' 页';$('prev').disabled=page<=1;$('next').disabled=page>=pages;}
for(const id of ['q','direction','round','year','layer'])$(id).addEventListener('input',()=>{page=1;render()});for(const [id,m] of [['verifiedTab','verified'],['pendingTab','pending']])$(id).onclick=()=>{mode=m;page=1;$('verifiedTab').classList.toggle('active',mode==='verified');$('pendingTab').classList.toggle('active',mode==='pending');render()};$('prev').onclick=()=>{page--;render()};$('next').onclick=()=>{page++;render()};$('reset').onclick=()=>{for(const id of ['q','direction','round','year','layer'])$(id).value='';page=1;render()};$('download').onclick=()=>{let rows=mode==='verified'?[['公司','主线','技术','历史轮次','公告日期','日期精度','金额原币','币种','金额口径','投资方（非完整）','当前状态','核验层','证据','核验截止','备注'],...current.flatMap(c=>c.shown.map(e=>[c.name,c.direction,c.technology,e.round,e.date,e.datePrecision,e.amount??'',e.currency,e.amountBasis,e.investors,c.status,c.evidenceStatus,e.sourceUrl,e.checkedAt,e.notes]))]:[['公司','主线','待核验原因','线索','备注'],...current.map(c=>[c.name,c.direction,c.reason,c.sourceUrl,c.notes])];const csv='\uFEFF'+rows.map(r=>r.map(v=>'"'+String(v??'').replace(/^[=+@-]/,"'$&").replaceAll('"','""')+'"').join(',')).join('\r\n');const u=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=u;a.download='OpenRaise_Seed_D_'+D.asOf+'_'+mode+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),2000)};render();
</script></body></html>'''
(R/'funding.html').write_text(page)
nav='<a class="btn" href="funding.html">2021+ Seed–D 公司库 ↗</a>'
if nav not in old:old=old.replace('<a class="btn" href="https://github.com/42Channel/doris">',nav+'<a class="btn" href="https://github.com/42Channel/doris">',1)
(R/'index.html').write_text(old)
readme=(R/'README.md').read_text()
start='<!-- FUNDING-SUMMARY -->';end='<!-- /FUNDING-SUMMARY -->'
summary=f'''{start}
## 2021 年以来 Seed–D 公司研究库

**{n} 家公司 · {ne} 条历史融资事件**。以 2021-01-01 至 {d['asOf']} 的公开 Seed–D 事件为筛选依据，不限成立年份。

[打开融资筛选板](https://42channel.github.io/doris/funding.html) · [查看完整清单](FUNDING.md) · [下载 CSV](funding.csv) · [JSON](funding-data.json)

这是持续扩充的公开研究覆盖，**并非全球全量或每家公司完整融资史**；区分本次一手来源核验与既有快照。历史轮次与当前状态分开，待核验事件单列。原有 Top100 来源清单保持原结构。
{end}
'''
if start in readme:readme=re.sub(re.escape(start)+'.*?'+re.escape(end),summary,readme,flags=re.S)
else:readme=readme.replace('## 目录',summary+'\n## 目录',1)
(R/'README.md').write_text(readme)
print('Rendered funding.html, FUNDING.md, CSV/JSON; linked existing board.')

import csv
with (R/'funding.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['ID','公司','主线','技术','历史符合轮次','轮次组','公告日期','日期精度','金额原币','币种','金额口径','公告所列投资方（非完整）','核验层','当前状态','证据','核验截止','备注'])
 for c in cs:
  for e in c['events']:w.writerow([c['id'],c['name'],c['direction'],c['technology'],e['round'],e['roundGroup'],e['date'],e['datePrecision'],e['amount'] if e['amount'] is not None else '',e['currency'],e['amountBasis'],e['investors'],c['evidenceStatus'],c['status'],e['sourceUrl'],e['checkedAt'],e['notes']])
