"""Keep observed values intact; create a separately flagged forecast series."""
import sqlite3
import numpy as np
import pandas as pd
from common import RAW, CLEAN, TABLES, START, END, dump, save_table

rename = {'区域':'area','日期':'date','指标名称':'indicator','酒店档次':'grade','值':'occupancy','单位':'unit'}
audit = {}
for kind in ['city', 'district']:
    raw = pd.read_excel(RAW / f'{kind}_daily.xlsx').rename(columns=rename)
    raw['date'] = pd.to_datetime(raw['date'], errors='raise')
    raw['occupancy'] = pd.to_numeric(raw['occupancy'], errors='raise')
    data = raw[raw['date'].between(START, END)].copy()
    assert not data.duplicated(['area','date','indicator','grade']).any(), '主键重复，需人工核对'
    assert data['occupancy'].between(0, 100).all(), '入住率超出物理范围'
    assert data['occupancy'].notna().all()
    data = data.sort_values(['date','area'])
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['weekday'] = data['date'].dt.dayofweek
    data['weekend'] = data['weekday'].ge(5)
    # Statistical outliers can be genuine holiday peaks; flag instead of deleting.
    q1 = data.groupby('area')['occupancy'].transform(lambda x:x.quantile(.25))
    q3 = data.groupby('area')['occupancy'].transform(lambda x:x.quantile(.75))
    data['iqr_flag'] = (data['occupancy'] < q1-1.5*(q3-q1)) | (data['occupancy'] > q3+1.5*(q3-q1))
    missing = []
    dates = pd.date_range(START, END)
    for area, group in data.groupby('area'):
        for date in dates.difference(group['date']):
            missing.append(dict(area=area,date=str(date.date())))
    audit[kind] = dict(raw_rows=len(raw), kept_rows=len(data), excluded_before_start=len(raw)-len(data),
                       areas=data['area'].nunique(), duplicate_rows=0, missing_values=0,
                       missing_keys=missing, statistical_flags=int(data['iqr_flag'].sum()))
    data.to_csv(CLEAN / f'{kind}_daily.csv', index=False, encoding='utf-8-sig')
    data.to_json(CLEAN / f'{kind}_daily.json', orient='records', date_format='iso', force_ascii=False)
    with sqlite3.connect(CLEAN / 'accommodation.sqlite') as conn:
        data.to_sql(f'{kind}_daily', conn, if_exists='replace', index=False)
    if kind == 'city':
        series = data.set_index('date')['occupancy'].asfreq('D')
        observed = series.notna()
        # A causal fallback never looks into a future test day.
        for idx in series[series.isna()].index:
            candidates = [series.get(idx-pd.Timedelta(days=7*k), np.nan) for k in range(1,5)]
            values = [v for v in candidates if pd.notna(v)]
            series.loc[idx] = np.mean(values) if values else series.loc[:idx].ffill().iloc[-1]
        assert series.notna().all()
        forecast = pd.DataFrame({'occupancy':series,'observed':observed})
        forecast.to_csv(CLEAN / 'city_forecast_series.csv', encoding='utf-8-sig', index_label='date')
assert audit['city']['kept_rows'] >= 500
dump(audit, TABLES / 'cleaning_audit.json')
print('清洗完成：', {k:v['kept_rows'] for k,v in audit.items()})
