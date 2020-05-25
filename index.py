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
from apps import home
from apps import functions


# APP HEADER
# this will appear as the header of every page of the app

# this_page_header = html.Div([
#
#     dbc.NavbarSimple([
#     # website header
#     html.Img(src='/logo.png',
#     alt='quant views logo',
#     style={'height': '90px'}),
#     ])
#
# ])


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

this_page_header = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src='/logo.png', height="80px")),
                    #dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),
                    dbc.Col(html.Div('ABOUT')),
                    dbc.Col(html.Div('FAQ')),
                    dbc.Col(html.Div('CONTACT')),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        ),
        # dbc.NavbarToggler(id="navbar-toggler"),
        # dbc.Colla[pse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="#2FC086",
    dark=True,
)



app.layout = html.Div([

    dcc.Location(id='url', refresh=False),

    html.Div(this_page_header),

    html.Div(id='page-content', className='body')

], style = {'backgroundColor': config.colors['background'],
            'margin': -10,
            'padding': 10})


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home.layout()
    # if pathname == '/recession_paths':
    #     return recession_paths.layout()
    # if pathname == '/markets_in_rear_view':
    #     return markets_in_rear_view.layout()
    else:
        return '404'

# https://github.com/plotly/dash/issues/71
# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
image_directory = '/Users/education/Desktop'
static_image_route = '/'
@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    return flask.send_from_directory(image_directory, image_name)

if __name__ == '__main__':
    app.run_server(debug=True)
