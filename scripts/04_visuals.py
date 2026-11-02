"""Ten textbook-format recreations, six separate model figures and a workflow."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Wedge, Circle, FancyBboxPatch, FancyArrowPatch
from matplotlib.colors import LinearSegmentedColormap
from common import FIGURES, TABLES, COLORS, BG, INK, MUTED, city_data, district_data

plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','SimHei','DejaVu Sans'],
                     'axes.unicode_minus':False,'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
city,district=city_data(),district_data()
monthly=pd.read_csv(TABLES/'monthly_comparison.csv',index_col=0,parse_dates=True)
dy=pd.read_csv(TABLES/'district_year.csv',index_col=0)
features=pd.read_csv(TABLES/'district_features.csv',index_col=0)
summary=json.loads((TABLES/'analysis_summary.json').read_text(encoding='utf-8'))
index=[]
DARK='#1A1E43'; BLUE='#0070C0'; SKY='#82ADD7'; WHITE='#F2F5FA'

def canvas(title, subtitle='',dark=False,figsize=(8,3.6)):
    bg,ink=(DARK,WHITE) if dark else ('#FFFFFF',INK)
    fig,ax=plt.subplots(figsize=figsize,facecolor=bg)
    ax.set_facecolor(bg)
    fig.subplots_adjust(left=.12,right=.95,top=.85,bottom=.17)
    ax.set_title(title,fontsize=14,pad=10,color=ink)
    ax.tick_params(colors=ink,labelsize=11)
    ax.xaxis.label.set_fontsize(12);ax.yaxis.label.set_fontsize(12)
    for sp in ax.spines.values():sp.set_color('#646A89' if dark else '#CDDBDF')
    ax.yaxis.label.set_color(ink);ax.xaxis.label.set_color(ink)
    return fig,ax

def save(fig,num,name,kind,template='',note=''):
    path=FIGURES/f'fig{num:02d}_{name}.png'
    fig.savefig(path,dpi=220,facecolor=fig.get_facecolor())
    fig.savefig(path.with_suffix('.svg'),facecolor=fig.get_facecolor())
    plt.close(fig)
    index.append(dict(number=f'fig{num:02d}',name=name,category=kind,template=template,file=path.name))

def legend(ax,dark=False,**kwargs):
    leg=ax.legend(frameon=False,**kwargs)
    if leg:
        for text in leg.get_texts():text.set_color(WHITE if dark else INK)

from template_charts import draw_templates
draw_templates(city,monthly,dy,summary,save)
a=monthly[monthly.index.year==2024]['occupancy'].values
b=monthly[monthly.index.year==2025]['occupancy'].values
x=np.arange(12)

fig,ax=canvas('2025年月均入住率同比变化')
delta=b-a;ax.bar(x,delta,color=[COLORS[0] if v>=0 else COLORS[2] for v in delta],width=.58)
ax.axhline(0,color=MUTED,lw=.8)
for i,v in enumerate(delta):ax.text(i,v+(.3 if v>=0 else -.3),f'{v:+.1f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=11)
ax.set(xticks=x,xticklabels=[f'{i}月' for i in range(1,13)],ylabel='同比变化（百分点）')
save(fig,11,'月度同比差异','业务模型','趋势与对比')

fig,ax=canvas('周内酒店入住率')
w=city.groupby('weekday')['occupancy'].agg(['mean','std'])
ax.errorbar(range(7),w['mean'],yerr=w['std'],fmt='o-',capsize=5,color=COLORS[0],ecolor=COLORS[1],lw=2,markersize=7)
for i,v in enumerate(w['mean']):ax.text(i,v+2,f'{v:.1f}',ha='center',color=INK)
ax.set(xticks=range(7),xticklabels=['周一','周二','周三','周四','周五','周六','周日'],ylabel='入住率（%）',ylim=(20,90))
ax.grid(axis='y',color='#E2EAED',lw=.6)
save(fig,12,'周内入住率特征','业务模型','趋势与对比')

fig,ax=canvas('区县入住水平与波动',figsize=(8,4.16))
offsets={'临平区':(-37,-18),'余杭区':(-40,10),'钱塘区':(10,-4),'萧山区':(8,10),'上城区':(6,-13),'拱墅区':(7,-2)}
for cluster,g in features.groupby('cluster'):
    ax.scatter(g['mean'],g['volatility'],s=95,color=COLORS[int(cluster)-1],label=f'第{cluster}组',edgecolor='white',lw=1,zorder=3)
    for j,(area,row) in enumerate(g.iterrows()):
        ax.annotate(area,(row['mean'],row['volatility']),xytext=offsets.get(area,(5,5)),textcoords='offset points',fontsize=10)
ax.set(xlabel='日均入住率（%）',ylabel='日度标准差（百分点）');ax.margins(.23)
legend(ax,loc='upper right');ax.grid(color='#E2EAED',lw=.6)
save(fig,13,'区县聚类散点图','业务模型','K-Means')

fcols=['mean','volatility','weekend_gap','seasonal_range']; f=features.sort_values(['cluster','mean'],ascending=[True,False])
z=(f[fcols]-features[fcols].mean())/features[fcols].std(ddof=0)
fig,ax=canvas('区县聚类特征',figsize=(8,4.64))
fig.subplots_adjust(left=.17,bottom=.15)
cm=LinearSegmentedColormap.from_list('mint_coral',[COLORS[0],'#F8FAFB',COLORS[2]])
im=ax.imshow(z,aspect='auto',cmap=cm,vmin=-2,vmax=2)
ax.set_xticks(range(4),labels=['入住水平','日度波动','周末差','季节幅度'])
ax.set_yticks(range(len(f)),labels=[f'{a}  第{int(f.loc[a,"cluster"])}组' for a in f.index])
for i in range(len(f)):
    for j in range(4):ax.text(j,i,f'{z.iloc[i,j]:+.2f}',ha='center',va='center',color=INK,fontsize=10)
fig.colorbar(im,ax=ax,fraction=.025,pad=.025,label='标准分数')
save(fig,14,'聚类特征热力图','业务模型','K-Means')

bt=pd.read_csv(TABLES/'forecast_backtest.csv',parse_dates=['date'])
fig,ax=canvas('入住率滚动回测',figsize=(8.8,3.6))
ax.plot(bt.date,bt.actual,color=INK,lw=1.5,label='实际值')
ax.plot(bt.date,bt.prediction,color=COLORS[0],lw=1.7,label='SARIMA')
ax.plot(bt.date,bt.weekly_naive,color=COLORS[2],lw=1,alpha=.8,label='周季节朴素法')
ax.fill_between(bt.date,bt.lower,bt.upper,color=COLORS[1],alpha=.24,label='95%预测区间')
for fold,g in bt.groupby('fold'):
    ax.axvline(g.date.iloc[0],color=MUTED,ls=':',lw=.8)
ax.set(ylabel='入住率（%）');legend(ax,loc='upper left',ncol=4,fontsize=9)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2));ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
save(fig,15,'滚动回测与误差','业务模型','SARIMA')

future=pd.read_csv(TABLES/'forecast_2026_january.csv',parse_dates=['date'])
fig,ax=canvas('未来28日酒店入住率预测',figsize=(8.8,3.6))
hist=city.loc['2025-10-01':,'occupancy'];ax.plot(hist.index,hist,color=INK,lw=1.3,label='历史真实观测')
ax.plot(future.date,future.prediction,color=COLORS[0],lw=2,label='点预测')
ax.fill_between(future.date,future.lower,future.upper,color=COLORS[1],alpha=.4,label='95%预测区间')
ax.axvline(pd.Timestamp('2025-12-31'),color=MUTED,ls='--',lw=1)
ax.set(ylabel='入住率（%）');legend(ax,loc='upper left',ncol=3,fontsize=9)
ax.xaxis.set_major_locator(mdates.MonthLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
save(fig,16,'未来28日预测区间','业务模型','SARIMA')

fig=plt.figure(figsize=(10,6.2),facecolor='white')
ax=fig.add_axes([0,0,1,1],xlim=(0,100),ylim=(0,62));ax.set_axis_off()
ax.add_patch(FancyBboxPatch((.7,.7),98.6,60.6,boxstyle='round,pad=0,rounding_size=1.2',
                            facecolor='#FAFBFD',edgecolor='#CED6DF',lw=.8))
blue=('#328BD0','#EDF5FD');pink=('#D9568C','#FDEEF4')
green=('#359D71','#EEF8F1');purple=('#9360C4','#F5EFFB');orange=('#D89040','#FFF7E9')

def group_box(x,y,w,h,title,palette):
    color,fill=palette
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=.9',
                 facecolor=fill,edgecolor=color,lw=1,linestyle=(0,(5,3))))
    dark={'#328BD0':'#236A9C','#D9568C':'#AA3668','#359D71':'#24704F','#9360C4':'#6D4095','#D89040':'#9A5D24'}
    ax.text(x+1.4,y+h-2.0,title,color=dark[color],fontsize=13,weight='bold',style='italic',va='center')

def node(x,y,w,h,label,color,fill='white',size=12.5):
    assert 0<x<x+w<100 and 0<y<y+h<62
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=.45',
                 facecolor=fill,edgecolor=color,lw=.85))
    dark={'#328BD0':'#236A9C','#D9568C':'#AA3668','#359D71':'#24704F','#9360C4':'#6D4095','#D89040':'#9A5D24'}
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=size,color=dark[color])

def arrow(start,end):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=11,
                               lw=1.05,color='#687A87',shrinkA=2,shrinkB=2))

group_box(2.2,49,95.6,10.8,'阶段一  数据治理',blue)
top=[(5,18,'日期统一'),(27.5,23,'缺日标记与异常检查'),(55,17,'特征构建'),(76.5,18.3,'分析数据表')]
for x,w,label in top:node(x,51.2,w,3.9,label,blue[0])
for (x,w,_),(nx,_,_) in zip(top,top[1:]):arrow((x+w,53.15),(nx,53.15))

columns=[(2.2,pink,'阶段二  时间变化',['月度同比与环比','星期均值对比','月度与周内需求节奏']),
         (34.8,green,'阶段三  区县分群',['区县四维特征','标准化与K-Means','轮廓系数及敏感性','区县需求画像']),
         (67.4,purple,'阶段四  入住率预测',['训练与验证划分','SARIMA与季节朴素法','三轮28日滚动回测','点预测及95%区间'])]
for x,palette,title,labels in columns:
    group_box(x,18.9,30.4,26.5,title,palette)
    center=x+15.2
    arrow((center,49),(center,45.5))
    # All three models use the cleaned observations; clustering is not a predictor input.
    ys=[37.6,29.1,20.6] if len(labels)==3 else [37.6,31.8,26.0,20.2]
    for j,(y,label) in enumerate(zip(ys,labels)):
        node(x+2.0,y,26.4,4.1,label,palette[0],palette[1] if j==len(labels)-1 else 'white')
        if j<len(labels)-1:arrow((center,y),(center,ys[j+1]+4.1))
    arrow((center,18.9),(center,15.7))

group_box(2.2,2.1,95.6,13.5,'阶段五  经营应用',orange)
for x,label in [(4.2,'分时排班'),(36.8,'区域资源安排'),(69.4,'预测偏离复核')]:
    node(x,8.5,26.4,3.3,label,orange[0])
    arrow((x+13.2,8.5),(x+13.2,6.4))
node(4.2,3.1,91.6,3.3,'经营建议与交互式可视化看板',orange[0],orange[1],size=13)
save(fig,17,'研究技术路线','研究流程')
pd.DataFrame(index).to_csv(TABLES/'figure_index.csv',index=False,encoding='utf-8-sig')
print('图表已生成：17张PNG与对应SVG，分辨率220 dpi。')
