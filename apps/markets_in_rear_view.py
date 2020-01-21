
import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import math
from utilities import *
import config

def serve_layout():

    content = [

        html.Div('Hello World', style={'color': 'red'})

    ]


    return content

layout = serve_layout