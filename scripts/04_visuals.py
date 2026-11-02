"""Ten textbook-format recreations, six separate model figures and a workflow."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Wedge, Circle, FancyBboxPatch
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

fig=plt.figure(figsize=(11,3.3),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
stages=[('数据整理','日期对齐\n缺失与异常检查'),('特征提取','时间特征\n区县画像'),('模型分析','趋势对比  区县聚类\n回测与区间预测'),('经营应用','交互可视化\n经营建议')]
for i,(title,desc) in enumerate(stages):
    x0=.05+i*.24
    ax.add_patch(FancyBboxPatch((x0,.22),.21,.56,boxstyle='round,pad=.012,rounding_size=.018',facecolor='#E6F1F1',edgecolor=COLORS[0],lw=1))
    ax.text(x0+.105,.64,title,ha='center',fontsize=15,weight='bold',color=COLORS[0])
    ax.text(x0+.105,.42,desc,ha='center',va='center',fontsize=11,color=INK,linespacing=1.8)
    if i<3:ax.annotate('',xy=(x0+.235,.52),xytext=(x0+.215,.52),arrowprops=dict(arrowstyle='->',color=COLORS[0],lw=2))
save(fig,17,'研究技术路线','研究流程')
pd.DataFrame(index).to_csv(TABLES/'figure_index.csv',index=False,encoding='utf-8-sig')
print('图表已生成：17张PNG与对应SVG，分辨率220 dpi。')
