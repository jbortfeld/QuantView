import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import math
from utilities import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# slate grey: 3f4d5e

colors = {
    'background': '#0C1B33',
    'plot_background': '#0C1B33',
    'paper_background': '#0C1B33',
    'line': '#03B5AA',
    'line2': '#FF6978',
    'line3': '#A42CD6',
    'font': '#03B5AA',
    'axis': 'white',
    'title': '#0C1B33',
    'zero_vertical': 'red'
}


this_page =[

    # website header
    html.H3(children='QIS | Quantitative Investment Strategy Applications and Research Group',
            style={'backgroundColor': colors['background'],
                   'color': colors['font']}),

    html.Div(children='''A ROI Project - Reproduce, Open-source and Improve Investment Research''',
             style={'backgroundColor': colors['background'],
                    'color': colors['font'],
                    'fontSize': 20}),




]



# set the layout of this page
app.layout = html.Div(style={'backgroundColor': colors['background']},
                             children=this_page)



if __name__ == '__main__':
    app.run_server(debug=True)