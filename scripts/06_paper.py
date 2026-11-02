"""Fill a preserved university template using verified analysis outputs."""
from pathlib import Path
from copy import deepcopy
import json
import re
import hashlib
import zipfile
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from common import ROOT, TABLES, FIGURES

template=ROOT/'docs/学校论文模板.docx'
if not template.exists():
    raise FileNotFoundError('缺少已归档的学校论文模板 docs/学校论文模板.docx')
s=json.loads((TABLES/'analysis_summary.json').read_text(encoding='utf-8'))
audit=json.loads((TABLES/'cleaning_audit.json').read_text(encoding='utf-8'))
dy=pd.read_csv(TABLES/'district_year.csv',index_col=0)
feat=pd.read_csv(TABLES/'district_features.csv',index_col=0)
monthly=pd.read_csv(TABLES/'monthly_comparison.csv',index_col=0,parse_dates=True)
weekday=pd.read_csv(TABLES/'weekday_summary.csv',index_col=0)
metrics=pd.read_csv(TABLES/'forecast_metrics.csv')
index=pd.read_csv(TABLES/'figure_index.csv')
doc=Document(template)
original=doc.paragraphs
middle_break=deepcopy(original[21]._p)
body=doc._element.body
anchor=original[10]._p
seen=False
for el in list(body):
    if el is anchor:seen=True;continue
    if seen and el.tag!=qn('w:sectPr'):body.remove(el)
# The reference has an accidental near-empty second cover page; omit its repeated college line.
college=original[9]._p
body.remove(college)
fields={3:('题　　目：','杭州酒店入住率分析与预测'),4:('学　　院：','数据科学学院'),
        5:('专业班级：','大数据241'),6:('学　　号：','2024459985112'),
        7:('姓　　名：','曹俊男'),8:('完成日期：','2026年11月2日')}
for i,(label,value) in fields.items():
    p=original[i]
    for r in p.runs:r.text=''
    p.add_run(label)
    r=p.add_run(value+'　'*(max(0,20-len(value))));r.underline=True
    for r in p.runs:r.font.name='楷体';r.font.size=Pt(14);r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'楷体')

def font(run,size=12,bold=False,name='宋体'):
    run.font.name=name;run.font.size=Pt(size);run.font.bold=bold;run.font.color.rgb=RGBColor(0,0,0)
    run._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),name)

for styname in ['Normal','Title','Heading 1','Heading 2','Heading 3']:
    if styname not in doc.styles:
        doc.styles.add_style(styname,WD_STYLE_TYPE.PARAGRAPH)
    sty=doc.styles[styname];sty.font.color.rgb=RGBColor(0,0,0)
    if styname=='Normal':
        sty.font.name='宋体';sty.font.size=Pt(12);sty._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'宋体')

article=[]

def no_indent(p):
    p.paragraph_format.first_line_indent=Pt(0)
    p.paragraph_format.left_indent=Pt(0);p.paragraph_format.right_indent=Pt(0)
    for ind in p._p.xpath('./w:pPr/w:ind'):
        for attr in ('firstLineChars','leftChars','rightChars'):
            ind.set(qn('w:'+attr),'0')

def para(text,style=None):
    p=doc.add_paragraph(style=style)
    p.paragraph_format.line_spacing=1.4;p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(3)
    p.paragraph_format.first_line_indent=Pt(24)
    p.paragraph_format.widow_control=True
    font(p.add_run(text))
    article.append(text)
    return p

def heading(text,level=1):
    p=doc.add_paragraph(style=f'Heading {level}')
    num=p._p.xpath('./w:pPr/w:numPr')
    for n in num:n.getparent().remove(n)
    # Explicit numbering avoids carrying the reference's empty heading counters.
    numPr=OxmlElement('w:numPr');numId=OxmlElement('w:numId');numId.set(qn('w:val'),'0');numPr.append(numId);p._p.get_or_add_pPr().append(numPr)
    p.paragraph_format.keep_with_next=True;p.paragraph_format.first_line_indent=Pt(0)
    p.paragraph_format.space_before=Pt(10 if level==1 else 6);p.paragraph_format.space_after=Pt(4)
    p.paragraph_format.line_spacing=1.3
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER if level==1 else WD_ALIGN_PARAGRAPH.LEFT
    font(p.add_run(text),14 if level==1 else 12,True,'黑体' if level==1 else '宋体')
    article.append(text);return p

def caption(text,before_table=False):
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(2);p.paragraph_format.space_after=Pt(4)
    p.paragraph_format.line_spacing=1.1;no_indent(p)
    p.paragraph_format.keep_with_next=before_table
    font(p.add_run(text),10)

def figure(number,cap,width=14.4):
    f=next(FIGURES.glob(f'fig{number:02d}_*.png'))
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    no_indent(p);p.paragraph_format.keep_with_next=True
    p.paragraph_format.space_before=Pt(2);p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.line_spacing=1.0
    p.add_run().add_picture(str(f),width=Cm(width))
    caption(cap)

def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths:
        widths=[v*14.5/sum(widths) for v in widths]
        for col,w in zip(t.columns,widths):col.width=Cm(w)
    for i,h in enumerate(headers):t.rows[0].cells[i].text=str(h)
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','bottom','left','right','insideH','insideV']:
        e=OxmlElement('w:'+edge)
        e.set(qn('w:val'),'single' if edge in ('top','bottom') else 'nil')
        e.set(qn('w:sz'),'10');e.set(qn('w:color'),'000000');borders.append(e)
    t._tbl.tblPr.append(borders)
    for row in rows:
        for c,v in zip(t.add_row().cells,row):c.text=str(v)
    for ri,row in enumerate(t.rows):
        trPr=row._tr.get_or_add_trPr()
        if ri==0:
            repeat=OxmlElement('w:tblHeader');trPr.append(repeat)
        cant=OxmlElement('w:cantSplit');trPr.append(cant)
        for ci,c in enumerate(row.cells):
            if widths:c.width=Cm(widths[ci])
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcPr=c._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'FFFFFF');tcPr.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                visible=(ri==0 and edge in ('top','bottom')) or (ri==len(t.rows)-1 and edge=='bottom')
                e=OxmlElement(f'w:{edge}');e.set(qn('w:val'),'single' if visible else 'nil')
                e.set(qn('w:sz'),'6' if ri==0 and edge=='bottom' else '10');e.set(qn('w:color'),'000000');borders.append(e)
            tcPr.append(borders)
            margins=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'55');e.set(qn('w:type'),'dxa');margins.append(e)
            tcPr.append(margins)
            for p in c.paragraphs:
                p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(1);no_indent(p)
                p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:font(r,10,ri==0)
    return t

p=doc.add_paragraph(style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
font(p.add_run('杭州酒店入住率分析与预测'),16,True,'黑体')
for text in ['曹俊男','（嘉兴大学 数据科学学院）']:
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;font(p.add_run(text),10.5)
abstract=('为识别杭州酒店需求的周期差异并支持短期经营安排，本文通过官方文件下载获得2023年11月至2025年12月791条全市、10294条区县入住率观测，经缺日标记、异常识别与日期对齐，运用同比环比、K-Means聚类和SARIMA开展分析，以Python实现模板复现图、业务图及联动大屏。结果显示，2025年日均入住率为57.61%，同比提高1.91个百分点；周六高于周日9.15个百分点，淳安与桐庐对周末和季节变化较敏感。三轮28日滚动回测的RMSE为3.38个百分点、MAPE为4.93%，优于周季节朴素法，并输出未来28日点预测及95%预测区间。据此提出分时排班、淡旺季资源调整和预测偏离复核建议。')
p=para('摘要：'+abstract);p.paragraph_format.space_before=Pt(18)
para('关键词：酒店入住率；趋势对比；区县聚类；时间序列预测；Python可视化')
doc._element.body.insert(len(doc._element.body)-1,middle_break)

heading('1 引言')
heading('1.1 研究背景',2)
para('酒店客房具有明显的时间约束，当天未售出的使用机会难以留存到以后。经营者既要关心旺季能否承接需求，也要判断平日、周末和不同区县的需求是否同步变化。单看年度平均值，容易忽略某些月份的回落；直接把周末视为统一旺段，又可能掩盖周六和周日的差别。公开的日度入住率为观察这些问题提供了较细的时间尺度。')
para('杭州的住宿场景涉及城区出行、休闲度假和县域旅游等多种需求。本文不预先为区县贴上商务型或度假型标签，而是先比较实际入住率的水平、波动及周期特征。研究对象限定为来源平台“所有档次酒店”日度汇总指标，其覆盖范围不能自动扩展为全市每一家酒店、民宿和其他旅馆的完整经营台账。')
heading('1.2 研究目的',2)
para('本文围绕三个问题展开：全市入住水平在2024年至2025年间如何变化，年度改善是否均匀分布在各月；13个区县能否形成具有解释价值的市场分组；在只使用样本截止日前信息的条件下，短期预测是否优于简单的周期重复。分析最后落实到可操作的排班、促销和监测建议，不把统计相关关系写成因果结论。')
heading('1.3 研究意义',2)
para('课程项目的价值不仅在于图形数量。只有数据口径、模型参数、图表编码和文字结论能够互相核对，可视化才具有分析意义。本研究将原始文件、清洗表、模型结果和图片统一归档，并在交互大屏中保留筛选与明细导出功能，便于从结论返回观测记录。相同数据可以同时用于教材图形结构复现和业务问题讨论，二者分别计数，避免用旧作业或重复截图充抵本次成果。')
figure(17,'图1 研究技术路线')

heading('2 数据准备与预处理')
heading('2.1 数据源介绍',2)
para('主数据源为杭州文化和旅游数据在线开放平台[1]，查询入口为https://data.wgly.hangzhou.gov.cn/home/#/dataPlatform/ssDatabase。项目在2026年10月22日下载两张原始Excel文件：全市每日酒店入住率与杭州区县每日酒店入住率。平台说明其数据来自PMS、OTA等预订入住数据。本文使用的是平台已经发布的汇总结果，未获得可识别旅客身份的订单资料，也未推算酒店企业的收入或利润。')
caption('表1 原始文件与正式分析样本',True)
table(['数据表','原始记录数','分析记录数','观察单位'],[['全市入住率','822','791','城市与日期'],['区县入住率','10294','10294','区县与日期'],['预测规则日序列','派生','792','日期，含1个标记补值']], [4.3,2.3,2.3,5.9])
para('全市原始文件覆盖2023年10月1日至2025年12月31日，网页的指标说明则将起点写为2023年11月1日。为降低两种表述不一致带来的影响，正式样本统一从2023年11月1日开始，剔除10月31条全市记录。791条全市真实观测本身已经超过500条要求，预测序列中的补值不计入真实样本数量。2024年与2025年两个完整年度用于主要年度比较和区县聚类，2023年末观测用于扩展预测训练历史。')
heading('2.2 合规获取方式',2)
para('获取方式为政府文旅开放平台提供的原始文件直接下载，属于课程附件A中的政府开放数据文件方式。具体流程是在网页选择全市或区县、酒店入住率、所有档次、每日及日期范围，再依次点击下载和下载原始数据。程序只读取已经下载到本地的Excel，不使用网页解析、模拟登录或批量抓取。原件另存于data/raw，文件的SHA-256摘要记录在source_manifest.json，供后续核验。')
heading('2.3 数据来源合规声明',2)
para('根据平台服务条款[2]，相关公共数据可以免费获取并作非排他使用，不得有偿售卖；使用成果须注明“杭州文化和旅游数据在线开放平台”及下载日期，并表明分析属于个人行为。正文、README及数据说明文档保留这些信息。数据继续受来源平台协议约束，项目不将其重新声明为不受限制的开放许可。可视化及模型结果为本课程的个人研究，不代表数据发布单位的经营判断。')
heading('2.4 数据集结构与关联关系',2)
para('两张表共同包含区域、日期、指标名称、酒店档次、值和单位六个原始字段。区域、日期、指标和档次构成复合键；本次导出中指标与档次固定，检验区域和日期即可识别重复。日历字段由日期直接派生，不额外引入外部数据源。全市和区县使用同一时间窗口，但保留不同的统计总体。由于没有区县可售客房数，本文不采用13个区县入住率的简单平均替代全市官方序列。')

heading('3 数据清洗与治理')
heading('3.1 缺失异常与重复处理',2)
para('清洗首先区分“值为空”与“某一天整条记录不存在”。正式样本的入住率字段没有空值，也没有复合键重复；全市缺少2023年11月18日，上城区和临安区同日缺失，其余区县在研究窗口内日期完整。历史均值、同比和区县画像均仅根据真实观测计算，不把缺失日当成0。对月度和年度汇总同时输出实际观测天数，防止缺日问题在聚合后被掩盖。')
para('物理边界检查要求入住率位于0%至100%，全部记录通过该项检查。箱线图规则在全市标记10条、区县标记286条统计异常记录。它们可能对应真实的低谷或高峰，在没有原始订单可复核时直接删除会改变旅游需求的季节特征，故仅设置标记而不删值。异常识别用于提醒核查，不等于认定数据错误。')
heading('3.2 类型统一与指标派生',2)
para('日期统一转为日期类型，入住率保留百分数数值尺度，例如57.6表示57.6%。新增年份、月份、星期与周末标记。其中周末仅指星期六和星期日，不等同于法定节假日安排。不同年度天数不完全相同，年度入住水平采用真实日度数值的算术平均；月均值也按当月有效日期计算，不对已是比率的指标求和。')
para('时间序列模型需要规则日历。全市预测表按日补齐索引，唯一缺失日使用此前至多四个同星期日期的均值补足，并设置observed=False。该规则只查看过去，既不调用次日值，也不读取未来回测数据。补值表与真实观测表分开导出，保证论文中的样本规模和实际观测一致。')
heading('3.3 数据整合与复用',2)
para('项目将城市序列、区县序列和各自的日期派生字段分别保存，按区域与日期稳定排序。区县特征以区域为唯一键，从完整年度日度表计算，再与同一区县的年度变化结果进行一对一对齐。整个样本未做随机抽样，也未使用Faker扩充。清洗结果同时导出CSV、JSON和SQLite，字段定义、缺失日期及异常标记数量另有说明，因而其他人可以跳过Excel软件直接复算。')

heading('4 商业分析模型')
heading('4.1 模型选型及计算逻辑',2)
para('三类方法分别回答时间变化、区域差异和短期预测问题，均属于课程模型清单[7]。趋势比较采用月均值、同比、环比及周内均值；区县分群采用K-Means；预测采用SARIMA并配置周季节朴素法作为参照。数据缺少订单金额、独立顾客ID和复购记录，不适合直接构造RFM或留存同期群，选型以现有字段能够支持的业务含义为依据。')
para('设某期入住率均值为u，环比相对变化为(u本期/u上期－1)×100%，同比相对变化为(u本期/u上年同期－1)×100%。对已经用百分数表示的入住率，本文优先报告百分点差u本期－u基期，以避免混淆。例如57.61%与55.70%的差为1.91个百分点，相对增幅约3.42%。两种表述都正确，但含义不同。')
para('区县画像由四项特征组成：日均入住率、日度标准差、周末均值减去周一至周五均值、12个月平均入住率的最高值与最低值之差。先对四列做标准化，再最小化各区县到所属簇中心的平方距离之和。使用2024年至2025年完整年度，可以避免某一区县因只覆盖旺季而被误分。K-Means产生的是探索性分组，不是行政分类，也不能直接等同于酒店档次。')
para('SARIMA把日度序列中的短期相关与7日周期结合起来，记作(p,d,q)(P,D,Q)₇。其一般形式为季节与非季节滞后多项式共同作用于差分后的入住率，并由移动平均误差项解释剩余波动。statsmodels的状态空间实现可输出多步预测及相应区间[4]。周季节朴素法则重复预测原点之前最近7天的模式，提供低复杂度基准[6]。')
heading('4.2 参数与阈值设定依据',2)
para(f'聚类候选簇数为2、3、4，随机种子固定为241，每个候选重复初始化50次。13个区县的样本较小，因此要求最小簇至少包含2个区县，再按平均轮廓系数选择。最终保留{s["cluster_k"]}簇，轮廓系数为{s["silhouette"]:.3f}。轮廓系数用于判断组内紧密与组间分离程度[5]，不能解释为分类准确率。')
para('预测比较三个预先给定的低阶结构：(1,0,1)(1,0,1)₇、(1,1,1)(0,1,1)₇和(2,0,0)(1,0,0)₇。低阶候选有助于控制参数数量，7日周期来自周内经营节奏。参数仅用2025年9月11日至10月8日的28天验证集比较RMSE，选出(1,1,1)(0,1,1)₇，之后不利用测试误差反向改选。所有候选的收敛状态以及验证误差均保存为结果表。')
heading('4.3 模型验证与使用边界',2)
para('回测区间为2025年10月9日至12月31日，分成三个互不重叠的28天窗口。每轮只用该窗口之前已经发生的数据训练，并一次性预测未来28天；下一轮再向前扩展训练窗口。SARIMA和朴素法使用相同的预测原点与实际观测。误差报告RMSE、MAPE和MAE，其中RMSE、MAE的单位为百分点，MAPE为相对百分误差。')
caption('表2 三轮28日回测的合并误差',True)
table(['模型','RMSE 百分点','MAPE %','MAE 百分点'],[[r.model,f'{r.rmse:.2f}',f'{r.mape:.2f}',f'{r.mae:.2f}'] for r in metrics.itertuples()],[5.2,3.1,3.1,3.4])
para(f'SARIMA的RMSE为{s["metrics"][0]["rmse"]:.2f}个百分点，MAPE为{s["metrics"][0]["mape"]:.2f}%；周季节朴素法分别为{s["metrics"][1]["rmse"]:.2f}个百分点和{s["metrics"][1]["mape"]:.2f}%。RMSE下降约{(1-s["metrics"][0]["rmse"]/s["metrics"][1]["rmse"])*100:.1f}%，表明模型在本次留出区间有实际增益。84个回测观测全部落入95%预测区间，覆盖率为100%；这一结果也提示区间可能偏宽，不能据此宣称概率校准已经充分。')
para('聚类还做了逐一移除特征的敏感性检查。移除周末差时调整兰德指数为1.000，移除季节幅度时降至0.239，说明分组对季节特征较敏感。后续讨论保留这一限制，不把探索性分组当成稳定不变的市场事实。预测的区间属于未来观测的不确定范围，不是均值估计的置信区间；本项目用95%预测区间回应课程的区间输出要求。')

heading('5 Python数据分析与可视化')
heading('5.1 数据探索性分析',2)
para(f'2024年全市日均入住率为{s["city_2024"]:.2f}%，2025年为{s["city_2025"]:.2f}%，提高{s["year_change_pp"]:.2f}个百分点。2025年8月月均值为65.40%，1月为47.18%，两者相差18.22个百分点。全年改善并不意味着每个月都走高，2025年1月比上年同月低0.67个百分点，2月则高7.93个百分点。春节日期跨月变动可能影响月度可比性，单靠这些汇总值无法把变化全部归因于经营策略或政策。')
heading('5.2 十种模板复现及实现比较',2)
para('从教材[3]第二章的30种模板中选取10种适合入住率数据的图形，分别对应原工作表9、13、2、4、23、6、30、11、14和20。绘图保留原作的深蓝背景、标题层级、图例位置和标记形式，包括红蓝对比折线、黄色均值线、多色标注框、居中类别的蝴蝶条形、带轨道的滑珠以及渐变圆环。仅将商品、销量和年份替换为本次酒店指标，不将原 Excel 截图作为分析结果。完整作品见附录及fig01至fig10。')
para('对比柱形图、蝴蝶图和滑珠图选取淳安、建德、萧山、余杭及临安五个区县，比较同一对象的年度水平。带均值柱形图使用上城、拱墅、西湖、滨江、萧山与余杭六区，黄色线为这六个区的简单均值，不能当作全市加权入住率。标注柱形图沿用八色柱体与气泡数值框；红蓝折线比较两年上半年同月水平，柱形折线以蓝柱表示入住率、红线表示同比相对增幅，两项指标分别读取各自数值。')
para('平滑折线图采用2024年5月至2025年3月的月均值，保留橙色曲线、峰值虚线和底部年份色带，平滑只连接月度观测，不生成额外样本。单值圆环显示2025年日均入住率57.61%，剩余弧段为其100%补数。南丁格尔圆环将全年365个观测日按入住率区间分组，50%至60%的日期占46.85%，60%至70%占36.44%，50%以下与70%及以上分别占12.88%和3.84%；各组左端点计入本组、右端点计入下一组；角度表示天数占比，分层半径延续原模板。')
para('Excel通过单元格驱动图表，Python则先完成聚合计算，再按模板坐标绘制柱体、曲线与标签。本文将样式和计算分开，数据更新后可重绘全部作品。业务图采用白底与青蓝、薄荷绿、珊瑚色，图内保留坐标单位、图例和必要数值，具体方法及结果解释写入正文。所有静态图均由Matplotlib生成，PNG为220 dpi，并提供SVG。')
heading('5.3 六张业务模型图及解读',2)
para('图2将全年改善拆解为12个同月差值。2025年共有11个月高于2024年对应月份，但2月增幅显著大于其他月份，7月仅提高0.29个百分点。由此可以区分年度水平改善和个别月份的集中变化，营销复盘应同时检查同月基准与节假日错位，而不能只引用全年均值。')
figure(11,'图2 月度入住率同比变化')
para('图3揭示了周内节奏的非对称性。周六日均入住率为60.88%，周日为51.73%，两天相差9.15个百分点。把周六和周日合并后，周末均值反而比周一至周五低约0.22个百分点。周末整体指标会抵消方向不同的两种表现，统一上调周末预期可能导致周日备货偏多。误差线表示日度标准差，不作为组间显著性的证据。')
figure(12,'图3 周内入住率均值与标准差')
para('图4使用四维特征完成聚类，画面只投影平均水平与波动两个维度，因此二维距离不能代替完整的模型距离。淳安县和桐庐县组成第2组，其余11个区县为第1组。第1组内部也包含临安、富阳等较低均值区县，不能简单命名为高入住率组。分组名称宜围绕本次特征差异解释，而不预设经济功能。')
figure(13,'图4 区县入住水平与波动分群')
para('结合图5，淳安和桐庐的周末差分别为3.91和2.80个百分点，月均季节幅度分别为31.86和23.32个百分点，提示其需求对周末及月份切换更敏感。淳安的日度波动也较大，标准差为12.92个百分点。相比之下，滨江两年日均入住率为63.32%，周末差为负3.61个百分点。区域之间需要不同的监测重点，不能将全市周末均值直接套用到每个区县。')
figure(14,'图5 区县特征标准化画像')
para('图6将实际值、SARIMA预测和周期朴素法放在同一留出区间中。三轮预测原点分别位于各28日窗口之前，阴影随预测步数扩展。模型减少了机械重复上一周造成的偏差，但仍会遗漏突发活动等外生影响。误差表与图形共同使用，比只看训练期拟合曲线更能说明预测是否有效。')
figure(15,'图6 三轮28日滚动回测')
para(f'图7展示以2025年12月31日为原点、对2026年1月1日至28日的样本外预测。28天点预测均值为{s["forecast_average"]:.2f}%。预测原点固定为2025年末，不是当前的实时经营预报；本文没有取得该28天的实际值用于再次评分。区间没有在图中被人为压窄，经营者应同时关注中心估计与不确定范围。')
figure(16,'图7 2026年1月1日至28日入住率预测')
heading('5.4 交互式可视化大屏',2)
para('大屏由Python调用Pyecharts生成，使用本地ECharts资源运行，无需联网加载图表库。日期、年份快捷按钮和区县筛选共同控制KPI、日度趋势、月均柱形、周内结构、区域比较、波动散点和观测明细，超过6个联动组件。点击区域柱条或散点会更新分析范围，筛选结果可导出为CSV。固定历史原点的预测图单独标注范围，不随筛选伪装成重新训练的结果。')
para('界面采用浅色画布和青蓝主色，数值使用等宽数字排布，珊瑚色只强调当前选区。与教材深色复现图相比，大屏更重视观察顺序和交互反馈。顶部先给出当前范围与指标，中部展示趋势和区域差异，底部提供明细。用户可以从某一异常月份缩小日期范围，再检查具体区县和观测日，完成由总览到细节的验证。图8为可运行界面的演示截图。')
screen=ROOT/'outputs/dashboard/大屏演示.png'
if screen.exists():
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;no_indent(p)
    p.paragraph_format.keep_with_next=True;p.paragraph_format.line_spacing=1.0
    p.add_run().add_picture(str(screen),width=Cm(12.2))
    caption('图8 杭州酒店入住率交互大屏图表区域')

heading('6 商业案例分析')
heading('6.1 案例背景',2)
para('设定的应用场景是住宿经营者需要为下一阶段安排前台、保洁、餐饮配套及营销资源。本文不掌握单家酒店的可售房数、取消率与客单价，无法给出精确的人数排班或定价金额。案例据公开的入住率变化提供需求监测方向，实际执行前还需与酒店自身的订单、成本和渠道数据结合。')
heading('6.2 结果解读',2)
para('全市2025年的平均水平有所提高，但各区县改善幅度并不一致。淳安提高4.49个百分点，萧山提高3.94个百分点，临安降低0.52个百分点。这些差异与周期特征一起说明，区域经营复盘应观察长期水平和短期波动两个方面。单凭入住率不能判定收益改善，因为低价促销也可能带来更高入住；本文没有收入指标，故不推断利润增长。')
para('分群刻画区域间的需求差异，预测描述全市未来数周的变化，两者分别服务于区域经营复盘与短期资源安排。本文未将聚类标签作为SARIMA的解释变量，因此不据此推断区域特征对全市入住率的因果影响。')
heading('6.3 商业建议',2)
para('第一，按具体星期安排服务弹性。周六与周日均值相差9.15个百分点，宜分别设定人员备班与采购检查点，不将整个周末套用同一档位。建议酒店先以自身近四周同星期订单验证这一方向，再决定是否调整班次；公开市级均值只提供外部参照。')
para('第二，对周末及季节敏感区县加强淡旺转换监测。淳安与桐庐的季节幅度较高，可以在月底结合下一月预订情况复核房态和可变服务投入。2025年全市8月至9月月均值下降8.82个百分点，暑期结束时尤其需要检查需求回落，避免将旺季安排机械延续。')
para('第三，用同月与同星期基准复盘促销。年度提升1.91个百分点不意味着每个月改善同样大，2月同比变化还受节假日日期影响。复盘表应同时列出入住率、基期值和百分点差，若能取得酒店自身房价，再补充收益指标，防止仅以入住率追求规模。')
para('第四，采用预测区间设置复核机制。SARIMA的回测RMSE约3.38个百分点，可作为理解常见点预测误差量级的参考，不能直接当成保证误差上限。若新观测持续偏离预测区间，或出现会展、极端天气等事件，应先检查输入数据与外生条件，再更新模型。95%区间的回测覆盖率达到100%，也值得继续关注区间是否过宽。')
para('第五，将临安等未同步改善的区县列为进一步调查对象。临安年度变化为负0.52个百分点，本文只能确定现象，尚不能区分供给增加、客群变化或数据覆盖调整。后续可用同一平台允许下载的客流、酒店档次指标进行关联核验，数据不足时不据此评价某一家酒店的经营能力。')

heading('7 结论与展望')
heading('7.1 研究结论',2)
para('本文完成了从公开文件核验、数据治理到三类模型分析和Python可视化的完整流程。791条全市真实观测与10294条区县观测支撑了时间和空间两个层面的比较。2025年全市日均入住水平较2024年提高，改善分布却存在明显月度差异；周六与周日的反向表现使合并周末指标失去部分解释力。区县分群提示淳安与桐庐具有较突出的周末及季节特征。')
para('三轮28日回测显示，SARIMA在本次测试区间优于周季节朴素法。项目另外生成10种教材格式图、6张业务模型图和交互大屏，图表数据来自同一清洗与计算过程，能够按脚本复现。可视化不仅用于陈列结果，也帮助识别年度平均值、周末均值和地区均值可能隐藏的信息。')
heading('7.2 局限性与展望',2)
para('来源平台没有在本次导出中提供酒店样本数、可售房数及覆盖率，研究结果应限定为平台发布的酒店汇总口径。日度序列缺少个别观测，聚类只有13个区县且对季节幅度敏感，探索性分组还需更多年份验证。模型未显式加入节假日、会展、房价、天气或供给变化，全年长周期只通过历史信息间接体现，跨节假日外推尤其需要谨慎。')
para('研究窗口截至2025年末，因此2026年1月的预测应被理解为历史样本外案例。后续若取得同口径实际值，可继续检验误差和区间覆盖；若补齐酒店客房容量，则能讨论更合适的区域加权和收益指标。在此之前，本文将描述性结论、预测结果与待验证解释分别呈现。')
heading('7.3 AI使用披露',2)
para('本项目使用OpenAI Codex进行AI辅助工作，涵盖要求拆解、数据来源检索与下载操作辅助、Python脚本和论文初稿生成、可视化排版及语言润色。关键提示包括使用杭州真实住宿数据，分别完成10种模板图、6张业务模型图和1个联动大屏，预测须包含95%区间与回测，以及文字逻辑通畅、句式和关联表达避免机械重复。')
para('数据文件经实际读取，样本数量、日期范围与缺失项均由程序核验，模型误差来自已运行的回测，未以AI生成数值替代观测。AI也参与了正文草拟，不能将其使用范围仅表述为检查错别字。作者应在提交前理解代码、核对结论与课程要求，并对最终提交版本负责。')

heading('参考文献')
refs=[
'[1] 杭州文化和旅游数据在线开放平台. 实时旅游数据[DB/OL]. [2026-10-22]. https://data.wgly.hangzhou.gov.cn/home/#/dataPlatform/ssDatabase.',
'[2] 杭州文化和旅游数据在线开放平台. 服务条款[EB/OL]. [2026-10-22]. https://data.wgly.hangzhou.gov.cn/home/ToS.pdf.',
'[3] 郭宏远. Excel数据可视化 从图表到数据大屏[M]. 北京：清华大学出版社, 2023.',
'[4] statsmodels developers. SARIMAXResults.get_forecast[EB/OL]. [2026-10-22]. https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAXResults.get_forecast.html.',
'[5] scikit-learn developers. Selecting the number of clusters with silhouette analysis on KMeans clustering[EB/OL]. [2026-10-22]. https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html.',
'[6] HYNDMAN R J, ATHANASOPOULOS G. Forecasting Principles and Practice[M/OL]. 3rd ed. Melbourne: OTexts, 2021. [2026-10-22]. https://otexts.com/fpp3/toolbox.html.',
'[7] 商业数据分析课程. 期末大作业要求及评分标准 2026年秋季学期[Z]. 2026. 课程提供的原始文件.'
]
for r in refs:
    p=para(r);p.paragraph_format.first_line_indent=Pt(0)
    for run in p.runs:font(run,10)

heading('附录')
heading('A 核心代码片段',2)
para('以下为SARIMA核心代码，完整程序及一键入口见仓库。')
code='model = SARIMAX(history, order=(1, 1, 1),\n    seasonal_order=(0, 1, 1, 7)).fit(disp=False)\nforecast = model.get_forecast(steps=28)\ninterval = forecast.conf_int(alpha=0.05)'
p=doc.add_paragraph();no_indent(p)
p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.1
p.paragraph_format.keep_together=True
font(p.add_run(code),8.5,name='Consolas')
heading('B 项目仓库与目录结构',2)
para('公开仓库：https://github.com/YDZ-R/CDA-homework。data保存原始及清洗数据，scripts保存代码，outputs保存图表与离线大屏，docs保存论文。安装requirements.txt后运行python run_all.py即可复现。')
heading('C 图表索引与模板缩览',2)
caption('表3 独立图表作品索引',True)
table(['文件号','类型','图表名称'],[[r.number,r.category,r.name] for r in index.itertuples()],[2.0,3.0,9.8])
para('fig01至fig10为模板复现，fig11至fig16为业务模型图，fig17为研究流程。以下附10张模板作品，完整PNG与SVG文件见outputs/figures。')
heading('模板复现作品',2)
for num in range(1,11):
    record=index.iloc[num-1]
    figure(num,f'{record["number"]} {record["name"]}（{record["template"]}）',width=13.7)

doc.core_properties.author='曹俊男'
doc.core_properties.title='杭州酒店入住率分析与预测'
doc.core_properties.subject='商业数据分析期末课程项目'
doc.core_properties.keywords='酒店入住率；趋势对比；区县聚类；时间序列预测；Python可视化'
doc.settings.element.append(OxmlElement('w:updateFields'))
doc.settings.element[-1].set(qn('w:val'),'true')
target=ROOT/'docs/杭州酒店入住率分析与预测.docx'
doc.save(target)
# Restore untouched package parts byte-for-byte, including their XML declarations.
with zipfile.ZipFile(template) as source,zipfile.ZipFile(target) as built:
    keep={n:source.read(n) for n in source.namelist() if n.startswith(('word/header','word/footer','word/media/'))}
    temporary=target.with_suffix('.preserved.docx')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as out:
        for info in built.infolist():out.writestr(info,keep.get(info.filename,built.read(info.filename)))
temporary.replace(target)
text='\n\n'.join(article)
(ROOT/'docs/论文正文.md').write_text(text,encoding='utf-8')
meta=dict(chinese_characters=len(re.findall('[\u4e00-\u9fff]',text)),abstract_characters=len(abstract),
          template_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),template_sections=3,
          final_sections=len(doc.sections),figures=17,author='曹俊男',student_id='2024459985112')
(TABLES/'paper_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
assert 200<=len(abstract)<=300
assert meta['chinese_characters']>=3000
print('论文已生成：',target,'；正文与附录汉字',meta['chinese_characters'],'；摘要',len(abstract))
