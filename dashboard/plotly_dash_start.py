import json
from collections import deque

import numpy as np
import plotly
import plotly.graph_objs as go
from matplotlib import pyplot as plt

import dashsubcomponents
from dash import Dash
import dash
from dash.dependencies import Input, Output
from dash_extensions import WebSocket
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
import dash_bootstrap_components as dbc
from dash import Output, html, dcc, Input, ctx
import pandas as pd
import plotly.tools as tls

# Create example app.
app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()], external_stylesheets=[dbc.themes.BOOTSTRAP])

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

websocket = html.Div([
    dcc.Input(id="input", autoComplete="off"), html.Div(id="message"),
])

mltraining = html.Div(
    [html.P("""Commands: "start" to start the Training. Results will be plotted when the training finished. """),
     dbc.Button('Start training', id='starttraining', n_clicks=0),html.Div(style={"margin-top": "5px"}), websocket])
mainpage = html.Div([html.P("Willkommen"), websocket])
liveData = html.Div(
    [html.P("""Live Data from the sensor. Commands: "live" to start the live Transmitting, "stopLive" to stop it. """),
     html.Div(id="hidden_div_for_redirect_callback"),
     dbc.Button('Start live transmit', id='startLiveTransmit', n_clicks=0, style={"margin-right": "4px"}),dbc.Button('Stop live transmit', id='stopLiveTransmit', n_clicks=0),html.Div(style={"margin-top": "5px"}), websocket, html.Br(),
     html.H2("Daten Beschleunigungssensor"),
     dcc.Graph(id='live-graph-accelerometer', animate=False, config={"responsive": True})])

content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div(
    [dcc.Location(id="url"), dashsubcomponents.sidebar, content, WebSocket(url="ws://192.168.8.218:5300/", id="ws")])

@app.callback(Output("ws", "send"), Output("hidden_div_for_redirect_callback", "children"), Input('startLiveTransmit', 'n_clicks'), prevent_initial_call=True)
def send(n_clicks):
    return "live", dcc.Location(pathname="/livedata", id="someid_doesnt_matter")

@app.callback(Output("ws", "send"), Input('stopLiveTransmit', 'n_clicks'), prevent_initial_call=True)
def send(n_clicks):
    return "stopLive"

@app.callback(Output("ws", "send"), Input('starttraining', 'n_clicks'), prevent_initial_call=True)
def send(n_clicks):
    print("Test")
    return "start"

@app.callback(Output("ws", "send"), Input("input", "value"), prevent_initial_call=True)
def send(value):
    return value


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return mainpage
    elif pathname == '/mltraining':
        return mltraining
    elif pathname == '/livedata':
        return liveData
    else:
        return mainpage


def df_to_plotly(df):
    return {'z': df.values.tolist(),
            'x': df.columns.tolist(),
            'y': df.columns.tolist()}


@app.callback(Output("message", "children"), [Input("ws", "message")])
def message(e):
    if str(e['data']) == None:
        return
    if str(e['data']).startswith("dataframeoutput:"):
        dataframe_string = str(e['data']).split("dataframeoutput:")[1]
        loaded_df = pd.read_json(dataframe_string, orient='index')

        print(loaded_df)
        print(loaded_df['ax'].tolist())

        # Correlation logic
        corr = loaded_df.corr()
        fig = go.Figure(data=go.Heatmap(df_to_plotly(loaded_df)))
        # End correlation logic

        return html.Div([dcc.Graph(
            id='ResultGraph',
            figure={
                'data': [
                    {"x": loaded_df.index.values.tolist(), "y": loaded_df['ax'].tolist(), 'type': 'line', 'name': 'Ax'},
                    {"x": loaded_df.index.values.tolist(), "y": loaded_df['ay'].tolist(), 'type': 'line', 'name': 'Ay'},
                    {"x": loaded_df.index.values.tolist(), "y": loaded_df['az'].tolist(), 'type': 'line', 'name': 'Az'},
                ],
                'layout': {
                    'title': 'Recorded Data Graph- Accelerometer',
                    'showlegend': 'true'
                }
            }
        ),
            dcc.Graph(
                id='ResultGraphGyroscope',
                figure={
                    'data': [
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['gx'].tolist(), 'type': 'line',
                         'name': 'Gx'},
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['gy'].tolist(), 'type': 'line',
                         'name': 'Gy'},
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['gz'].tolist(), 'type': 'line',
                         'name': 'Gz'},
                    ],
                    'layout': {
                        'title': 'Recorded Data Graph - Gyroscope',
                        'showlegend': 'true'
                    }
                }
            ),
            dcc.Graph(
                id='ResultGraphMagnetometer',
                figure={
                    'data': [
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['qx'].tolist(), 'type': 'line',
                         'name': 'qx'},
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['qy'].tolist(), 'type': 'line',
                         'name': 'qy'},
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['qz'].tolist(), 'type': 'line',
                         'name': 'qz'},
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['qw'].tolist(), 'type': 'line',
                         'name': 'qw'},

                    ],
                    'layout': {
                        'title': 'Recorded Data Graph - Magnetometer',
                        'showlegend': 'true'
                    }
                }
            ),
            dcc.Graph(
                id='ResultGraphPressure',
                figure={
                    'data': [
                        {"x": loaded_df.index.values.tolist(), "y": loaded_df['p'].tolist(), 'type': 'line',
                         'name': 'p'}
                    ],
                    'layout': {
                        'title': 'Recorded Data Graph - Pressure',
                        'showlegend': 'true'
                    }
                }
            ),
            dcc.Graph(
                id='ResultGraphCorrelation',
                figure=fig
            ),
        ])
    if (str(e['data']).startswith("liveData:")):
        return
    return f"Response from websocket: {e['data']}"


X = deque(maxlen=50)
xaxiscounter = 0
YforAx = deque(maxlen=50)
YforAy = deque(maxlen=50)
YforAz = deque(maxlen=50)


@app.callback(Output("live-graph-accelerometer", "figure"), [Input("ws", "message")])
def message(e):
    global xaxiscounter
    global X
    global YforAx
    global YforAy
    global YforAz
    if str(e['data']) == None:
        return
    if (str(e['data']).startswith("liveData:")):
        dict_string = str(e['data']).split("liveData:")[1]
        dict_values = json.loads(dict_string)
        xaxiscounter += 1
        X.append(xaxiscounter)
        YforAx.append(dict_values["ax"])
        YforAy.append(dict_values["ay"])
        YforAz.append(dict_values["az"])

        figure = {
            'data': [
                {"x": list[X], "y": list[YforAx], 'type': 'line', 'name': 'ax'},
            ],
            'layout': {
                'title': 'Live Data Graph',
                'showlegend': 'true'
            }
        }
        dataAx = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(YforAx),
            name='AccelerometerX',
        )
        dataAy = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(YforAy),
            name='AccelerometerY',
        )
        dataAz = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(YforAz),
            name='AccelerometerZ',
        )

        return {'data': [dataAx, dataAy, dataAz],
                'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]), uirevision=True)}


if __name__ == '__main__':
    app.run_server()
