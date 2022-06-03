import dashsubcomponents
from dash import Dash
from dash.dependencies import Input, Output
from dash_extensions import WebSocket
import dash_bootstrap_components as dbc
from dash import Output, html, dcc, Input

# Create example app.
app = Dash(__name__, prevent_initial_callbacks=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

websocket = html.Div([
    dcc.Input(id="input", autoComplete="off"), html.Div(id="message"),
    WebSocket(url="ws://127.0.0.1:5000/", id="ws")
])


content = dbc.Container([dcc.Textarea(id='liveupdate', value="This will contain the log", style={'width': '100%', 'height': '100%'}), websocket, dcc.Interval(interval=1000, n_intervals=0, id="trigger")], id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), dashsubcomponents.sidebar, content])


@app.callback(Output("ws", "send"), [Input("input", "value")])
def send(value):
    return value

@app.callback(Output("message", "children"), [Input("ws", "message")])
def message(e):
    return f"Response from websocket: {e['data']}"

if __name__ == '__main__':
    app.run_server()