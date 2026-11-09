"""Bilingual clinical risk workbench. Parameters and inference stay in R parity."""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import hashlib
import html
import json
import math
import numpy as np
import streamlit as st
from predictor import load_model,predict,Z95
from figures import probability_figure
from regplot_view import regplot_scores,nomogram_svg
from i18n import TEXT,label,level_label,value_text,unit_text,help_note,scenario,timing,coefficient_label

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='风险预测' if st.session_state.get('language','zh')=='zh' else 'Risk prediction',layout='wide',page_icon=':material/monitor_heart:')
st.html('<style>'+ROOT.joinpath('styles.css').read_text(encoding='utf-8')+'</style>')
st.session_state.setdefault('language','zh')
lang=st.session_state.language
t=TEXT[lang]

@st.cache_data(max_entries=8)
def read_model(path,mtime): return load_model(path)
@st.cache_data(max_entries=8)
def read_summary(path,mtime): return json.loads(Path(path).read_text(encoding='utf-8-sig'))

try:
    path=ROOT/'model.json';model=read_model(str(path),path.stat().st_mtime_ns)
    path=ROOT/'distribution.json'
    summary=read_summary(str(path),path.stat().st_mtime_ns) if path.exists() else {}
except (OSError,ValueError,KeyError):
    st.error(t['load_error']);st.stop()

fingerprint=hashlib.sha256(json.dumps(model,sort_keys=True).encode()).hexdigest()
if st.session_state.get('model_fingerprint')!=fingerprint:
    for key in list(st.session_state):
        if key.startswith(('num_','slide_','cat_','precision_','active_precision_')): del st.session_state[key]
    st.session_state.model_fingerprint=fingerprint
    st.session_state['precision_mode']='source'

def rounded(value,n):
    value=float(Decimal(str(value)).quantize(Decimal(1).scaleb(-n),rounding=ROUND_HALF_UP))
    return int(value) if n==0 else value
def sync(source,target,n):
    initial=st.session_state[source];value=rounded(initial,n)
    st.session_state[source]=value;st.session_state[target]=value
    if not math.isclose(float(initial),float(value),rel_tol=0,abs_tol=1e-12):
        st.toast(t['rounded'].format(n=n,value=value))
def sync_category(widget_key,canonical_key):
    st.session_state[canonical_key]=st.session_state[widget_key]
def change_view(view): st.session_state['view_nav']=view
def reset():
    for field in model['variables']:
        name=field['name']
        if field['type']=='continuous':
            n=st.session_state.get('active_precision_'+name,field['decimals'])
            value=rounded(field['default'],n)
            st.session_state['num_'+name]=value;st.session_state['slide_'+name]=value
        else: st.session_state['cat_'+name]=str(field['default'])
if not st.session_state.get('inputs_initialized_'+fingerprint):
    reset();st.session_state['inputs_initialized_'+fingerprint]=True

def esc(x):return html.escape(str(x))
def table(title,headers,rows):
    output='<div class="data-table-wrap"><table class="clinical-table"><caption>'+esc(title)+'</caption><thead><tr>'
    output+=''.join('<th scope="col">'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'
    for row in rows: output+='<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>'
    st.html(output+'</tbody></table></div>')

values={}
with st.sidebar:
    st.html('<div class="brand"><div class="brand-mark">＋</div><div><div class="brand-name">'+
        ('临床预测工具' if lang=='zh' else 'Clinical prediction')+'</div><div class="brand-sub">AKI · '+
        ('研究与教学' if lang=='zh' else 'Research & teaching')+'</div></div></div>')
    st.html('<div class="sidebar-heading">'+t['patient']+'</div><div class="sidebar-hint">'+t['patient_hint']+'</div>')
    # Precision choices use stable codes, so language switching preserves state.
    with st.expander(t['precision']):
        custom=st.toggle(t['custom'],key='precision_custom')
        st.caption(t['precision_hint'] if custom else t['source'])
        for field in model['variables']:
            if field['type']!='continuous': continue
            name=field['name'];source=field.get('data_decimals',field['decimals']);key='precision_'+name
            st.session_state.setdefault(key,field['decimals'])
            n=st.number_input(label(field,lang)+' · '+t['digits'],min_value=source,max_value=10,step=1,
                 key=key,persist_state='session',help=t['precision_help'].format(n=source)) if custom else source
            field['decimals']=int(n);field['step']=10**(-n)
            if st.session_state.get('active_precision_'+name)!=n:
                value=rounded(st.session_state['num_'+name],n)
                st.session_state['num_'+name]=value;st.session_state['slide_'+name]=value
                st.session_state['active_precision_'+name]=n
    st.button(t['reset'],on_click=reset,icon=':material/restart_alt:',width='stretch')
    for field in model['variables']:
        name=field['name'];unit=unit_text(field,lang);display=label(field,lang)+(f' ({unit})' if unit else '')
        if field['type']=='continuous':
            n=field['decimals'];cast=int if n==0 else float
            fmt='%d' if n==0 else f'%.{n}f'
            help_text=help_note(field,lang)+(' ' if lang=='en' else '')+t['range'].format(
                low=f"{field['min']:g}",high=f"{field['max']:g}",step=f"{field['step']:g}")
            values[name]=st.number_input(display,min_value=cast(field['min']),max_value=cast(field['max']),
                step=cast(field['step']),format=fmt,key='num_'+name,on_change=sync,
                args=('num_'+name,'slide_'+name,n),help=help_text,persist_state='session')
            st.slider(display+' · '+t['slider'],min_value=cast(field['min']),max_value=cast(field['max']),
                step=cast(field['step']),format=fmt,key='slide_'+name,on_change=sync,
                args=('slide_'+name,'num_'+name,n),label_visibility='collapsed',persist_state='session')
        else:
            # Translated option labels are presentation, never the stored code.
            # A language-specific widget prevents native selectbox option identity
            # changes from resetting a patient's category on language switch.
            canonical='cat_'+name;widget=f'category_{lang}_{name}'
            st.session_state[widget]=st.session_state[canonical]
            st.selectbox(display,[str(l['value']) for l in field['levels']],
               format_func=lambda code,f=field:level_label(f,code,lang),key=widget,
               on_change=sync_category,args=(widget,canonical),help=help_note(field,lang))
            values[name]=st.session_state[canonical]
    st.html('<div class="footnote">'+t['footer']+'</div>')

header,language=st.columns([4,1],vertical_alignment='top')
with language:
    st.segmented_control(t['language'],['zh','en'],format_func=lambda code:'中文' if code=='zh' else 'EN',
        key='language_switch',default=lang,required=True,width='content',label_visibility='collapsed',
        on_change=lambda:st.session_state.update(language=st.session_state.language_switch))
with header:
    st.html('<div class="page-heading"><div><h1>'+t['title']+'</h1><p>'+esc(scenario(model,lang))+'</p></div></div>')
st.html('<div class="teaching-note"><span class="status-dot"></span>'+t['notice' if model.get('is_simulated') else 'research']+'</div>')
st.html('<div class="timepoint">'+esc(timing(model,lang))+'</div>')
try:
    result=predict(model,values);scores=regplot_scores(model,values,summary)
except (ValueError,KeyError,TypeError):
    st.error(t['prediction_error']);st.stop()

st.html('<div class="metric-strip">'+''.join(
    f'<div class="metric-cell"><div class="metric-label">{esc(title)}</div><div class="metric-value {extra}">{value}</div></div>'
    for title,value,extra in ((t['risk'],f"{result['probability']:.2%}",''),(t['ci'],f"{result['lower']:.2%} – {result['upper']:.2%}",'ci'),(t['total'],f"{scores['total']:.2f}",'')))+'</div>')
st.session_state.setdefault('view_nav','nomogram')
with st.container(key='view_nav'):
    columns=st.columns(4,gap='small')
    for column,key in zip(columns,('nomogram','graphical','numerical','model')):
        with column:
            st.button(t[key],key='nav_'+key,on_click=change_view,args=(key,),
                type='primary' if st.session_state.view_nav==key else 'secondary',width='stretch')
view=st.session_state.view_nav
with st.container(key='main_panel'):
    st.html('<div class="section-head'+(' centered-section' if view in ('numerical','model') else '')+'"><h2>'+t[view]+'</h2><p>'+t['outcome']+'</p></div>')
    if view=='nomogram':
        st.html('<div class="section-description">'+t['nomogram_hint']+'</div>')
        st.html('<div class="mobile-chart-hint">'+('左右滑动查看完整列线图' if lang=='zh' else 'Swipe horizontally to explore the full nomogram')+'</div>')
        if not summary: st.caption(t['no_distribution'])
        with st.container(key='nomogram_scroll'):
            st.image(nomogram_svg(model,values,summary,lang),width='stretch')
        st.html('<div class="footnote">'+t['score_note']+'</div>')
    elif view=='graphical':
        st.html('<div class="section-description">'+t['graph_hint']+'</div>')
        st.plotly_chart(probability_figure(result,lang),width='stretch',key='probability_chart',
             config={'displayModeBar':False,'displaylogo':False},theme=None)
        st.html('<div class="risk-detail">'+''.join(f'<div><span>{esc(title)}</span><strong>{value:.2%}</strong></div>' for title,value in
           ((t['lower'],result['lower']),(t['estimate'],result['probability']),(t['upper'],result['upper'])))+'</div>')
        st.html('<div class="footnote">'+t['ci_note']+'</div>')
    elif view=='numerical':
        table(t['parameters'],[t['parameter'],t['value'],t['unit']],
          [[label(f,lang),value_text(f,values[f['name']],lang),unit_text(f,lang) or '—'] for f in model['variables']])
        table(t['results'],[t['parameter'],t['value']],[[t['risk'],f"{result['probability']:.2%}"],
          [t['lower'],f"{result['lower']:.2%}"],[t['upper'],f"{result['upper']:.2%}"],
          [t['lp'],f"{result['lp']:.6f}"],[t['se'],f"{result['se']:.6f}"]])
    else:
        training=model['training']
        st.html('<div class="section-description">'+t['model_type']+' · '+t['coding']+'</div>')
        st.html('<div class="model-facts">'+''.join(f'<div><strong>{v}</strong><span>{esc(k)}</span></div>' for k,v in
             ((t['samples'],training['n']),(t['events'],training['events']),(t['predictors'],len(model['variables']))))+'</div>')
        beta=np.asarray(model['coefficients']);se=np.sqrt(np.maximum(np.diag(model['covariance']),0))
        table(t['coefficients'],[t['term'],t['coefficient'],t['se'],t['coef_lower'],t['coef_upper']],
          [[coefficient_label(name,model,lang),f'{b:.4f}',f'{s:.4f}',f'{b-Z95*s:.4f}',f'{b+Z95*s:.4f}']
            for name,b,s in zip(model['coefficient_names'],beta,se)])
        definition=[]
        for f in model['variables']:
            if f['type']=='continuous': bounds=f"{f['min']:g}–{f['max']:g}";step=f"{f['step']:g}"
            else: bounds='; '.join(str(v['value'])+' = '+level_label(f,v['value'],lang) for v in f['levels']);step='—'
            definition.append([label(f,lang),unit_text(f,lang) or '—',bounds,step,help_note(f,lang).rstrip('；;')])
        table(t['definition'],[t['parameter'],t['unit'],t['range_code'],t['step'],t['timing']],definition)
        st.html('<div class="footnote">'+t['model_scope']+'</div>')
with st.expander(t['more']):
    st.caption(t['model_note']+' '+t['ci_note']+' '+t['score_note'])
