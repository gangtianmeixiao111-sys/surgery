"""Compact probability chart; the nomogram uses the actual R SVG."""
import numpy as np
import plotly.graph_objects as go
from i18n import TEXT
INK='#22334e'; BLUE='#41688e'; LINE='#8e9eaf'; RED='#d9535f'; PAPER='#fcfdff'
FONT='Times New Roman, SimSun, 宋体, Songti SC, serif'

def probability_figure(result,lang='zh'):
    """Full calibrated 0–100% ruler, with no invented risk bands."""
    t=TEXT[lang];p=result['probability'];a=result['lower'];b=result['upper']
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[0,1],y=[0,0],mode='lines',line=dict(color='#e3eaf2',width=18),hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=[a,b],y=[0,0],mode='lines',line=dict(color=BLUE,width=18),
       hovertemplate=t['ci']+f': {a:.2%} – {b:.2%}<extra></extra>'))
    fig.add_trace(go.Scatter(x=[p],y=[0],mode='markers',marker=dict(size=20,color=RED,line=dict(color=PAPER,width=3)),
       hovertemplate=t['estimate']+': %{x:.2%}<extra></extra>'))
    fig.add_annotation(x=p,y=.48,text=f'<b>{p:.2%}</b>',showarrow=False,font=dict(family=FONT,size=32,color=INK))
    fig.add_annotation(x=p,y=.28,text=t['risk'],showarrow=False,font=dict(family=FONT,size=12,color='#65738a'))
    for x in np.arange(0,1.001,.1):
        fig.add_shape(type='line',x0=x,x1=x,y0=-.50,y1=-.47,line=dict(color=LINE,width=1))
    fig.update_layout(template='none',height=280,paper_bgcolor=PAPER,plot_bgcolor=PAPER,
        margin=dict(l=30,r=30,t=15,b=40),font=dict(family=FONT,color=INK,size=12),showlegend=False,
        xaxis=dict(range=[-.025,1.025],tickvals=list(np.arange(0,1.001,.2)),tickformat='.0%',
                   showgrid=False,zeroline=False,fixedrange=True),
        yaxis=dict(range=[-.5,.65],visible=False,fixedrange=True),dragmode=False)
    return fig
