#This dashboard is a modified version of https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-pk-calc

#MODULES
#Core components
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

from app import app

#Visualization
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# APP

layout =  html.Div(
    className="",
    children=[
        ##
        html.Div(
            className="pkcalc-banner",
            children=[
                html.Div(
                    className="pkcalc-title",
                    children=[
                        html.A(
                            id="dash-logo",
                            children=[html.Img(src=app.get_asset_url("nyan.gif"))],
                            href="/",
                        ),
                        html.H2("DRUG MATCHMAKER"),
                    ],
                ), 
                html.Div(
                    className="pkcalc-nav",
                    children=[
                        dcc.Link('Targets', href='/targets'),
                        dcc.Link('Database Information', href='/database'),
                        dcc.Link('Team', href='/team')
                    ],
                ),
            ],#children banner
        ),#div banner
        ##
        html.Div(
            className="container",
            children=[
                html.H3('Marie Bocher'),
                html.P(html.A('LinkedIn Profile', href='https://www.linkedin.com/in/marie-bocher-8b6b5562/')),
                html.Div(
                   className = 'row pkcalc-container',
                   children=[
                       html.Div(
                           className = 'eight columns pkcalc-settings',
                           children = [
                               html.P("Marie's background is in Earth Science. After 7 years of academic research in fluids dynamics and probabilistic forecasting of various solid Earth systems, she transitioned to the Data Science field. She is particularly interested in full-stack data science projects in health, environment and education.")
                           ],#div text
                       ), #divCV
                       html.Div(
                           className = 'four columns',
                           children = [html.Img(src=app.get_asset_url('MB.png'), style={'width':'100%'})]
                       ), #div picture
                   ],#row3 container children 
               ), #row3 container div3 row
                html.Hr(),
                html.H3('Mariana Zorkina'),
                html.P(html.A('LinkedIn Profile', href='https://www.linkedin.com/in/mariana-zorkina-0b103163/')),
                html.Div(
                    className = 'row pkcalc-container',
                    children=[
                        html.Div(
                            className='four columns',
                            children = [html.Img(src=app.get_asset_url('MZ.jpg'), style={'width':'100%'})]
                        ), #div photo
                        html.Div(
                            className = 'eight columns pkcalc-settings',
                            children = [
                                html.P('Mariana is a PhD candidate and lecturer at the University of Zurich. Her background is in sinology, linguistics and literature studies and  she is currently writing a dissertation on computational approaches to analysis of Chinese poetry. She is giving talks on Digital Humanities internationally and has served as editor in several media dedicated to digital transformation of academic research. She is experienced in working in a multicultural environment, speaks English, Russian, Mandarin and German and is interested in NLP projects.')
                            ], 
                        ), #div text
                    ],#children div2 row
                ), #container div2 row
                html.Hr(),
                html.H3('Seamus Dines Muntaner'),
                html.P(html.A('LinkedIn Profile', href='https://www.linkedin.com/in/seamus-dines-muntaner/')),
                html.Div(
                   className = 'row pkcalc-container',
                   children=[
                       html.Div(
                           className = 'eight columns pkcalc-settings',
                           children = [
                               html.P('Seamus is currently enrolled in a Master of Biotechnology at the University of Queensland where he will explore the intersection of health and artificial intelligence. He also works for a drug development group where he will apply this "Drug Matchmaker" to the companies drug assets to facilitate business development. Seamus was born in Spain and grew up in China before completing his secondary and tertiary education in Australia so he speaks English, Mandarin, Catalan and Spanish fluently and hopes to use his languages and cultural background to promote the globalization of healthcare, technology and business.')
                           ],
                       ), #divCV
                       html.Div(
                           className = 'four columns',
                           children = [html.Img(src=app.get_asset_url('S2.jpeg'), style={'width':'100%'})]
                       ), #div picture
                   ],#row3 container children 
               ), #row3 container div3 row
            ], #children main container
        )#div main container
    ]#main children div
)#main div

