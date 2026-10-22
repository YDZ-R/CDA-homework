"""Three methods: period comparison, K-means segmentation, SARIMA forecasting."""
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from statsmodels.tsa.statespace.sarimax import SARIMAX
from common import CLEAN, TABLES, SEED, city_data, district_data, save_table, dump

city, district = city_data(), district_data()
monthly = city['occupancy'].resample('MS').agg(['mean','count']).rename(columns={'mean':'occupancy','count':'observed_days'})
monthly['mom_pp'] = monthly['occupancy'].diff()
monthly['mom_pct'] = monthly['occupancy'].pct_change(fill_method=None)*100
monthly['yoy_pp'] = monthly['occupancy'].diff(12)
monthly['yoy_pct'] = monthly['occupancy'].pct_change(12, fill_method=None)*100
save_table(monthly, 'monthly_comparison', True)
yearly = city.groupby('year')['occupancy'].agg(['mean','std','min','max','count'])
save_table(yearly, 'yearly_summary', True)
weekday = city.groupby('weekday')['occupancy'].agg(['mean','std','count'])
save_table(weekday, 'weekday_summary', True)
district_year = district[district['year'].isin([2024,2025])].groupby(['area','year'])['occupancy'].mean().unstack()
district_year['change_pp'] = district_year[2025]-district_year[2024]
save_table(district_year, 'district_year', True)

# Compare complete calendar years only, so all districts use the same window.
part = district[district['year'].isin([2024,2025])].copy()
features = part.groupby('area')['occupancy'].agg(mean='mean', volatility='std')
w = part.groupby(['area','weekend'])['occupancy'].mean().unstack()
features['weekend_gap'] = w[True]-w[False]
m = part.groupby(['area','month'])['occupancy'].mean().unstack()
features['seasonal_range'] = m.max(axis=1)-m.min(axis=1)
X = StandardScaler().fit_transform(features)
candidates, fitted = [], {}
for k in [2,3,4]:
    model = KMeans(n_clusters=k, random_state=SEED, n_init=50).fit(X)
    fitted[k] = model
    candidates.append(dict(k=k,silhouette=float(silhouette_score(X,model.labels_)),
                           smallest_group=int(np.bincount(model.labels_).min())))
valid = [x for x in candidates if x['smallest_group']>=2]
chosen = max(valid, key=lambda x:x['silhouette'])['k']
labels = fitted[chosen].labels_
means = {i:features.iloc[np.where(labels==i)[0]]['mean'].mean() for i in set(labels)}
order = {old:i+1 for i,(old,_) in enumerate(sorted(means.items(), key=lambda x:x[1], reverse=True))}
features['cluster'] = [order[x] for x in labels]
features['change_pp'] = district_year['change_pp']
save_table(features, 'district_features', True)
save_table(pd.DataFrame(candidates), 'cluster_selection')
# A modest sensitivity check; the sample consists of only 13 districts.
stability=[]
for j in range(4):
    labs = KMeans(n_clusters=chosen,random_state=SEED,n_init=50).fit_predict(np.delete(X,j,axis=1))
    stability.append(dict(omitted_feature=features.columns[j],ari=float(adjusted_rand_score(labels,labs))))
save_table(pd.DataFrame(stability), 'cluster_sensitivity')

y = pd.read_csv(CLEAN/'city_forecast_series.csv', parse_dates=['date']).set_index('date')['occupancy'].asfreq('D')
# 28-day validation and 3 non-overlapping 28-day backtests. Test values do not select parameters.
test_start = len(y)-84
train, validation = y.iloc[:test_start-28], y.iloc[test_start-28:test_start]
specs = [((1,0,1),(1,0,1,7)), ((1,1,1),(0,1,1,7)), ((2,0,0),(1,0,0,7))]
def fit(series, spec):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return SARIMAX(series, order=spec[0],seasonal_order=spec[1],trend='c' if spec[0][1]==0 else 'n',
                       enforce_stationarity=True,enforce_invertibility=True).fit(disp=False,maxiter=160)
def metrics(actual,pred):
    a,p=np.asarray(actual),np.asarray(pred)
    return dict(rmse=float(np.sqrt(np.mean((a-p)**2))),mape=float(np.mean(abs((a-p)/a))*100),mae=float(np.mean(abs(a-p))))
selection=[]
for i,spec in enumerate(specs):
    result=fit(train,spec)
    selection.append(dict(candidate=i,order=str(spec[0]),seasonal_order=str(spec[1]),
                          converged=bool(result.mle_retvals.get('converged',False)),
                          **metrics(validation,result.forecast(28))))
eligible=[r for r in selection if r['converged']]
assert eligible, '候选SARIMA均未收敛，需调整模型'
best=min(eligible,key=lambda r:r['rmse'])['candidate']
spec=specs[best]
save_table(pd.DataFrame(selection),'forecast_validation')
preds=[]; model_fits=[]
for fold in range(3):
    pos=test_start+fold*28
    history=y.iloc[:pos]; actual=y.iloc[pos:pos+28]
    model=fit(history,spec); model_fits.append(bool(model.mle_retvals.get('converged',False)))
    fc=model.get_forecast(28); ci=fc.conf_int(alpha=.05)
    naive=np.resize(history.iloc[-7:].to_numpy(),28)
    for i,date in enumerate(actual.index):
        preds.append(dict(date=str(date.date()),fold=fold+1,actual=float(actual.iloc[i]),
                          prediction=float(fc.predicted_mean.iloc[i]),lower=float(ci.iloc[i,0]),upper=float(ci.iloc[i,1]),
                          weekly_naive=float(naive[i]),origin=str(history.index[-1].date())))
backtest=pd.DataFrame(preds)
assert model_fits==[True,True,True], '回测模型未收敛'
save_table(backtest,'forecast_backtest')
scores=[]
for name,col in [('SARIMA','prediction'),('周季节朴素法','weekly_naive')]:
    scores.append(dict(model=name,**metrics(backtest.actual,backtest[col])))
save_table(pd.DataFrame(scores),'forecast_metrics')
final=fit(y,spec); assert final.mle_retvals.get('converged',False)
fc=final.get_forecast(28); ci=fc.conf_int(alpha=.05)
future=pd.DataFrame({'date':fc.predicted_mean.index.strftime('%Y-%m-%d'),'prediction':fc.predicted_mean.values,
                     'lower':ci.iloc[:,0].values,'upper':ci.iloc[:,1].values})
save_table(future,'forecast_2026_january')
coverage=float(((backtest.actual>=backtest.lower)&(backtest.actual<=backtest.upper)).mean())
summary=dict(city_rows=len(city),district_rows=len(district),city_2024=float(yearly.loc[2024,'mean']),
             city_2025=float(yearly.loc[2025,'mean']),year_change_pp=float(yearly.loc[2025,'mean']-yearly.loc[2024,'mean']),
             best_month_2025=str(monthly.loc['2025','occupancy'].idxmax().date()),
             worst_month_2025=str(monthly.loc['2025','occupancy'].idxmin().date()),
             weekend_gap=float(city[city.weekend]['occupancy'].mean()-city[~city.weekend]['occupancy'].mean()),
             cluster_k=chosen,silhouette=float(next(r['silhouette'] for r in candidates if r['k']==chosen)),
             spec=[list(spec[0]),list(spec[1])], validation_start=str(validation.index[0].date()),
             test_start=str(backtest.date.min()),test_end=str(backtest.date.max()),
             coverage_95=coverage,metrics=scores,forecast_average=float(future.prediction.mean()),
             forecast_origin='2025-12-31',forecast_end=str(future.date.iloc[-1]),
             cluster_sensitivity=stability)
dump(summary,TABLES/'analysis_summary.json')
print(json.dumps(summary,ensure_ascii=False,indent=2))
