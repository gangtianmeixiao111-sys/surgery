"""The actual R regplot SVG with a live, mathematically identical patient layer."""
import xml.etree.ElementTree as ET
import re
import numpy as np
from predictor import predict,Z95
from i18n import label,scenario,TEXT

NS='http://www.w3.org/2000/svg'
FONT='Times New Roman, SimSun, 宋体, Songti SC, serif'
ET.register_namespace('',NS)

def regplot_scores(model,values,summary):
    asset=summary['regplot'];result=predict(model,values)
    b=np.asarray(asset['betas'],dtype=float);m=np.asarray(asset['m'],dtype=float)
    vector=np.asarray(result['design'][1:]);vact=np.asarray(asset['vact'],dtype=int)
    terms=b*(vector-m)
    if not np.isclose(float(terms.sum()+asset['intercept']),result['lp'],rtol=0,atol=1e-10):
        raise ValueError('The R nomogram design and prediction model differ.')
    L=asset['L'];M=asset['M'];scale=100/(M-L)
    fields={f['name']:f for f in model['variables']}
    rows=[]
    for i,name in enumerate(asset['row_names']):
        contribution=float(terms[vact==i+1].sum())
        rows.append({'field':fields[name],'contribution':contribution,'points':(contribution-L)*scale})
    total=sum(r['points'] for r in rows)
    return {'rows':rows,'total':total,'scale':scale,'offset':asset['intercept']+L*len(rows),
            'probability':result['probability'],'centered_lp':float(terms.sum())}

def nomogram_svg(model,values,summary,lang='zh'):
    asset=summary['regplot'];scores=regplot_scores(model,values,summary);result=predict(model,values)
    root=ET.fromstring(asset['svg'])
    width,height=asset['device_size']
    root.set('width','100%');root.set('height','auto')
    root.set('role','img');root.set('aria-label',TEXT[lang]['nomogram'])
    description=ET.Element('{'+NS+'}desc')
    description.text=TEXT[lang]['nomogram_hint']
    root.insert(0,description)
    fields={f['name']:f for f in model['variables']}
    for node in root.iter('{'+NS+'}text'):
        raw=(node.text or '').strip();replacement=None
        if lang=='zh':
            if raw in fields: replacement=label(fields[raw],lang)
            elif raw=='Points': replacement='分值'
            elif raw=='Total points': replacement='总分'
            elif raw.startswith('Pr('): replacement='发生概率'
        if raw==model['title']: replacement=scenario(model,lang)
        if replacement is not None:
            node.text=replacement
        # Replace the font on every original R label and tick. Remove widths
        # measured in Arial so Times/Song glyphs keep their natural proportions.
        node.attrib.pop('textLength',None);node.attrib.pop('lengthAdjust',None)
        style=re.sub(r'font-family\s*:[^;]*(;|$)','',node.attrib.get('style',''))
        node.set('style',style+';font-family:'+FONT+';')
        node.set('font-family',FONT)
    overlay=ET.SubElement(root,'{'+NS+'}g',{'id':'patient-overlay','fill':'#FF0000','stroke':'#FF0000'})
    xd=asset['x_device'];yd=asset['y_device']
    def x(v):return xd[0]+v*(xd[1]-xd[0])
    def y(v):return yd[0]+v*(yd[1]-yd[0])
    def node(tag,**attributes):
        return ET.SubElement(overlay,'{'+NS+'}'+tag,{k.replace('_','-'):str(v) for k,v in attributes.items()})
    def line(x1,y1,x2,y2,dotted=False,width=.7):
        attrs=dict(x1=x1,y1=y1,x2=x2,y2=y2,stroke_width=width,fill='none')
        if dotted:attrs['stroke_dasharray']='.8 1.8'
        node('line',**attrs)
    def point(cx,cy,r=2.6):node('circle',cx=cx,cy=cy,r=r,stroke_width=.45)
    top=asset['npanels']+1+asset['make_space']+.4
    # The row order, coordinates and affine mapping come directly from regplot.
    for i,row in enumerate(scores['rows']):
        rank=asset['irank'].index(i+1)+1
        ypos=rank+.5+asset['make_space'];cx=x(row['contribution'])
        line(cx,y(ypos+.02),cx,y(top-.02),dotted=True)
        point(cx,y(ypos));point(cx,y(top))
    L=asset['L'];M=asset['M'];span=asset['Range'];minimum=asset['Min_tot_score']
    def lp_x(lp):return x(L+(M-L)*(lp-asset['intercept']-minimum)/span)
    cx=lp_x(result['lp']);total_y=asset['yref_pos']-1;prob_y=asset['pos_of_nomo'];delta=asset['delta']
    cy=y(total_y);r=4.2
    node('polygon',points=f'{cx},{cy-r} {cx+r},{cy} {cx},{cy+r} {cx-r},{cy}',stroke_width=.55)
    total_text=node('text',x=cx,y=y(total_y+delta),text_anchor='middle',stroke='none',
                    font_family=FONT,font_style='italic',font_size=10.8)
    total_text.text=f"{scores['total']:.3g}"
    py=y(prob_y)
    line(cx,cy,cx,py,width=.8)
    point_y=y(prob_y+delta)
    node('polygon',points=f'{cx-4},{point_y-3} {cx+4},{point_y-3} {cx},{point_y+4}',stroke_width=.6)
    probability_text=node('text',x=cx-5,y=point_y+1,text_anchor='end',stroke='none',
                          font_family=FONT,font_style='italic',font_size=10.8)
    probability_text.text=f"{result['probability']:.3g}"
    low=lp_x(result['lp']-Z95*result['se']);high=lp_x(result['lp']+Z95*result['se'])
    line(low,py,high,py,width=1.25)
    for value in (low,high):line(value,py-5.5,value,py+5.5,width=1.2)
    # R itself allows the patient total/CI outside its observed total-score axis.
    # Expand the canvas if necessary so allowed input combinations stay visible.
    left=min(0,cx-35,low-10);right=max(width,cx+25,high+10)
    root.set('viewBox',f'{left} 0 {right-left} {height}')
    root.set('style','display:block;max-width:100%;height:auto;background:#FFFFFF;')
    return ET.tostring(root,encoding='unicode')
