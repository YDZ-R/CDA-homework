"""Recreate ten selected Chapter 2 layouts with the Hangzhou observations."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Wedge, FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import PchipInterpolator

BG='#1A1E43'; BLUE='#0070C0'; SKY='#82ADD7'; RED='#E74E69'
WHITE='#FFFFFF'; GRAY='#72758A'; GOLD='#FFC000'


def board(title,subtitle,height=617):
    fig=plt.figure(figsize=(8.32,height/100),facecolor=BG)
    ax=fig.add_axes([0,0,1,1],xlim=(0,832),ylim=(height,0))
    ax.set_axis_off()
    ax.text(50,40,title,color=WHITE,fontsize=26,weight='bold',va='top')
    ax.text(50,99,subtitle,color=WHITE,fontsize=16,va='top')
    return fig,ax


def text(ax,x,y,value,size=11,color=WHITE,ha='center',**kwargs):
    return ax.text(x,y,str(value),fontsize=size,color=color,ha=ha,va='center',**kwargs)


def rect(ax,x,y,w,h,color):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor='none'))


def key(ax,items,x=64,y=184):
    for color,label in items:
        rect(ax,x,y-4,12,9,color);text(ax,x+18,y,label,11,ha='left')
        x+=125


def draw_templates(city,monthly,dy,summary,save):
    # The category counts, placement, colors and marks follow the Excel examples.
    areas=['淳安县','建德市','萧山区','余杭区','临安区']
    old=dy.loc[areas,'2024'].to_numpy();new=dy.loc[areas,'2025'].to_numpy()
    fig,ax=board('2025年区县酒店入住率同比','日均入住率（%），同比差值为百分点',645)
    key(ax,[(BLUE,'2024年'),(SKY,'2025年')])
    base=540;scale=4.5
    ax.plot([53,780],[base,base],color=GRAY,lw=.7)
    for x,area,v,w in zip(np.linspace(109,685,5),areas,old,new):
        rect(ax,x-17,base-v*scale,33,v*scale,BLUE)
        rect(ax,x+25,base-w*scale,33,w*scale,SKY)
        text(ax,x,base-v*scale-15,f'{v:.1f}')
        text(ax,x+41,base-w*scale+18,f'{w:.1f}')
        arrow=x+42
        ax.annotate('',xy=(arrow,base-w*scale-2),xytext=(arrow,base-v*scale-2),
                    arrowprops=dict(arrowstyle='-|>',color=WHITE,lw=.9,mutation_scale=9))
        text(ax,arrow+16,base-(v+w)*scale/2-10,f'{w-v:+.1f}',10,ha='left')
        text(ax,x+21,base+27,area,13)
    save(fig,1,'对比柱形图','模板复现','第二章9 对比柱形图')

    a=monthly.loc['2024','occupancy'].to_numpy();b=monthly.loc['2025','occupancy'].to_numpy()
    fig,ax=board('2025年上半年月均入住率同比','2024年与2025年1—6月入住率（%）',622)
    plot=fig.add_axes([.13,.155,.815,.49],facecolor=BG)
    plot.set(ylim=(0,80),xlim=(-.45,5.45),xticks=range(6),
             xticklabels=[f'{i}月' for i in range(1,7)],yticks=range(0,81,20))
    plot.tick_params(colors=WHITE,length=0,labelsize=11,pad=10)
    for sp in plot.spines.values():sp.set_visible(False)
    plot.grid(axis='y',color=GRAY,ls='--',alpha=.55,lw=.7)
    plot.plot(range(6),a[:6],'o-',color=RED,lw=2,label='2024年',ms=6)
    plot.plot(range(6),b[:6],'o-',color=BLUE,lw=2,label='2025年',ms=6)
    for i,(v,w) in enumerate(zip(a[:6],b[:6])):
        plot.annotate(f'{v:.1f}',(i,v),xytext=(0,-23 if v<w else 15),
                      textcoords='offset points',ha='center',color=WHITE,fontsize=10)
        plot.annotate(f'{w:.1f}',(i,w),xytext=(0,15 if w>=v else -23),
                      textcoords='offset points',ha='center',color=WHITE,fontsize=10)
    plot.legend(loc='upper right',bbox_to_anchor=(1,1.19),ncol=2,frameon=False,
                labelcolor=WHITE,fontsize=11,handlelength=2,handletextpad=.3)
    save(fig,2,'对比折线图','模板复现','第二章13 对比折线图')

    six=['上城区','拱墅区','西湖区','滨江区','萧山区','余杭区']
    values=dy.loc[six,'2025'].to_numpy();mean=values.mean()
    fig,ax=board('2025年六区酒店入住率分布','六区日均入住率及其算术均值（%）',594)
    xs=np.linspace(108,738,6);base=495;scale=4.8
    for x,v,area in zip(xs,values,six):
        rect(ax,x-19,base-v*scale,38,v*scale,BLUE)
        text(ax,x,base-v*scale-19,f'{v:.1f}')
        text(ax,x,base+25,area,13)
    ax.plot([49,802],[base,base],color=GRAY,lw=.8)
    ax.plot([93,765],[base-mean*scale]*2,color=GOLD,lw=2)
    text(ax,775,base-mean*scale-51,f'六区均值：{mean:.1f}',11,GOLD,ha='right')
    save(fig,3,'均值柱形图','模板复现','第二章2 带均值柱形图')

    eight=['上城区','拱墅区','西湖区','滨江区','萧山区','余杭区','淳安县','桐庐县']
    values=dy.loc[eight,'2025'].to_numpy()
    colors=['#80BDCF','#489F9A','#EB6A49','#FFC000','#0097D6',BLUE,'#4D55D7','#46469F']
    fig,ax=board('2025年八区县酒店入住水平','八区县年度日均入住率（%）',616)
    base=515;scale=4.35;xs=np.linspace(160,762,8)
    for v in range(0,81,20):
        yy=base-v*scale;ax.plot([119,800],[yy,yy],ls='--',lw=.6,color=GRAY,alpha=.6)
        text(ax,101,yy,v,11,ha='right')
    for i,(x,v,area,c) in enumerate(zip(xs,values,eight,colors)):
        top=base-v*scale;rect(ax,x-20,top,40,v*scale,c)
        bx=x-21;by=top-38
        rect(ax,bx,by,45,25,c)
        tail=[(x-12,by+25),(x-5,top-4),(x-3,by+25)] if i%2==0 else [(x+4,by+25),(x-3,top-4),(x+14,by+25)]
        ax.add_patch(Polygon(tail,facecolor=c,edgecolor='none'))
        text(ax,x+1,by+12,f'{v:.1f}',10)
        text(ax,x,base+26,area,11)
    save(fig,4,'标注柱形图','模板复现','第二章4 标注柱形图')

    vals=b[6:];growth=monthly.loc['2025','yoy_pct'].to_numpy()[6:]
    fig,ax=board('2025年下半年入住率及同比','月均入住率与同月相对增幅',617)
    key(ax,[(BLUE,'入住率（%）'),(RED,'同比（%）')],x=540,y=154)
    xs=np.linspace(123,708,6);base=500
    for x,v,m in zip(xs,vals,range(7,13)):
        h=v*3.1;rect(ax,x-18,base-h,36,h,BLUE)
        text(ax,x,base-h-18,f'{v:.1f}',12);text(ax,x,base+26,f'{m}月',12)
    ys=250-growth*15
    ax.plot(xs,ys,'o-',color=RED,ms=6,lw=2)
    for x,y,v in zip(xs,ys,growth):text(ax,x,y-27,f'{v:.1f}%',12)
    save(fig,5,'柱形折线图','模板复现','第二章23 柱形折线图')

    fig,ax=board('2025年五区县入住率同比','两年区县日均入住率（%）',588)
    text(ax,310,166,'2025年',15,BLUE);text(ax,516,166,'2024年',15,RED)
    for yy,area,v,w in zip(np.linspace(204,484,5),areas,old,new):
        rect(ax,368-w*3.7,yy-14,w*3.7,28,BLUE)
        rect(ax,488,yy-14,v*3.7,28,RED)
        text(ax,428,yy,area,13)
        text(ax,368-w*3.7+12,yy,f'{w:.1f}',11,ha='left')
        text(ax,488+v*3.7-12,yy,f'{v:.1f}',11,ha='right')
    save(fig,6,'蝴蝶图','模板复现','第二章6 蝴蝶图')

    order=sorted(areas,key=lambda q:dy.loc[q,'2025'],reverse=True)
    fig,ax=board('2025年五区县酒店入住率对比','圆点分别表示2024年与2025年日均入住率',593)
    for x,col,label in [(76,BLUE,'2025年'),(205,'#A6A6A6','2024年')]:
        ax.plot(x,155,'o',ms=12,mfc=col,mec=WHITE,mew=1.4)
        text(ax,x+24,155,label,11,ha='left')
    for yy,area in zip(np.linspace(198,493,5),order):
        v,w=dy.loc[area,['2024','2025']]
        start,end=124,661;rect(ax,start,yy-6,end-start,12,GRAY)
        rect(ax,start,yy-6,(end-start)*w/100,12,BLUE)
        text(ax,start-18,yy,area,13,ha='right')
        for value,col in [(v,'#A6A6A6'),(w,BLUE)]:
            ax.plot(start+(end-start)*value/100,yy,'o',ms=14,mfc=col,mec=WHITE,mew=1.4)
        text(ax,start+(end-start)*w/100,yy-28,f'{w:.1f}%',12)
    save(fig,7,'对比滑珠图','模板复现','第二章30 对比滑珠图')

    data=monthly.loc['2024-05-01':'2025-03-01','occupancy'];v=data.to_numpy()
    fig,ax=board('酒店月均入住率走势','2024年5月至2025年3月入住率（%）',617)
    xs=np.linspace(128,767,len(v));base=470;scale=4.0;ys=base-v*scale
    ax.plot([97,799],[base,base],color=WHITE,lw=.6)
    for tick in range(0,81,20):text(ax,79,base-tick*scale,tick,11,'#F66732',ha='right')
    smooth=np.linspace(xs[0],xs[-1],600)
    ax.plot(smooth,PchipInterpolator(xs,ys)(smooth),color='#FF6726',lw=1.5)
    peak=int(v.argmax());ax.plot([xs[peak]]*2,[ys[peak],base],color=RED,ls='--',lw=.8)
    text(ax,xs[peak],ys[peak]-17,f'{v[peak]:.1f}',12)
    for x,date in zip(xs,data.index):
        ax.plot([x,x],[base,base+6],color=WHITE,lw=.6)
        text(ax,x,base+23,f'{date.month}月',12)
    for x,w,label,c in [(78,532,'2024年','#65C9DA'),(618,195,'2025年','#F5C353')]:
        ax.add_patch(FancyBboxPatch((x,515),w,32,boxstyle='round,pad=0,rounding_size=6',facecolor=c,edgecolor='none'))
        text(ax,x+w/2,531,label,13)
    save(fig,8,'平滑折线图','模板复现','第二章11 平滑折线图')

    v=summary['city_2025'];fig,ax=board('2025年全市酒店平均入住率','全年真实观测的日均入住水平',617)
    cx,cy=423,345;radius=174;width=17
    ax.add_patch(Wedge((cx,cy),radius,0,360,width=width,facecolor='#303455',edgecolor='none'))
    cmap=LinearSegmentedColormap.from_list('ring',['#7030A0',RED])
    span=360*v/100;start=180+(360-span)/2
    for i in range(360):
        a0=start+span*i/360
        ax.add_patch(Wedge((cx,cy),radius,a0,a0+span/360+.15,width=width,facecolor=cmap(i/359),edgecolor='none'))
    text(ax,cx,328,f'{v:.1f}%',44);text(ax,cx,409,'日均入住率',16)
    save(fig,9,'单值圆环图','模板复现','第二章14 单值圆环图')

    observed=city.loc['2025','occupancy']
    counts=pd.cut(observed,[0,50,60,70,100.0001],right=False).value_counts(sort=False)
    names=['50%以下','50%—60%','60%—70%','70%及以上']
    ranked=sorted(zip(names,counts.to_numpy()),key=lambda pair:pair[1],reverse=True)
    shares=np.array([c for _,c in ranked])/len(observed)
    fig,ax=board('2025年入住水平的天数分布','按全市每日入住率分组',624)
    cx,cy=417,375;inner=108;start=-90
    colors=['#512DCB','#6073F3','#66CBDD','#F5C353']
    for i,((name,count),share,c) in enumerate(zip(ranked,shares,colors)):
        outer=180-i*14;angle=share*360
        ax.add_patch(Wedge((cx,cy),outer,start,start+angle,width=outer-inner,facecolor=c,edgecolor='none'))
        mid=np.radians(start+angle/2);right=np.cos(mid)>=0
        px=cx+(outer+12)*np.cos(mid);py=cy+(outer+12)*np.sin(mid)
        x2=648 if right else 188
        y2=[320,505,330,195][i]
        ax.plot([px,x2,x2+(88 if right else -88)],[py,y2,y2],color=c,lw=.7)
        ax.plot(px,py,'o',ms=4,color=c)
        align='left' if right else 'right';tx=x2+(5 if right else -5)
        text(ax,tx,y2-40,name,12,ha=align)
        text(ax,tx,y2-17,f'{share:.1%}',12,c,ha=align)
        start+=angle
    save(fig,10,'南丁格尔圆环图','模板复现','第二章20 南丁格尔圆环图')
