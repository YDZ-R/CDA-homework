"""Generate an offline Pyecharts dashboard with shared date and district filters."""
import json
import shutil
from pyecharts.charts import Line, Bar, Scatter
from pyecharts import options as opts
from common import ROOT, COLORS, city_data, district_data, TABLES

out=ROOT/'outputs/dashboard'; assets=out/'assets';assets.mkdir(exist_ok=True)
asset=assets/'echarts.min.js'
if not asset.exists():
    candidate=ROOT.parent/'_work/echarts.min.js'
    if not candidate.exists():raise FileNotFoundError('缺少已归档的ECharts离线资源 outputs/dashboard/assets/echarts.min.js')
    shutil.copy2(candidate,asset)

def base(chart):
    chart.set_global_opts(legend_opts=opts.LegendOpts(pos_top='0%'),
        tooltip_opts=opts.TooltipOpts(trigger='axis'),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color='#526E79')),
        yaxis_opts=opts.AxisOpts(name='入住率（%）',axislabel_opts=opts.LabelOpts(color='#526E79')))
    return json.loads(chart.dump_options())

line=Line().add_xaxis([]).add_yaxis('日度入住率',[],is_symbol_show=False,color=COLORS[0])
bar=Bar().add_xaxis([]).add_yaxis('日均入住率',[],color=COLORS[0])
scatter=Scatter().add_xaxis([]).add_yaxis('区县',[],symbol_size=14)
options={'trend':base(line),'ranking':base(bar),'monthly':base(bar),'weekday':base(bar),
         'scatter':base(scatter),'forecast':base(line)}
city=city_data().reset_index();district=district_data()
records=lambda d:[[str(r.date.date()),r.area,round(float(r.occupancy),3)] for r in d.itertuples()]
import pandas as pd
clusters=pd.read_csv(TABLES/'district_features.csv').set_index('area')['cluster'].to_dict()
future=pd.read_csv(TABLES/'forecast_2026_january.csv').round(3).to_dict('records')
summary=json.loads((TABLES/'analysis_summary.json').read_text(encoding='utf-8'))
payload=dict(city=records(city),district=records(district),clusters=clusters,future=future,summary=summary)
html=r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>杭州酒店入住率分析看板</title><script src="assets/echarts.min.js"></script>
<style>
:root{--ink:#253f4b;--muted:#526e79;--teal:#287d8e;--mint:#79b9bb;--coral:#f1b09a;--line:#dce6e9;--bg:#f5f8f8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 "Microsoft YaHei","Noto Sans SC",sans-serif;font-variant-numeric:tabular-nums}
::selection{background:#c4e6e4;color:#173f48}a{color:var(--teal);text-underline-offset:3px}input{accent-color:var(--teal);caret-color:var(--teal)}
main{max-width:1520px;margin:0 auto;padding:32px 34px 28px}header{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-bottom:22px}
h1{font-size:30px;line-height:1.3;letter-spacing:.01em;margin:0 0 8px;font-weight:700}p{margin:0;color:var(--muted)}.source{text-align:right;font-size:12px;max-width:450px}
.filters{display:flex;flex-wrap:wrap;align-items:flex-end;gap:16px;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:var(--muted)}input,select,button{font:inherit;color:var(--ink);background:white;border:1px solid #b3c8cf;border-radius:6px;padding:8px 11px;min-height:40px}
button{cursor:pointer}button:hover{background:#e5f1f1;border-color:var(--teal)}button:disabled{cursor:default;opacity:.5}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #79b9bb;outline-offset:2px}
.preset{display:flex;gap:7px;flex-wrap:wrap}.primary{background:var(--teal);color:white;border-color:var(--teal)}.primary:hover{background:#226c7b;color:white}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;padding:22px 0}.kpi{padding:3px 22px 4px 0;border-right:1px solid var(--line)}.kpi:last-child{border:0}.kpi strong{display:block;font-size:30px;font-weight:650;line-height:1.35}.kpi span{font-size:12px;color:var(--muted)}.kpi label{font-size:13px;margin-bottom:4px}
.grid{display:grid;grid-template-columns:1.5fr 1fr;gap:20px}.panel{background:white;border:1px solid var(--line);padding:20px 18px 8px;min-width:0;border-radius:12px}.panel h2{font-size:17px;margin:0 0 3px}.panel p{font-size:12px;min-height:23px}.chart{height:290px;width:100%;margin-top:10px}.short{height:260px}.wide{grid-column:1/-1}.table-wrap{overflow:auto;max-height:340px;margin-top:12px}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:9px 13px;border-bottom:1px solid var(--line);white-space:nowrap}th{background:#edf4f4;position:sticky;top:0;color:var(--ink)}td:nth-child(3){text-align:right}tbody tr:hover{background:#f2f8f8}
.table-head{display:flex;justify-content:space-between;align-items:center;gap:20px}.notice{padding:13px 0;font-size:12px;color:var(--muted)}.empty{display:none;background:#fff3ec;color:#714a35;padding:14px;margin-top:12px;border-radius:6px}footer{margin-top:20px;padding-top:15px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}
@media(max-width:850px){main{padding:20px 16px}header{display:block}.source{text-align:left;margin-top:10px}.grid{grid-template-columns:1fr}.wide{grid-column:auto}.kpis{grid-template-columns:repeat(2,1fr);gap:16px}.kpi:nth-child(2){border:0}h1{font-size:25px}.filters{gap:10px}.chart{height:290px}.panel{padding:16px 12px 6px}.preset{width:100%}}
</style></head><body><main>
<header><div><h1>杭州酒店入住率分析看板</h1></div><div class="source">2023-11-01 至 2025-12-31</div></header>
<section class="filters" aria-label="数据筛选">
<label>开始日期<input id="start" type="date" min="2023-11-01" max="2025-12-31" value="2024-01-01"></label>
<label>结束日期<input id="end" type="date" min="2023-11-01" max="2025-12-31" value="2025-12-31"></label>
<label>分析范围<select id="area"><option value="杭州">全市官方口径</option></select></label>
<div class="preset"><button data-year="2024">2024年</button><button data-year="2025">2025年</button><button id="reset">全部样本</button><button id="apply" class="primary">更新分析</button></div>
</section><div id="error" class="empty" role="status"></div>
<section class="kpis" aria-label="关键指标"><div class="kpi"><label>选定范围日均入住率</label><strong id="mean">—</strong><span>实际观测日的算术平均</span></div><div class="kpi"><label>日度波动</label><strong id="std">—</strong><span>标准差，单位为百分点</span></div><div class="kpi"><label>有效观测天数</label><strong id="count">—</strong><span id="missing">—</span></div><div class="kpi"><label>区间最高入住率</label><strong id="peak">—</strong><span id="peakDate">—</span></div></section>
<div class="grid">
<section class="panel"><h2>日度入住率与移动平均</h2><div id="trend" class="chart"></div></section>
<section class="panel"><h2>区县平均入住率</h2><div id="ranking" class="chart"></div></section>
<section class="panel"><h2>月度入住水平</h2><div id="monthly" class="chart short"></div></section>
<section class="panel"><h2>周内入住节奏</h2><div id="weekday" class="chart short"></div></section>
<section class="panel"><h2>区县水平与波动</h2><div id="scatter" class="chart short"></div></section>
<section class="panel"><h2>未来28日预测</h2><p>预测原点：2025-12-31</p><div id="forecast" class="chart short"></div></section>
<section class="panel wide"><div class="table-head"><div><h2>观测明细</h2><p id="tableNote">显示筛选结果中最近45条观测，可导出全部筛选结果。</p></div><button id="csv">导出筛选数据 CSV</button></div><div class="table-wrap"><table><thead><tr><th>日期</th><th>范围</th><th>入住率（%）</th><th>指标口径</th></tr></thead><tbody id="rows"></tbody></table></div></section>
</div><footer>曹俊男 · 大数据241</footer>
</main><script>
const DATA=__DATA__,OPTIONS=__OPTIONS__,C=['#287d8e','#79b9bb','#f1b09a','#8ca9ce'];
const $=id=>document.getElementById(id),areas=[...new Set(DATA.district.map(r=>r[1]))].sort();
areas.forEach(a=>{let o=document.createElement('option');o.value=a;o.textContent=a;$('area').appendChild(o)});
const charts={};Object.keys(OPTIONS).forEach(id=>{charts[id]=echarts.init($(id));charts[id].setOption(OPTIONS[id]);});
const avg=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:null;
const sd=a=>a.length>1?Math.sqrt(a.reduce((s,x)=>s+(x-avg(a))**2,0)/(a.length-1)):null;
const group=(rows,key)=>{let o={};rows.forEach(r=>{let k=key(r);(o[k]??=[]).push(r[2])});return Object.entries(o).map(([k,v])=>[k,avg(v),sd(v),v.length])};
const chartBase={animationDuration:450,color:C,textStyle:{fontFamily:'Microsoft YaHei, sans-serif',color:'#253f4b'},grid:{left:50,right:22,top:38,bottom:48,containLabel:true},tooltip:{trigger:'axis'},legend:{show:false},xAxis:{type:'category',axisLine:{lineStyle:{color:'#b9ccd2'}},axisLabel:{color:'#526e79'}},yAxis:{type:'value',name:'入住率（%）',splitLine:{lineStyle:{color:'#e8eff1'}},axisLabel:{color:'#526e79'}}};
let selected=[];
function draw(){
 const start=$('start').value,end=$('end').value,area=$('area').value;
 const filter=r=>r[0]>=start&&r[0]<=end;
 let rows=(area==='杭州'?DATA.city:DATA.district.filter(r=>r[1]===area)).filter(filter);
 selected=rows; $('error').style.display='none';
 if(!start||!end||start>end||!rows.length){
  selected=[];
  ['mean','std','peak','missing','peakDate'].forEach(id=>$(id).textContent='—');
  $('count').textContent='0';$('csv').disabled=true;
  ['trend','ranking','monthly','weekday','scatter'].forEach(id=>charts[id].clear());
  $('rows').replaceChildren();$('tableNote').textContent='共0条真实观测。';
  $('error').textContent='该日期范围没有有效观测，请调整起止日期。';$('error').style.display='block';return;
 }
 $('csv').disabled=false;
 let values=rows.map(r=>r[2]),mean=avg(values),peak=Math.max(...values),days=Math.round((new Date(end)-new Date(start))/864e5)+1;
 $('mean').textContent=mean.toFixed(1)+'%';$('std').textContent=values.length>1?sd(values).toFixed(1)+' pp':'—';$('count').textContent=rows.length;
 $('missing').textContent='所选'+days+'天，缺'+Math.max(0,days-rows.length)+'天';$('peak').textContent=peak.toFixed(1)+'%';$('peakDate').textContent=rows.find(r=>r[2]===peak)[0];
 let base=(area==='杭州'?DATA.city:DATA.district.filter(r=>r[1]===area));
 let ma=rows.map(r=>avg(base.filter(z=>z[0]<=r[0]&&(new Date(r[0])-new Date(z[0]))/864e5<28).map(z=>z[2])));
 charts.trend.setOption({...chartBase,legend:{show:true,top:0},dataZoom:[{type:'inside'},{type:'slider',height:14,bottom:4}],xAxis:{...chartBase.xAxis,data:rows.map(r=>r[0])},series:[{type:'line',name:'日度入住率',data:values,showSymbol:false,lineStyle:{width:1.4,color:C[1]},itemStyle:{color:C[1]}},{type:'line',name:'28日移动平均',data:ma.map(x=>+x.toFixed(2)),showSymbol:false,lineStyle:{width:2.4,color:C[0]},itemStyle:{color:C[0]}}]},true);
 let ranks=group(DATA.district.filter(filter),r=>r[1]).sort((a,b)=>a[1]-b[1]);
 charts.ranking.setOption({...chartBase,grid:{left:12,right:38,top:16,bottom:26,containLabel:true},xAxis:{type:'value',max:100,name:'%'},yAxis:{type:'category',data:ranks.map(r=>r[0]),axisLabel:{color:'#526e79'},axisTick:{show:false},axisLine:{show:false}},series:[{type:'bar',barMaxWidth:14,data:ranks.map(r=>({value:+r[1].toFixed(2),itemStyle:{color:r[0]===area?C[2]:C[0]}})),label:{show:true,position:'right',formatter:p=>p.value.toFixed(1)}}]},true);
 let months=group(rows,r=>r[0].slice(0,7));
 charts.monthly.setOption({...chartBase,xAxis:{...chartBase.xAxis,data:months.map(r=>r[0]),axisLabel:{rotate:35,color:'#526e79'}},series:[{type:'bar',name:'月均入住率',data:months.map(r=>+r[1].toFixed(2)),itemStyle:{color:C[0]},barMaxWidth:28}]},true);
 let weekdays=group(rows,r=>(new Date(r[0]+'T00:00:00Z').getUTCDay()+6)%7).sort((a,b)=>a[0]-b[0]);
 charts.weekday.setOption({...chartBase,xAxis:{...chartBase.xAxis,data:weekdays.map(r=>['周一','周二','周三','周四','周五','周六','周日'][r[0]])},series:[{type:'bar',data:weekdays.map(r=>+r[1].toFixed(2)),itemStyle:{color:C[1]},barMaxWidth:35,label:{show:true,position:'top',formatter:p=>p.value.toFixed(1)}}]},true);
 let narrow=$('scatter').clientWidth<440;
 let scatter=ranks.filter(r=>r[3]>1).map(r=>({name:r[0],value:[+r[1].toFixed(2),+r[2].toFixed(2)],itemStyle:{color:C[(DATA.clusters[r[0]]-1)%4]},symbolSize:r[0]===area?22:14,label:{show:!narrow||r[0]===area}}));
 charts.scatter.setOption({...chartBase,grid:{left:42,right:28,top:38,bottom:68,containLabel:true},tooltip:{trigger:'item',formatter:p=>p.name+'<br>日均 '+p.value[0]+'%<br>波动 '+p.value[1]+' pp'},xAxis:{type:'value',name:'日均入住率（%）',nameLocation:'middle',nameGap:30,scale:true,splitLine:{lineStyle:{color:'#e8eff1'}}},yAxis:{...chartBase.yAxis,name:'标准差（pp）',scale:true},series:[{type:'scatter',data:scatter,label:{show:true,formatter:'{b}',position:'top',fontSize:10},labelLayout:{hideOverlap:true,moveOverlap:'shiftY'}}]},true);
 $('rows').innerHTML=rows.slice(-45).reverse().map(r=>'<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td>'+r[2].toFixed(1)+'</td><td>所有档次酒店 日度汇总</td></tr>').join('');
 $('tableNote').textContent='共'+rows.length+'条真实观测，显示最近'+Math.min(rows.length,45)+'条。';
}
const f=DATA.future;
charts.forecast.setOption({...chartBase,grid:{left:42,right:20,top:64,bottom:48,containLabel:true},legend:{show:true,top:0,data:['95%预测区间','点预测']},xAxis:{...chartBase.xAxis,data:f.map(r=>r.date)},series:[{type:'line',name:'下界',data:f.map(r=>r.lower),stack:'ci',symbol:'none',lineStyle:{opacity:0},areaStyle:{opacity:0},tooltip:{show:false}},{type:'line',name:'95%预测区间',data:f.map(r=>+(r.upper-r.lower).toFixed(3)),stack:'ci',symbol:'none',lineStyle:{opacity:0},areaStyle:{color:C[1],opacity:.35},tooltip:{show:false}},{type:'line',name:'点预测',data:f.map(r=>r.prediction),showSymbol:false,lineStyle:{color:C[0],width:2},itemStyle:{color:C[0]}}]},true);
$('apply').onclick=draw;['start','end','area'].forEach(id=>$(id).onchange=draw);
document.querySelectorAll('[data-year]').forEach(b=>b.onclick=()=>{$('start').value=b.dataset.year+'-01-01';$('end').value=b.dataset.year+'-12-31';draw()});
$('reset').onclick=()=>{$('start').value='2023-11-01';$('end').value='2025-12-31';$('area').value='杭州';draw()};
charts.ranking.on('click',p=>{$('area').value=p.name;draw()});charts.scatter.on('click',p=>{$('area').value=p.name;draw()});
$('csv').onclick=()=>{if(!selected.length)return;const csv='\ufeff日期,区域,入住率（%）\n'+selected.map(r=>[r[0],r[1],r[2]].join(',')).join('\n');let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.download='杭州入住率_筛选结果.csv';a.click();URL.revokeObjectURL(a.href)};
window.addEventListener('resize',()=>{Object.values(charts).forEach(c=>c.resize());draw()});draw();
</script></body></html>'''
html=html.replace('__DATA__',json.dumps(payload,ensure_ascii=False,separators=(',',':'))).replace('__OPTIONS__',json.dumps(options,ensure_ascii=False))
(out/'index.html').write_text(html,encoding='utf-8')
print('Pyecharts离线联动大屏已生成。')
