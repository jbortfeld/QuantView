
import dash
import dash_core_components as dcc
import dash_html_components as html

# VERTICAL NAVIGATION BAR

nav_bar = [

    dcc.Link('Home', href='/', style={'color': 'lightblue', 'font-size': 20}),

    html.Div('About', style={'color': 'lightblue', 'font-size': 20}),

    html.Div('Blog', style={'color': 'lightblue', 'font-size': 20}),

    html.Div('Github', style={'color': 'lightblue', 'font-size': 20}),

    html.Div('Contact Us', style={'color': 'lightblue', 'font-size': 20}),

    html.Br(),

    html.Div('This Blog', style={'color': 'lightblue', 'font-size': 20}),

    html.Div('This Github', style={'color': 'lightblue', 'font-size': 20}),


    html.Br(),

    html.Div('Apps', style={'color': 'lightblue', 'font-size': 20}),

    dcc.Link('-- Macro Similarity', href='/markets_in_rear_view', style={'color': 'lightblue', 'font-size': 16}),

    dcc.Link('-- Recession Analysis', href='/recession_paths', style={'color': 'lightblue', 'font-size': 16}),

]
