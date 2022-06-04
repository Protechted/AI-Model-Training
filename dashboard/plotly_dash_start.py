import json
from collections import deque

import plotly
import plotly.graph_objs as go

import dashsubcomponents
from dash import Dash
from dash.dependencies import Input, Output
from dash_extensions import WebSocket
import dash_bootstrap_components as dbc
from dash import Output, html, dcc, Input
import pandas as pd

# Create example app.
app = Dash(__name__, prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

websocket = html.Div([
    dcc.Input(id="input", autoComplete="off"), html.Div(id="message"),

])


mltraining = html.Div([dcc.Textarea(id='liveupdate', value="""Commands: "start" to start the Training """, style={'width': '100%', 'height': '100%'}), websocket])
mainpage = html.Div([html.P("Willkommen"), websocket])
liveData = html.Div([html.P("Live Data from the sensor"), websocket, html.Br(), html.H2("Daten Beschleunigungssensor"), dcc.Graph(id = 'live-graph-accelerometer', animate = False, config={"responsive":True})])


content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), dashsubcomponents.sidebar, content, WebSocket(url="ws://192.168.8.218:5300/", id="ws")])


@app.callback(Output("ws", "send"), [Input("input", "value")])
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

@app.callback(Output("message", "children"), [Input("ws", "message")])
def message(e):
    if (str(e['data']).startswith("dataframeoutput:")):
        dataframe_string = str(e['data']).split("dataframeoutput:")[1]
        loaded_df = pd.read_json(dataframe_string, orient='index')

        print(loaded_df)
        print(loaded_df['ax'].tolist())
        return dcc.Graph(
            id='ResultGraph',
            figure={
                'data': [
                    {"x": loaded_df.index.values.tolist(), "y": loaded_df['ax'].tolist(), 'type': 'line', 'name': 'ax'},
                    {"x": loaded_df.index.values.tolist(), "y": loaded_df['p'].tolist(), 'type': 'line', 'name': 'p'}
                ],
                'layout': {
                    'title': 'Recorded Data Graph',
                    'showlegend': 'true'
                }
            }
        )
    if (str(e['data']).startswith("liveData:")):
        return
    return f"Response from websocket: {e['data']}"


X = deque(maxlen = 50)
xaxiscounter = 0
YforAx = deque(maxlen = 50)
YforAy = deque(maxlen = 50)
YforAz = deque(maxlen = 50)


@app.callback(Output("live-graph-accelerometer", "figure"), [Input("ws", "message")])
def message(e):
    global xaxiscounter
    global X
    global YforAx
    global YforAy
    global YforAz
    if (str(e['data']).startswith("liveData:")):
        dict_string = str(e['data']).split("liveData:")[1]
        dict_values = json.loads(dict_string)
        xaxiscounter +=1
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

        return {'data': [dataAx,dataAy,dataAz],
                'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]), uirevision = True)}

if __name__ == '__main__':
    app.run_server()