"""Inference for an R-exported additive binary logistic model; no refitting."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import plotly.graph_objects as go

Z95 = 1.959963984540054


def load_model(path: str | Path) -> dict:
    model = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if model.get("schema_version") != 1 or model.get("model_type") != "binary_logistic_additive":
        raise ValueError("模型格式不支持，请重新运行 R 导出器。")
    beta = np.asarray(model["coefficients"], dtype=float)
    cov = np.asarray(model["covariance"], dtype=float)
    base = np.asarray(model["base_design"], dtype=float)
    if beta.ndim != 1 or cov.shape != (beta.size, beta.size) or base.shape != beta.shape:
        raise ValueError("模型系数、协方差和设计矩阵维度不一致。")
    if not all(np.isfinite(a).all() for a in (beta, cov, base)):
        raise ValueError("模型参数中存在非有限值。")
    if not np.allclose(cov, cov.T, rtol=1e-9, atol=1e-12):
        raise ValueError("模型协方差矩阵不对称。")
    for field in model["variables"]:
        if field["type"] == "continuous":
            deltas = [field["design_delta"]]
            if not field["min"] < field["max"] or not field["step"] > 0:
                raise ValueError(f"{field['name']} 的输入范围或步长无效。")
        elif field["type"] == "categorical":
            deltas = [level["design_delta"] for level in field["levels"]]
        else:
            raise ValueError("存在不支持的变量类型。")
        if any(np.asarray(delta).shape != beta.shape or not np.isfinite(delta).all() for delta in deltas):
            raise ValueError("变量编码与模型系数维度不一致。")
    return model


def expit(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def variable_delta(field: dict, value) -> np.ndarray:
    if field["type"] == "continuous":
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field['label']} 需要数值。") from None
        if not math.isfinite(number) or not field["min"] <= number <= field["max"]:
            raise ValueError(f"{field['label']} 超出已配置的输入范围。")
        return np.asarray(field["design_delta"], dtype=float) * (number - field["reference"])
    for level in field["levels"]:
        if str(value) == str(level["value"]):
            return np.asarray(level["design_delta"], dtype=float)
    raise ValueError(f"{field['label']} 的分类编码无效。")


def predict(model: dict, values: dict) -> dict:
    beta = np.asarray(model["coefficients"], dtype=float)
    vector = np.asarray(model["base_design"], dtype=float).copy()
    contributions = []
    for field in model["variables"]:
        if field["name"] not in values:
            raise ValueError(f"缺少 {field['label']}。")
        delta = variable_delta(field, values[field["name"]])
        vector += delta
        contributions.append(float(delta @ beta))
    lp = float(vector @ beta)
    variance = float(vector @ np.asarray(model["covariance"], dtype=float) @ vector)
    if variance < -1e-9:
        raise ValueError("预测方差为负，请检查模型导出。")
    se = math.sqrt(max(0.0, variance))
    return {"lp": lp, "se": se, "probability": expit(lp),
            "lower": expit(lp-Z95*se), "upper": expit(lp+Z95*se),
            "contributions": contributions, "design": vector.tolist()}


def nomogram_scores(model: dict, values: dict) -> dict:
    beta = np.asarray(model["coefficients"], dtype=float)
    rows = []
    for field in model["variables"]:
        if field["type"] == "continuous":
            extremes = [float(variable_delta(field, v) @ beta) for v in (field["min"], field["max"])]
        else:
            extremes = [float(np.asarray(v["design_delta"]) @ beta) for v in field["levels"]]
        contribution = float(variable_delta(field, values[field["name"]]) @ beta)
        rows.append({"field": field, "minimum": min(extremes), "maximum": max(extremes), "contribution": contribution})
    widest = max(row["maximum"]-row["minimum"] for row in rows)
    scale = 100.0/widest if widest > 1e-14 else 1.0
    for row in rows:
        row["points"] = (row["contribution"]-row["minimum"])*scale
        row["max_points"] = (row["maximum"]-row["minimum"])*scale
    total = sum(row["points"] for row in rows)
    max_total = sum(row["max_points"] for row in rows)
    offset = float(np.asarray(model["base_design"]) @ beta) + sum(row["minimum"] for row in rows)
    return {"rows": rows, "scale": scale, "total": total, "max_total": max_total,
            "offset": offset, "probability": expit(offset+total/scale)}


def format_value(field: dict, value) -> str:
    if field["type"] == "categorical":
        return next(level["label"] for level in field["levels"] if str(level["value"]) == str(value))
    return f"{float(value):.{field['decimals']}f}"


def nomogram_figure(model: dict, values: dict) -> go.Figure:
    scores = nomogram_scores(model, values)
    beta = np.asarray(model["coefficients"], dtype=float)
    n = len(scores["rows"])
    fig = go.Figure()
    labels, positions = ["Points"], [n+3]
    teal, red, muted = "#28646B", "#C64343", "#81949B"

    def axis(y, xs, texts, start=0, end=100, stagger=False):
        fig.add_trace(go.Scatter(x=[start,end],y=[y,y],mode="lines",line=dict(color=muted,width=1),hoverinfo="skip",showlegend=False))
        lanes=[]
        for x,text in zip(xs,texts):
            fig.add_shape(type="line",x0=x,x1=x,y0=y-.07,y1=y+.07,line=dict(color=muted,width=1))
            lane=0
            if stagger:
                while lane<len(lanes) and any(abs(x-other)<max(12,len(str(text))*2.5) for other in lanes[lane]):
                    lane+=1
                if lane==len(lanes): lanes.append([])
                lanes[lane].append(x)
            label_y=y-.2-.2*lane
            if lane:
                fig.add_shape(type="line",x0=x,x1=x,y0=y-.08,y1=label_y+.08,line=dict(color=muted,width=.7,dash="dot"))
            fig.add_annotation(x=x,y=label_y,text=str(text),showarrow=False,font=dict(size=11,color="#48616A"))

    axis(n+3,list(range(0,101,20)),list(range(0,101,20)))
    for i,row in enumerate(scores["rows"]):
        field=row["field"]; y=n+2-i
        label=field["label"]+(f" ({field['unit']})" if field.get("unit") else "")
        labels.append(label);positions.append(y)
        if field["type"] == "continuous":
            tick_values=np.unique(np.round(np.linspace(field["min"],field["max"],4),field["decimals"]))
            texts=[f"{v:.{field['decimals']}f}" for v in tick_values]
            contributions=[float(variable_delta(field,v) @ beta) for v in tick_values]
        else:
            texts=[v["label"] for v in field["levels"]]
            contributions=[float(np.asarray(v["design_delta"]) @ beta) for v in field["levels"]]
        xs=[(v-row["minimum"])*scores["scale"] for v in contributions]
        if row["max_points"] < 1e-8:
            xs=[0];texts=["无分值差异"]
        axis(y,xs,texts,end=max(row["max_points"],0.01),stagger=field["type"]=="categorical")
        current=format_value(field,values[field["name"]])
        fig.add_trace(go.Scatter(x=[row["points"]],y=[y],mode="markers",marker=dict(color=red,size=10),
                                customdata=[[current,row["points"]]],hovertemplate=f"{label}<br>%{{customdata[0]}}<br>分值 %{{customdata[1]:.2f}}<extra></extra>",showlegend=False))
        fig.add_annotation(x=102,y=y,text=f"{current} → {row['points']:.1f}分",showarrow=False,xanchor="left",font=dict(color=red,size=11))

    maximum=max(scores["max_total"],1.0)
    total_x=scores["total"]/maximum*100
    total_ticks=np.linspace(0,maximum,6)
    labels.extend(["Total points",model["outcome_label"]]);positions.extend([1,0])
    axis(1,total_ticks/maximum*100,[f"{v:.0f}" for v in total_ticks])
    risk_ticks=[.001,.01,.05,.1,.2,.4,.6,.8,.9,.95,.99,.999]
    risk_x=[];risk_text=[]
    for p in risk_ticks:
        point=(math.log(p/(1-p))-scores["offset"])*scores["scale"]
        if 0<=point<=maximum:
            risk_x.append(point/maximum*100);risk_text.append(f"{p:.1%}" if p<.01 or p>.99 else f"{p:.0%}")
    axis(0,risk_x,risk_text)
    fig.add_trace(go.Scatter(x=[total_x,total_x],y=[0,1],mode="lines+markers",line=dict(color=red,dash="dot"),
                            marker=dict(color=red,size=10),hoverinfo="skip",showlegend=False))
    fig.add_annotation(x=102,y=1,text=f"{scores['total']:.2f}分",showarrow=False,xanchor="left",font=dict(color=red,size=12))
    fig.add_annotation(x=102,y=0,text=f"{scores['probability']:.2%}",showarrow=False,xanchor="left",font=dict(color=red,size=12))
    fig.update_layout(template="plotly_white",height=max(540,90+65*(n+4)),
                      margin=dict(l=225,r=170,t=20,b=45),font=dict(family="Arial, Microsoft YaHei, sans-serif"),
                      xaxis=dict(range=[-2,120],visible=False,fixedrange=True),
                      yaxis=dict(range=[-.65,n+3.5],tickvals=positions,ticktext=labels,showgrid=False,zeroline=False,fixedrange=True))
    return fig


def probability_figure(result: dict, outcome_label: str) -> go.Figure:
    fig=go.Figure(go.Scatter(x=[result["probability"]],y=[0],mode="markers",
        marker=dict(size=13,color="#28646B",symbol="square"),
        error_x=dict(type="data",array=[result["upper"]-result["probability"]],
                     arrayminus=[result["probability"]-result["lower"]],color="#28646B",thickness=2),
        hovertemplate="预测概率 %{x:.2%}<extra></extra>"))
    fig.update_layout(template="plotly_white",height=290,margin=dict(l=30,r=30,t=30,b=50),
                      xaxis=dict(title=outcome_label,range=[0,1],tickformat=".0%"),
                      yaxis=dict(visible=False,range=[-1,1]),showlegend=False)
    return fig
