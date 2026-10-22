"""Validate the two official, manually downloaded Excel files and record hashes."""
import hashlib
import pandas as pd
from common import RAW, TABLES, dump

manifest = []
for name in ['city_daily.xlsx', 'district_daily.xlsx']:
    path = RAW / name
    if not path.exists():
        raise FileNotFoundError(f'缺少官方下载文件：{path}')
    frame = pd.read_excel(path)
    assert list(frame.columns) == ['区域', '日期', '指标名称', '酒店档次', '值', '单位']
    assert frame['指标名称'].eq('酒店入住率').all()
    assert frame['酒店档次'].eq('所有档次').all()
    manifest.append(dict(file=name, rows=len(frame), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         downloaded='2026-10-22', source='杭州文化和旅游数据在线开放平台',
                         url='https://data.wgly.hangzhou.gov.cn/home/#/dataPlatform/ssDatabase',
                         method='网页查询后点击下载原始数据；未使用爬虫'))
dump(manifest, TABLES / 'source_manifest.json')
print('已核验原始文件：', [(x['file'], x['rows']) for x in manifest])
