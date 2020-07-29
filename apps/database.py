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
layout = html.Div(
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
                html.H3('Data sources and engineering'),
                html.Div(
                    className = 'row pkcalc-container',
                    children=[
                        html.Div(
                            #className = 'four columns',
                            children = [html.Img(
                                src=app.get_asset_url("linear_database2.svg"), 
                                style={'width':'100%'}
                            ),
                                       ],#children
                        ),
                    ],#children div1
                ), #container div1
                html.Hr(),
                html.H3('Database statistics'),
                html.Div(
                    className = 'row pkcalc-container',
                    children=[
                        html.Div(
                            #className = 'four columns',
                            children = [html.Img(
                                src=app.get_asset_url("database_statistics.svg"), 
                                style={'width':'100%'}),
                                       ],#children
                        ),
                    ],#children div2
                ), #container div2

                html.Hr(),
                html.H3('Ranking metrics: PMI'),
                html.Div(
                    className = 'row pkcalc-container',
                    children=[
                        html.Div(
                            #className = 'four columns',
                            children = [html.Img(
                                src=app.get_asset_url("PMI.svg"), 
                                style={'width':'100%'}),
                                       ],#children
                        ),
                    ],#children div4
                ), #container div4
                html.Hr(),
                html.H3('Time series forecasting'),
                html.Div(
                    className = 'row pkcalc-container',
                    children=[
                        html.Div(
                            #className = 'four columns',
                            children = [html.Img(
                                src=app.get_asset_url("ML_calculation.svg"), 
                                style={'width':'100%'}),
                                       ],#children
                        ),
                    ],#children div5
                ), #container div5
            ], #children container
        )#div container
    ]#main children div
)#main div