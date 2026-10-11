"""Compact, consistent CeCe Plotly styling with explicit units and bases."""

import plotly.express as px

from cece.presentation import nutrient_text

PALETTE = ["#D85C46", "#49745E", "#8873A8"]
FONT = "Arial, sans-serif"


def bar_chart(frame, x, y, title, unit, colors, grouped=False):
    fig = px.bar(frame.dropna(subset=[y]), x=x, y=y, color="Food", color_discrete_map=colors,
                 barmode="group" if grouped else "relative", title=title)
    fig.update_layout(
        height=330, margin=dict(l=20, r=15, t=55, b=35),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=13, color="#193737"),
        title=dict(font=dict(size=18), x=0),
        legend=dict(title=None, orientation="h", y=-0.22, x=0, font=dict(size=11)),
        bargap=.35, bargroupgap=.12,
    )
    fig.update_xaxes(title=None, tickfont=dict(size=12), showgrid=False, automargin=True)
    fig.update_yaxes(title=unit, rangemode="tozero", gridcolor="#E7E6DF", zeroline=False, automargin=True)
    fig.update_traces(hovertemplate=f"%{{y:.2f}} {unit}<extra>%{{fullData.name}}</extra>")
    if x == "Food":
        fig.update_layout(showlegend=False)
    return fig


def comparison_chart(frame, nutrient, title, unit, colors):
    """One responsive horizontal chart; absent measurements never become bars."""
    data = frame.dropna(subset=[nutrient]).copy()
    data["Display value"] = data[nutrient].map(lambda v: nutrient_text(v, unit))
    fig = px.bar(data, x=nutrient, y="Food", color="Food", orientation="h",
                 color_discrete_map=colors, text="Display value", custom_data=["Description"], title=title)
    fig.update_layout(height=130 + 65 * max(1, len(frame)), margin=dict(l=10, r=85, t=48, b=40),
                      font=dict(family=FONT, size=14, color="#193737"), showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", bargap=.45,
                      title=dict(font=dict(size=22), x=0), hoverlabel=dict(font=dict(family=FONT, size=14)))
    fig.update_xaxes(title=unit, rangemode="tozero", gridcolor="#EEE7DF", zeroline=False, tickfont=dict(size=14))
    fig.update_yaxes(title=None, autorange="reversed", automargin=True, tickfont=dict(size=14))
    fig.update_traces(textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}<br>%{text}<br>%{customdata[0]}<extra></extra>")
    return fig
