"""Ten textbook-format recreations, six separate model figures and a workflow."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

def canvas(title, subtitle='',dark=False,figsize=(10,6.4)):
    bg,ink=(DARK,WHITE) if dark else (BG,INK)
    fig,ax=plt.subplots(figsize=figsize,facecolor=bg)
    ax.set_facecolor(bg)
    fig.subplots_adjust(left=.12,right=.94,top=.79,bottom=.17)
    fig.text(.07,.94,title,fontsize=20,weight='bold',color=ink,va='top')
    fig.text(.07,.875,subtitle,fontsize=10,color=SKY if dark else MUTED,va='top')
    ax.tick_params(colors=ink,labelsize=9)
    for sp in ax.spines.values():sp.set_color('#646A89' if dark else '#CDDBDF')
    ax.yaxis.label.set_color(ink);ax.xaxis.label.set_color(ink)
    return fig,ax

def save(fig,num,name,kind,template='',note=''):
    dark=kind=='模板复现'
    fig.text(.07,.045,note or '数据：杭州文化和旅游数据在线开放平台，2026-10-22下载；作者Python绘制。',
             fontsize=8,color=SKY if dark else MUTED)
    path=FIGURES/f'fig{num:02d}_{name}.png'
    fig.savefig(path,dpi=220,facecolor=fig.get_facecolor())
    fig.savefig(path.with_suffix('.svg'),facecolor=fig.get_facecolor())
    plt.close(fig)
    index.append(dict(number=f'fig{num:02d}',name=name,category=kind,template=template,file=path.name))

def legend(ax,dark=False,**kwargs):
    leg=ax.legend(frameon=False,**kwargs)
    if leg:
        for text in leg.get_texts():text.set_color(WHITE if dark else INK)

a=monthly[monthly.index.year==2024]['occupancy'].values
b=monthly[monthly.index.year==2025]['occupancy'].values
x=np.arange(12)

fig,ax=canvas('上半年酒店入住率年度对比','2024年与2025年1—6月  |  对比柱形图',True)
xx=np.arange(6);v1=a[:6];v2=b[:6]
ax.bar(xx-.18,v1,.32,color=BLUE,label='2024年');ax.bar(xx+.18,v2,.32,color=SKY,label='2025年')
for i,(v,w) in enumerate(zip(v1,v2)):
    ax.text(i-.18,v+1,f'{v:.1f}',ha='center',color=WHITE,fontsize=10)
    ax.text(i+.18,w-4,f'{w:.1f}',ha='center',color=WHITE,fontsize=10)
    ax.text(i,76,f'{w-v:+.1f}个百分点',ha='center',color=SKY,fontsize=9)
ax.set(xticks=xx,xticklabels=[f'{i}月' for i in range(1,7)],ylim=(0,85),ylabel='入住率（%）')
legend(ax,True,loc='upper left',bbox_to_anchor=(0,1.05),ncol=2)
save(fig,1,'对比柱形图','模板复现','第二章9 对比柱形图')

fig,ax=canvas('酒店入住率的月度轨迹','2024年与2025年全年对照  |  对比折线图',True)
ax.plot(x,a,'o-',color=BLUE,lw=2.3,label='2024年');ax.plot(x,b,'o-',color=SKY,lw=2.3,label='2025年')
for i,v in enumerate(b):ax.text(i,v+1.2,f'{v:.1f}',color=WHITE,ha='center',fontsize=8)
ax.set(xticks=x,xticklabels=[f'{i}月' for i in range(1,13)],ylim=(25,85),ylabel='入住率（%）')
legend(ax,True,loc='lower center',ncol=2)
save(fig,2,'对比折线图','模板复现','第二章1 对比折线图')

vals=dy['2025'].sort_values(ascending=False)
fig,ax=canvas('各区县酒店入住率与全市基准','2025年日度均值  |  均值柱形图',True)
ax.bar(np.arange(len(vals)),vals,color=BLUE,width=.56)
ax.axhline(summary['city_2025'],color=SKY,ls='--',lw=1.5,label=f"全市官方序列均值 {summary['city_2025']:.1f}%")
for i,v in enumerate(vals):ax.text(i,v+1,f'{v:.1f}',ha='center',color=WHITE,fontsize=8)
ax.set(xticks=np.arange(len(vals)),xticklabels=vals.index,ylim=(0,85),ylabel='入住率（%）')
ax.tick_params(axis='x',rotation=45);legend(ax,True,loc='upper right')
save(fig,3,'均值柱形图','模板复现','第二章2 均值柱形图')

fig,ax=canvas('全年入住率的高低月份','2025年各月日度均值  |  标注柱形图',True)
ax.bar(x,b,color=BLUE,width=.55)
peak=int(np.argmax(b));low=int(np.argmin(b))
for i,v in enumerate(b):ax.text(i,v+1,f'{v:.1f}',ha='center',color=WHITE,fontsize=9)
ax.annotate(f'最高月 {peak+1}月',xy=(peak,b[peak]),xytext=(peak-1,82),color=SKY,
            arrowprops=dict(arrowstyle='->',color=SKY),ha='center')
ax.annotate(f'最低月 {low+1}月',xy=(low,b[low]),xytext=(low+1,31),color='#F1B09A',
            arrowprops=dict(arrowstyle='->',color='#F1B09A'))
ax.set(xticks=x,xticklabels=[f'{i}月' for i in range(1,13)],ylim=(0,90),ylabel='入住率（%）')
save(fig,4,'标注柱形图','模板复现','第二章6 标注柱形图')

fig,ax=canvas('入住水平与月度变化','2025年月度均值及相邻月份的百分点变化  |  柱形折线图',True)
bars=ax.bar(x,b,color=BLUE,width=.52,label='月均入住率')
ax.set(xticks=x,xticklabels=[f'{i}月' for i in range(1,13)],ylim=(0,90),ylabel='入住率（%）')
ax2=ax.twinx();ax2.plot(x,monthly.loc['2025','mom_pp'],color=SKY,marker='o',lw=2,label='环比百分点变化')
ax2.tick_params(colors=SKY);ax2.set_ylabel('环比变化（百分点）',color=SKY);ax2.spines['right'].set_visible(True)
ax2.spines['right'].set_color(SKY);ax2.set_ylim(-25,25)
ax.legend([bars,ax2.lines[0]],['月均入住率','环比百分点变化'],loc='upper center',ncol=2,frameon=False,labelcolor=WHITE)
save(fig,5,'柱形折线图','模板复现','第二章20 柱形折线图')

order=dy.sort_values('2025').index;y=np.arange(len(order))
fig,ax=canvas('区域入住率的年度镜像','左侧2024年  右侧2025年；左右长度分别比较各年入住率  |  蝴蝶图',True,figsize=(10,7.5))
ax.barh(y,-dy.loc[order,'2024'],color=BLUE,height=.6,label='2024年')
ax.barh(y,dy.loc[order,'2025'],color=SKY,height=.6,label='2025年')
ax.set(yticks=y,yticklabels=order,xlim=(-90,90),xlabel='入住率（%，两侧均以正值读取）')
ax.set_xticks([-80,-40,0,40,80],labels=['80','40','0','40','80']);ax.axvline(0,color='#69728C',lw=1)
for i,area in enumerate(order):
    ax.text(-dy.loc[area,'2024']-2,i,f"{dy.loc[area,'2024']:.1f}",ha='right',va='center',color=WHITE,fontsize=8)
    ax.text(dy.loc[area,'2025']+2,i,f"{dy.loc[area,'2025']:.1f}",va='center',color=WHITE,fontsize=8)
legend(ax,True,loc='upper right',ncol=2)
save(fig,6,'蝴蝶图','模板复现','第二章13 蝴蝶图')

fig,ax=canvas('区县入住率的年度移动','圆点为年度日均水平，连线展示变化方向  |  对比滑珠图',True,figsize=(10,7.5))
for i,area in enumerate(order):ax.plot([dy.loc[area,'2024'],dy.loc[area,'2025']],[i,i],color='#7586A9',lw=3,zorder=1)
ax.scatter(dy.loc[order,'2024'],y,color=BLUE,s=90,label='2024年',zorder=3)
ax.scatter(dy.loc[order,'2025'],y,color=SKY,s=90,label='2025年',zorder=4)
for i,area in enumerate(order):ax.text(79,i,f"{dy.loc[area,'change_pp']:+.1f} pp",color=WHITE,va='center',fontsize=9)
ax.set(yticks=y,yticklabels=order,xlim=(25,91),xlabel='入住率（%）');legend(ax,True,loc='upper right',ncol=2)
save(fig,7,'对比滑珠图','模板复现','第二章17 对比滑珠图')

fig,ax=canvas('区县入住率相对上年基准','短条为2025年日均值，竖线为2024年实际值  |  子弹图',True,figsize=(10,7.5))
ax.barh(y,[100]*len(y),height=.58,color='#30385E')
ax.barh(y,dy.loc[order,'2025'],height=.28,color=SKY,label='2025年实际')
for i,area in enumerate(order):ax.plot([dy.loc[area,'2024']]*2,[i-.32,i+.32],color='#F5C353',lw=2)
ax.plot([],[],color='#F5C353',lw=2,label='2024年实际基准')
ax.set(yticks=y,yticklabels=order,xlim=(0,100),xlabel='入住率（%）');legend(ax,True,loc='upper left',bbox_to_anchor=(0,1.06),ncol=2)
save(fig,8,'子弹图','模板复现','第二章25 子弹图',note='基准采用上年实际水平，不设置或虚构经营目标。来源：杭州文化和旅游数据在线开放平台。')

fig,ax=canvas('2025年全市酒店平均入住水平','日度官方入住率的算术平均  |  单值圆环图',True)
v=summary['city_2025'];ax.pie([v,100-v],startangle=90,counterclock=False,colors=[SKY,'#30385E'],
                            wedgeprops=dict(width=.18,edgecolor=DARK))
ax.text(0,.06,f'{v:.1f}%',fontsize=40,weight='bold',color=WHITE,ha='center',va='center')
ax.text(0,-.24,'年度日均入住率',color=SKY,ha='center',fontsize=13)
save(fig,9,'单值圆环图','模板复现','第二章7 单值圆环图',note='剩余弧段表示100%减去日均入住率，不据此计算空置客房总量。来源同前。')

fig=plt.figure(figsize=(10,7),facecolor=DARK);ax=fig.add_axes([.22,.17,.56,.62],projection='polar',facecolor=DARK)
theta=np.arange(12)*2*np.pi/12;ax.set_theta_zero_location('N');ax.set_theta_direction(-1)
# Radius is transformed so annular sector area, not radius, is proportional to the rate.
inner=4;radius=np.sqrt(inner**2+b)
ax.bar(theta,radius-inner,bottom=inner,width=2*np.pi/12*.9,color=[BLUE,SKY]*6,edgecolor=DARK)
ax.set_xticks(theta,labels=[f'{i}月' for i in range(1,13)],color=WHITE);ax.set_yticks([]);ax.grid(False);ax.spines['polar'].set_visible(False)
for t,r,v in zip(theta,radius,b):ax.text(t,r+.8,f'{v:.1f}',color=WHITE,ha='center',va='center',fontsize=9)
fig.text(.07,.94,'月度入住率的径向对照',fontsize=20,weight='bold',color=WHITE)
fig.text(.07,.875,'2025年日均值；扇环面积与入住率成比例  |  南丁格尔圆环图',fontsize=10,color=SKY)
save(fig,10,'南丁格尔圆环图','模板复现','第二章22 南丁格尔圆环图')

fig,ax=canvas('年度均值改善是否覆盖全年','模型一  趋势与对比分析；柱体表示2025年相对2024年的同月变化')
delta=b-a;ax.bar(x,delta,color=[COLORS[0] if v>=0 else COLORS[2] for v in delta],width=.58)
ax.axhline(0,color=MUTED,lw=.8)
for i,v in enumerate(delta):ax.text(i,v+(.3 if v>=0 else -.3),f'{v:+.1f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
ax.set(xticks=x,xticklabels=[f'{i}月' for i in range(1,13)],ylabel='同比变化（百分点）')
save(fig,11,'月度同比差异','业务模型','趋势与对比')

fig,ax=canvas('周内需求的节奏','模型一  周期比较；点为均值，误差线为样本标准差，并非置信区间')
w=city.groupby('weekday')['occupancy'].agg(['mean','std'])
ax.errorbar(range(7),w['mean'],yerr=w['std'],fmt='o-',capsize=5,color=COLORS[0],ecolor=COLORS[1],lw=2,markersize=7)
for i,v in enumerate(w['mean']):ax.text(i,v+2,f'{v:.1f}',ha='center',color=INK)
ax.set(xticks=range(7),xticklabels=['周一','周二','周三','周四','周五','周六','周日'],ylabel='入住率（%）',ylim=(20,90))
ax.grid(axis='y',color='#E2EAED',lw=.6)
save(fig,12,'周内入住率特征','业务模型','趋势与对比')

fig,ax=canvas('区县市场的入住水平与波动','模型二  K-Means；按2024—2025年均值、波动、周末差与季节幅度分组')
for cluster,g in features.groupby('cluster'):
    ax.scatter(g['mean'],g['volatility'],s=95,color=COLORS[int(cluster)-1],label=f'第{cluster}组',edgecolor='white',lw=1,zorder=3)
    for j,(area,row) in enumerate(g.iterrows()):
        ax.annotate(area,(row['mean'],row['volatility']),xytext=(5,5 if j%2==0 else -13),textcoords='offset points',fontsize=9)
ax.set(xlabel='日均入住率（%）',ylabel='日度标准差（百分点）');ax.margins(.23)
legend(ax,loc='upper right');ax.grid(color='#E2EAED',lw=.6)
save(fig,13,'区县聚类散点图','业务模型','K-Means')

fcols=['mean','volatility','weekend_gap','seasonal_range']; f=features.sort_values(['cluster','mean'],ascending=[True,False])
z=(f[fcols]-features[fcols].mean())/features[fcols].std(ddof=0)
fig,ax=canvas('区县分组的四维画像','模型二  各特征已标准化；0表示13个区县的该项平均水平',figsize=(10,7.5))
cm=LinearSegmentedColormap.from_list('mint_coral',[COLORS[0],'#F8FAFB',COLORS[2]])
im=ax.imshow(z,aspect='auto',cmap=cm,vmin=-2,vmax=2)
ax.set_xticks(range(4),labels=['平均入住率','日度波动','周末与工作日差','月均季节幅度'])
ax.set_yticks(range(len(f)),labels=[f'{a}  第{int(f.loc[a,"cluster"])}组' for a in f.index])
for i in range(len(f)):
    for j in range(4):ax.text(j,i,f'{z.iloc[i,j]:+.2f}',ha='center',va='center',color=INK,fontsize=9)
fig.colorbar(im,ax=ax,fraction=.025,pad=.025,label='标准分数')
save(fig,14,'聚类特征热力图','业务模型','K-Means')

bt=pd.read_csv(TABLES/'forecast_backtest.csv',parse_dates=['date'])
fig,ax=canvas('模型在未见数据上的表现','模型三  三次28日滚动回测；阴影为SARIMA的95%预测区间',figsize=(11,6.4))
ax.plot(bt.date,bt.actual,color=INK,lw=1.5,label='实际值')
ax.plot(bt.date,bt.prediction,color=COLORS[0],lw=1.7,label='SARIMA')
ax.plot(bt.date,bt.weekly_naive,color=COLORS[2],lw=1,alpha=.8,label='周季节朴素法')
ax.fill_between(bt.date,bt.lower,bt.upper,color=COLORS[1],alpha=.24)
for fold,g in bt.groupby('fold'):
    ax.axvline(g.date.iloc[0],color=MUTED,ls=':',lw=.8)
ax.set(ylabel='入住率（%）');legend(ax,loc='upper left',ncol=3);ax.tick_params(axis='x',rotation=15)
save(fig,15,'滚动回测与误差','业务模型','SARIMA')

future=pd.read_csv(TABLES/'forecast_2026_january.csv',parse_dates=['date'])
fig,ax=canvas('样本截止日之后的28日预测','模型三  预测原点为2025年12月31日；属于历史样本外预测，不是当前实时预报',figsize=(11,6.4))
hist=city.loc['2025-10-01':,'occupancy'];ax.plot(hist.index,hist,color=INK,lw=1.3,label='历史真实观测')
ax.plot(future.date,future.prediction,color=COLORS[0],lw=2,label='点预测')
ax.fill_between(future.date,future.lower,future.upper,color=COLORS[1],alpha=.4,label='95%预测区间')
ax.axvline(pd.Timestamp('2025-12-31'),color=MUTED,ls='--',lw=1)
ax.set(ylabel='入住率（%）');legend(ax,loc='upper left',ncol=3);ax.tick_params(axis='x',rotation=15)
save(fig,16,'未来28日预测区间','业务模型','SARIMA')

fig=plt.figure(figsize=(11,5),facecolor=BG);ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
fig.text(.05,.93,'从公开数据到经营判断',fontsize=21,weight='bold',color=INK)
stages=[('官方下载','2张原始Excel\n保留文件与哈希'),('数据治理','口径统一与缺日标记\n按区域和日期对齐'),('模型分析','趋势对比  区县聚类\n滚动回测  区间预测'),('结果应用','16张图  联动大屏\n经营建议与局限披露')]
for i,(title,desc) in enumerate(stages):
    x0=.05+i*.24
    ax.add_patch(FancyBboxPatch((x0,.31),.21,.43,boxstyle='round,pad=.012,rounding_size=.018',facecolor='#E6F1F1',edgecolor=COLORS[0],lw=1))
    ax.text(x0+.105,.64,title,ha='center',fontsize=16,weight='bold',color=COLORS[0])
    ax.text(x0+.105,.46,desc,ha='center',va='center',fontsize=11,color=INK,linespacing=1.8)
    if i<3:ax.annotate('',xy=(x0+.235,.52),xytext=(x0+.215,.52),arrowprops=dict(arrowstyle='->',color=COLORS[0],lw=2))
ax.text(.5,.18,'验证约束：真实样本不少于500条  预测按时间切分  结果可追溯到原始文件',ha='center',color=MUTED,fontsize=11)
save(fig,17,'研究技术路线','研究流程')
pd.DataFrame(index).to_csv(TABLES/'figure_index.csv',index=False,encoding='utf-8-sig')
print('图表已生成：17张PNG与对应SVG，分辨率220 dpi。')
