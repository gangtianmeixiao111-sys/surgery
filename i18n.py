"""Complete interface translations; original category codes stay unchanged."""
TEXT = {
 'zh': {
 'title':'风险预测','language':'界面语言','patient':'患者参数','patient_hint':'填写当前患者指标，结果实时更新。',
 'notice':'仅用于教学演示，不能用于真实患者诊疗。','research':'研究模型，请结合适用人群与验证结果使用。',
 'nomogram':'动态列线图','graphical':'图形摘要','numerical':'数值摘要','model':'模型摘要',
 'risk':'预测概率','ci':'95%置信区间','total':'列线图总分','event':'目标结局','outcome':'AKI发生概率',
 'reset':'恢复默认值','precision':'小数位设置','precision_mode':'精度来源','source':'按数据表','custom':'逐项设置',
 'precision_hint':'逐项调整输入精度，输入框、滑块与结果保持同步。','digits':'小数位',
 'precision_help':'数据表已有 {n} 位小数；可增加至10位。','rounded':'已按当前精度保留 {n} 位小数：{value}',
 'range':'建模数据覆盖：{low}–{high}；步长：{step}。','nomogram_hint':'分布轮廓展示建模样本；红点与引导线对应当前患者。',
 'points':'分值','total_points':'总分','value':'当前值','density':'样本分布','reference':'中位数与四分位距',
 'no_distribution':'当前文件缺少分布摘要，请使用新版R导出器重新生成。',
 'graph_hint':'查看当前预测及参数不确定性。','ci_note':'置信区间反映模型参数不确定性。',
 'lower':'区间下限','upper':'区间上限','estimate':'预测值','probability':'概率','parameters':'当前患者参数',
 'results':'预测结果','parameter':'参数','unit':'单位','lp':'线性预测值','se':'标准误',
 'coefficients':'回归系数','term':'模型项','coefficient':'系数','coef_lower':'系数区间下限','coef_upper':'系数区间上限',
 'definition':'输入定义','range_code':'范围 / 编码','step':'步长','decimals':'小数位','timing':'时点与说明',
 'model_type':'二分类Logistic回归','samples':'建模样本','events':'事件数','predictors':'预测变量','coding':'目标事件编码为1',
 'categorical':'分类选择','none':'无','unknown':'未提供','download':'下载当前结果','more':'模型与预测说明',
 'model_note':'模型参数由R拟合导出；网页按同一组系数计算。','score_note':'列线图直接使用R美化版图形与计分方式，红点随当前输入更新。',
 'footer':'小红书：思绪随风 · 6739802809','load_error':'无法读取模型文件，请确认文件完整。',
 'prediction_error':'无法计算，请检查输入范围和模型文件。','slider':'滑块','number_type':'连续变量','factor_type':'分类变量',
 'regression':'模型信息','risk_axis':'AKI发生概率','model_scope':'输入范围来自本次拟合样本。',
 },
 'en': {
 'title':'Risk prediction','language':'Interface language','patient':'Patient inputs','patient_hint':'Enter patient measurements. Results update instantly.',
 'notice':'For teaching demonstrations only. Not for patient care.','research':'Research model. Check the intended population and validation evidence.',
 'nomogram':'Dynamic nomogram','graphical':'Graphical summary','numerical':'Numerical summary','model':'Model summary',
 'risk':'Predicted probability','ci':'95% confidence interval','total':'Total nomogram points','event':'Target outcome','outcome':'Probability of AKI',
 'reset':'Reset inputs','precision':'Decimal settings','precision_mode':'Precision source','source':'From data','custom':'Per variable',
 'precision_hint':'Set precision per variable. Inputs, sliders and results stay in sync.','digits':'Decimal places',
 'precision_help':'The data use {n} decimal places. Increase up to 10.','rounded':'Rounded to {n} decimal places: {value}',
 'range':'Modeling range: {low}–{high}; step: {step}.','nomogram_hint':'Distributions describe the modeling sample. Red markers and guides show this patient.',
 'points':'Points','total_points':'Total points','value':'Current value','density':'Sample distribution','reference':'Median and interquartile range',
 'no_distribution':'Distribution summaries are missing. Regenerate this app with the updated R exporter.',
 'graph_hint':'Inspect the estimate and its parameter uncertainty.','ci_note':'The interval reflects model parameter uncertainty.',
 'lower':'Lower limit','upper':'Upper limit','estimate':'Estimate','probability':'Probability','parameters':'Current patient inputs',
 'results':'Prediction results','parameter':'Parameter','unit':'Unit','lp':'Linear predictor','se':'Standard error',
 'coefficients':'Regression coefficients','term':'Model term','coefficient':'Coefficient','coef_lower':'Lower coefficient limit','coef_upper':'Upper coefficient limit',
 'definition':'Input definitions','range_code':'Range / code','step':'Step','decimals':'Decimals','timing':'Timing and definition',
 'model_type':'Binary logistic regression','samples':'Modeling sample','events':'Events','predictors':'Predictors','coding':'Target event is coded as 1',
 'categorical':'Category','none':'None','unknown':'Not supplied','download':'Download current results','more':'About this prediction',
 'model_note':'Parameters were fitted in R. This app uses the same coefficients.','score_note':'The nomogram uses the original R drawing and point scale. Red markers update with the current inputs.',
 'footer':'Rednote: si_xu_sui_feng · 6739802809','load_error':'Cannot read the model. Check that all application files are present.',
 'prediction_error':'Cannot calculate. Check the input ranges and model files.','slider':'Slider','number_type':'Continuous','factor_type':'Categorical',
 'regression':'Model information','risk_axis':'Probability of AKI','model_scope':'Input ranges come from the fitted modeling sample.',
 }
}

# name: English label, concise Chinese help, concise English help
FIELDS = {
 'Age':('Age','预测时点的年龄；','Age at the prediction time;'),
 'BMI':('Body mass index','预测时点的体重指数；','Body mass index at prediction;'),
 'Baseline_Creatinine':('Baseline creatinine','预测时点前可获得的基线肌酐；','Baseline creatinine available before prediction;'),
 'Admission_Lactate':('Admission lactate','入科预测时点的乳酸；','Lactate at ICU admission;'),
 'Admission_MAP':('Admission mean arterial pressure','入科预测时点的平均动脉压；','Mean arterial pressure at ICU admission;'),
 'Preop_Hemoglobin':('Preoperative hemoglobin','术前评估时点的血红蛋白；','Hemoglobin at preoperative assessment;'),
 'Preop_Albumin':('Preoperative albumin','术前评估时点的白蛋白；','Albumin at preoperative assessment;'),
 'Planned_Duration':('Planned procedure duration','术前预计的手术时长；','Planned procedure duration, known before surgery;'),
 'Admission_Albumin':('Admission albumin','入院预测时点的白蛋白；','Albumin at hospital admission;'),
 'Admission_Sodium':('Admission sodium','入院预测时点的血钠；','Sodium at hospital admission;'),
 'Admission_Hemoglobin':('Admission hemoglobin','入院预测时点的血红蛋白；','Hemoglobin at hospital admission;'),
 'Sex':('Sex','预测时点记录的性别。','Recorded sex at prediction.'),
 'Diabetes':('Diabetes history','预测时点已知的糖尿病病史。','Diabetes history known at prediction.'),
 'Vasopressor_At_Admission':('Vasopressor at admission','入科预测时点是否使用升压药。','Vasopressor use at ICU admission.'),
 'Admission_Source':('Admission source','进入ICU时的来源。','Source of admission to the ICU.'),
 'Urgent_Admission':('Urgent admission','本次是否为急诊入院。','Whether this admission was urgent.'),
 'Site':('Study center','本次住院所属研究中心。','Study center for this admission.'),
}
LEVELS = {
 'Sex':{'F':('女','Female'),'M':('男','Male')},
 'Diabetes':{'0':('无','No'),'1':('有','Yes')},
 'Vasopressor_At_Admission':{'0':('否','No'),'1':('是','Yes')},
 'Urgent_Admission':{'0':('否','No'),'1':('是','Yes')},
 'Admission_Source':{'ED':('急诊','Emergency'),'Ward':('病房','Ward'),'Postop':('术后','Postoperative')},
 'Site':{c:(f'中心{c}',f'Center {c}') for c in 'ABCD'},
}

def label(field, lang):
    return field.get('label_zh',field['label']) if lang=='zh' else field.get('label_en',FIELDS.get(field['name'],(field['name'].replace('_',' '),))[0])

def level_label(field, value, lang):
    code=str(value)
    if field['name'] in LEVELS and code in LEVELS[field['name']]:
        return LEVELS[field['name']][code][0 if lang=='zh' else 1]
    item=next(x for x in field['levels'] if str(x['value'])==code)
    return item.get('label_'+lang,item['label'] if lang=='zh' else code)

def help_note(field,lang):
    if field['name'] in FIELDS: return FIELDS[field['name']][1 if lang=='zh' else 2]
    return field.get('clinical_note_'+lang,'')

def value_text(field,value,lang):
    return level_label(field,value,lang) if field['type']=='categorical' else f"{float(value):.{field['decimals']}f}"

def unit_text(field,lang):
    unit=field.get('unit','')
    return {'岁':'years','分钟':'min'}.get(unit,unit) if lang=='en' else unit

def scenario(model,lang):
    names={f['name'] for f in model['variables']}
    if 'Site' in names:
        return ('多中心住院 · AKI风险评估','Multicentre admission · AKI assessment')[lang=='en']
    if 'Admission_Lactate' in names:
        return ('ICU入科 · AKI风险评估','ICU admission · AKI assessment')[lang=='en']
    if 'Planned_Duration' in names:
        return ('择期手术 · AKI风险评估','Elective surgery · AKI assessment')[lang=='en']
    return model.get('title_'+lang,model['title'])

def timing(model,lang):
    names={f['name'] for f in model['variables']}
    if 'Site' in names: return ('住院入院评估 · 预测随后7天的AKI事件','Hospital admission assessment · AKI within the following 7 days')[lang=='en']
    if 'Admission_Lactate' in names: return ('ICU入科评估 · 预测随后7天的AKI事件','ICU admission assessment · AKI within the following 7 days')[lang=='en']
    if 'Planned_Duration' in names: return ('择期手术术前评估 · 预测随后7天的AKI事件','Preoperative assessment · AKI within the following 7 days')[lang=='en']
    return model.get('prediction_timepoint_'+lang,model.get('prediction_timepoint','') if lang=='zh' else '')

def coefficient_label(name,model,lang):
    if name=='Intercept': return '截距' if lang=='zh' else 'Intercept'
    for field in sorted(model['variables'],key=lambda f:len(f['name']),reverse=True):
        if name==field['name']: return label(field,lang)
        if name.startswith(field['name']+'='):
            code=name.split('=',1)[1]
            return label(field,lang)+' · '+level_label(field,code,lang)
    return name
