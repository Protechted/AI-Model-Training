#!/usr/bin/env python3
import dash_bootstrap_components as dbc
from dash import Output, html, dcc, Input
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2("Protechted", className="display-5"),
        html.Hr(),
        html.P(
            "Admin interface zur Sturzerkennung", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact", external_link=True),
                dbc.NavLink("ML Training", href="/mltraining", active="exact", external_link=True),
                dbc.NavLink("Live Data", href="/livedata", active="exact", external_link=True),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)