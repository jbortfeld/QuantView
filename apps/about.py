import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def serve_layout():

	return [

	html.Br(),
	html.Br(),
	html.Br(),

		dbc.Row([
			dbc.Col('', width=2),
			dbc.Col(
				html.Img(src='web-development2.png', style={ 'height': '300px'})
			, width=3),


			dbc.Col([

				html.Br(),

				html.Div('''QuantViews''', style={'font-size': 48, 
					'font-weight': 'bold', 'color': '#2FC086'}),

				html.Div('''Financial Apps for Smarter Investing''', style={'font-size': 24, 
					'font-weight': 'bold', 'color': '#2FC086'}),

				html.Div('''By Joey Bortfeld''', style={'font-size': 18, 
					'font-weight': '', 'color': '#2FC086'}),
			])
			,	
		]),

		html.Br(),
		html.Br(),

		html.Div('''In my day job I'm a "quantitative analyst" covering the corporate bond markets. 
			Will Tesla by able to pay back the $10 billion in debt it has borrowed? What sectors are increasing their cash holdings?
			Is there a way to identify characteristics that are associated with outsized returns?''', 
			style={'text-align': 'left', 'margin-left': '5%', 'font-size': 18}),

		html.Br(),
		html.Br(),

		html.Div('''Now I want to make tools that are relevant for everyday people and that will help them
			navigate their financial life.''', style={'text-align': 'left', 'margin-left': '5%', 'font-size': 18}),

		html.Br(),
		html.Br(),

		html.Div('''My first app "Retirement Planning in Easy Mode" is a simple tool that will quickly 
			show users the long-term trajectory of their savings due to investing.''', 
			style={'text-align': 'left', 'margin-left': '5%', 'font-size': 18}),

		html.Br(),
		html.Br(),

		html.Div('''And there will be more! My next idea is to show users the comparative risk they are taking in 
			various financial investments. And after that I'd like to reproduce academic research on financial topics and
			show how they are relevant.''', 
			style={'text-align': 'left', 'margin-left': '5%', 'font-size': 18}),

		html.Br(),
		html.Br(),

		html.Div('''Questions or suggestions? Please write me at quantviews@gmail.com''',
			style={'text-align': 'left', 'margin-left': '5%', 'font-size': 18, 'color': '#2FC086'}),

		html.Br(),
		html.Br(),

		html.Div(
			html.A('''This website and all its analysis is open-source. See here''', 
			href='https://github.com/jbortfeld/QuantView')
		, style={'text-align': 'left', 'margin-left': '5%', 'font-size': 18, 'color': '#2FC086'}),

		html.Br(),
		html.Br(),




	]

layout=serve_layout