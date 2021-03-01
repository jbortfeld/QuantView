import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import pandas as pd
import math
import flask
from utilities import *

import config
from app import app
from app import server
from apps import nav_bar
from apps import retirement_easy
from apps import homepage
from apps import functions
from apps import about
from apps import systemic_risk
from apps import schelling_segregation



PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button("Search", color="primary", className="ml-2"),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

blog_address='https://medium.com/@jbortfeld/an-easy-app-for-retirement-planning-59dcf37be97'

this_page_header = dbc.Row([
        dbc.Col(
            html.A(
                html.Img(src='/logo.png', height="70px",)
                , href='/')
        , width=10, style={'margin': '10px'}),
        dbc.Col(
        ),
        dbc.Col(
            html.A('ABOUT', href='/about', 
                style={'color': 'white', 'font-weight': 'bold'})
            ,  style={'vertical-align': 'middle', 'margin': 'auto'}
        ),
    ], no_gutters=True, style={'background-color': "#2FC086", 'height': '90px'}
)

app.index_string = '''<!DOCTYPE html>
<html>
<head>
  <!-- Global site tag (gtag.js) - Google Analytics -->
    <script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

    ga('create', 'UA-179199475-1', 'auto');
    ga('send', 'pageview');
    </script>
  <!-- End Global Google Analytics -->
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
'''

app.layout = html.Div([

    dcc.Location(id='url', refresh=False),

    html.Div(this_page_header),

    html.Div(id='page-content', className='body')

], style = {'backgroundColor': config.colors['background'],
            'margin': 0,
            'padding': 0})


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return homepage.layout()
    elif pathname == '/retirement-planning-in-easy-mode':
        return retirement_easy.layout()
    elif pathname == '/about':
        return about.layout()
    elif pathname == '/systemic-risk':
        return systemic_risk.layout()
    elif pathname == '/schelling-segregation':
        return schelling_segregation.layout()
    else:
        return '404'

# https://github.com/plotly/dash/issues/71
# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
image_directory = 'images/'
static_image_route = '/'
@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    return flask.send_from_directory(image_directory, image_name)

if __name__ == '__main__':
    app.run_server(debug=True)
