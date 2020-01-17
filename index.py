import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import math
from utilities import *

from app import app
from apps import recession_paths


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return recession_paths.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)