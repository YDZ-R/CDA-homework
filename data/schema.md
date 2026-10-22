# 数据字段

`city_daily`与`district_daily`复合键为`area,date,indicator,grade`。本次指标和档次固定，`area,date`同样唯一。

|字段|类型|含义|
|---|---|---|
|area|字符串|杭州或13个区县|
|date|日期|观测日期|
|indicator|字符串|酒店入住率|
|grade|字符串|所有档次|
|occupancy|浮点数|百分数尺度，例如57.6代表57.6%|
|unit|字符串|原始单位％|
|year、month、weekday|整数|由日期派生，weekday的0为周一|
|weekend|布尔|星期六或日，不代表法定节假日|
|iqr_flag|布尔|超出本区域IQR规则边界，仅标记不删除|

`city_forecast_series`有date、occupancy和observed三列。792个规则日历日期中791个真实观测，1个按过去同星期均值补足。历史描述统计使用未补值的主表。

区县特征表以area为唯一键；无酒店级、订单级或旅客级主键。不存在可用于全市区域加权的客房容量字段。
