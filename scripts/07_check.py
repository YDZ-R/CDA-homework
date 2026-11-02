"""Small, independent checks for data integrity, forecasts and deliverable coverage."""
import json
import re
import sqlite3
import zipfile
import numpy as np
import pandas as pd
from PIL import Image
from docx import Document
from docx.oxml.ns import qn
from common import ROOT, CLEAN, TABLES, FIGURES

city=pd.read_csv(CLEAN/'city_daily.csv')
district=pd.read_csv(CLEAN/'district_daily.csv')
assert len(city)==791 and len(district)==10294
assert not city.duplicated(['area','date']).any()
assert not district.duplicated(['area','date']).any()
assert city.occupancy.between(0,100).all() and district.occupancy.between(0,100).all()
assert district.area.nunique()==13
summary=json.loads((TABLES/'analysis_summary.json').read_text(encoding='utf-8'))
assert np.isclose(city.loc[city.year.eq(2025),'occupancy'].mean(),summary['city_2025'])
bt=pd.read_csv(TABLES/'forecast_backtest.csv')
assert len(bt)==84 and bt.date.nunique()==84 and bt.groupby('fold').size().eq(28).all()
assert (pd.to_datetime(bt.origin)<pd.to_datetime(bt.date)).all()
assert (bt.lower<=bt.prediction).all() and (bt.prediction<=bt.upper).all()
assert np.isclose(np.sqrt(((bt.actual-bt.prediction)**2).mean()),summary['metrics'][0]['rmse'])
future=pd.read_csv(TABLES/'forecast_2026_january.csv')
assert len(future)==28 and future.date.iloc[0]=='2026-01-01' and future.date.iloc[-1]=='2026-01-28'
idx=pd.read_csv(TABLES/'figure_index.csv')
assert (idx.category=='模板复现').sum()==10 and (idx.category=='业务模型').sum()==6
assert idx[idx.category=='模板复现'].template.nunique()==10
assert idx.iloc[:10].template.str.extract(r'第二章(\d+)')[0].astype(int).tolist()==[9,13,2,4,23,6,30,11,14,20]
for file in idx.file:
    image=Image.open(FIGURES/file)
    assert min(image.info['dpi'])>=150
    assert (FIGURES/file).with_suffix('.svg').exists()
    svg=(FIGURES/file).with_suffix('.svg').read_text(encoding='utf-8')
    assert '数据：杭州文化和旅游' not in svg and '来源：杭州' not in svg
with sqlite3.connect(CLEAN/'accommodation.sqlite') as conn:
    assert conn.execute('select count(*) from city_daily').fetchone()[0]==len(city)
paper_meta=json.loads((TABLES/'paper_metadata.json').read_text(encoding='utf-8'))
paper=ROOT/'docs'/paper_meta['paper_file']
doc=Document(paper)
text='\n'.join(p.text for p in doc.paragraphs)+'\n'+'\n'.join(c.text for t in doc.tables for row in t.rows for c in row.cells)
assert len(re.findall('[\u4e00-\u9fff]',text))>3000
assert '曹俊男' in text and '2024459985112' in text
assert len(doc.sections)==3 and '关键词：酒店入住率；' in text
assert '注意：全文红色字体' not in text and '论文题目（三黑' not in text
assert len(doc.inline_shapes)>=19 # retained university logo plus 18 authored pictures
abstract=next(p.text.removeprefix('摘要：') for p in doc.paragraphs if p.text.startswith('摘要：'))
assert 200<=len(abstract)<=300
# The cover scoring form is retained; only the three authored data tables use three rules.
assert len(doc.tables)==5
cover=doc.tables[0]
assert len(cover.rows)==6
assert all(row.cells[1].width==cover.rows[0].cells[1].width for row in cover.rows)
assert all(row.cells[1].paragraphs[0].alignment==1 for row in cover.rows)
for table in doc.tables[2:]:
    for ri,row in enumerate(table.rows):
        for cell in row.cells:
            borders=cell._tc.get_or_add_tcPr().find(qn('w:tcBorders'))
            for edge in ['top','bottom','left','right']:
                actual=borders.find(qn('w:'+edge)).get(qn('w:val'))
                visible=(ri==0 and edge in ('top','bottom')) or (ri==len(table.rows)-1 and edge=='bottom')
                assert actual==('single' if visible else 'nil')
html=(ROOT/'outputs/dashboard/index.html').read_text(encoding='utf-8')
assert 'assets/echarts.min.js' in html and '__DATA__' not in html
assert (ROOT/'outputs/dashboard/assets/echarts.min.js').stat().st_size>500000
with zipfile.ZipFile(ROOT/'docs/学校论文模板.docx') as a,zipfile.ZipFile(paper) as b:
    preserved=[n for n in a.namelist() if n.startswith(('word/header','word/footer','word/media/'))]
    assert all(a.read(n)==b.read(n) for n in preserved), '源模板页眉页脚或校徽发生变化'
report=dict(data='通过',forecast='通过',figures='10模板+6业务+1流程',paper='通过',
            template_preserved_parts=preserved,dashboard='静态检查通过，浏览器联动另经实际测试')
(TABLES/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('数据、回测、图表数量、分辨率、论文与模板保留检查全部通过。')
