#This dashboard is a modified version of https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-pk-calc

#MODULES
#Core components
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import textwrap

from app import app

#Visualization
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#SQLite libraries
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine

#Custom modules
import sys
sys.path.insert(0,'./modules')

import sql_helper
import counts


# DATA
#Load DB connection
engine = create_engine('sqlite:///data/20200729pubmed_mini.db', echo=False)
con = engine.connect()


#Default values for the first view. These global variables are overwritten by update_table callback.
search_term = (1841,'ANG','Angiogenin')
df = sql_helper.get_rankings(search_term[0], engine)
drug_df = sql_helper.get_drug_info(search_term[0], engine)
drug_df_filt = drug_df.copy() #This is a shortcut way of dealing with filtering while overwriting global df. 
df_filt = df.copy()

#Explanatory popups in the datatable

#https://community.plotly.com/t/datatable-tooltip-data-argument-request-for-example/36276
#https://community.plotly.com/t/dash-datatable-tooltips/6327/15
#https://community.plotly.com/t/how-to-change-dash-table-tooltip-size/27661

#It would be better to have tooltip only on hover over table header, but this is impossible in current dash version.
#Track here https://github.com/plotly/dash-table/issues/295

#This is a more explicit way to create the tooltip. Shows tips for all cells
explanations = {'disease': 'disease name', 
                'f0': 'Ratio of joint occurrences target+disease to number of all abstracts, multiplied by 10**6', 
                'f1': 'Ratio of joint occurrences target+disease to number of abstracts mentioning target. Shows importance of disease to a given target.', 
                'f2': 'Ratio of joint occurrences together to number of abstracts mentioning disease. Shows importance of target to a given disease.', 
                'pmi': 'Pointwise mutual information. Shows how bigger than random are the chances that the two items co-occur,     but tends to show high rank for rare items. ',}
tooltip_data= [{c:
        {
            'type': 'text',
            'value': explanations[c],
            'delay':100, 'duration': 3000
        } for c in ['f0', 'f1', 'f2', 'pmi']} #shows info on all columns but 'disease'. Otherwise just use 'df.columns'
               for row in df.to_dict('rows') #remove if only want tooltip on the first row
              ]

#This is a shorter way, but only shows info for the first row in the table
# tooltip_data = [{
#                 'f0': 'Ratio of joint occurrences target+disease to number of all abstracts, multiplied by 10^6', 
#                 'f1': 'Ratio of joint occurrences target+disease to number of abstracts mentioning target. Shows importance of disease to a given target.', 
#                 'f2': 'Ratio of joint occurrences together to number of abstracts mentioning disease. Shows importance of target to a given disease.', 
#                 'pmi': 'Pointwise mutual information. Shows how bigger than random are the chances that the two items co-occur,     but tends to show high rank for rare items. '
# }]


# STYLE

table_header_style = {
    "backgroundColor": "rgb(2,21,70)",
    "color": "white",
    "textAlign": "center",
}


# APP
PAGE_SIZE = 5

layout = html.Div(
    className="",
    children=[
        #html.H1('Yay'),v
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
            ],
        ),
        ##
        html.Div(
            className="container",
            children=[
                html.Div(
                    className="row pkcalc-container",
                    children=[
                        html.Div(
                            className="four columns",
                            children=[
                                html.H3('Search')
                            ]
                        ),
                        html.Div(
                            className="eight columns",
                            children=[
                                html.H3('Drugs developed for given target')
                            ]
                        )]
                ),
                html.Div(
                    className="row pkcalc-container",
                    style={},
                    children=[
                        html.Div(
                            className="four columns pkcalc-settings",
                            children=[
                                html.Div([
                                    #https://dash.plotly.com/dash-core-components/input                                 
                                    dcc.Input(id="input1", type="text", placeholder="Enter the target abbreviation..", debounce=True),
                                        ]),#div search field
                                    html.Div(id="output"),
                                    ], #children "four columns pkcalc-settings"
                                ),#div "four columns pkcalc-settings"
                        
                        html.Div(
                            className="eight columns pkcalc-data-table",
                            children=[
                                dash_table.DataTable(
                                    style_cell={'whiteSpace': 'normal'},
                                    id='drug_table',
                                    columns=[{"name": i, "id": i} for i in drug_df.columns],
                                    data = drug_df.to_dict('records'),
                                    page_current=0,
                                    page_size=10, #change this for number of rows displayed on one page in table
                                    page_action='native',
                                    
                                    filter_action='native',
                                    filter_query='',
                                    
                                    sort_action='native',
                                    
                                    #This part not in example code. Delete if needed.
                                    #This adds a column with row selection. Need to use this as output in the next graph. 
                                    #row_selectable="single",
                                    #selected_rows=[], 
                                    
                                    #sort_mode='multi',
                                    #Tooltip stuff
                                    tooltip_data = tooltip_data,
                                    
                                    sort_by= [],
                                    style_header=table_header_style, #style added
                                            ),#dash_table.DataTable
                                    html.Div(id='datatable-interactivity-container'),
                                ], #children "eight columns pkcalc-data-table"
                            ),#div "eight columns pkcalc-data-table"
                    ]#children row1                    
                ),#div row1
                html.Hr(),
                html.H3('Target-disease correlations'),
                html.Div(
                    className="row pkcalc-container",
                    style={},
                    children=[
                        html.Div(
                            className="twelve columns pkcalc-data-table",
                            children=[
                                dash_table.DataTable(
                                    style_cell={'whiteSpace': 'normal'},
                                    id='table-paging-with-graph',
                                    columns=[{"name": i, "id": i} for i in df.columns],
                                    data = df.to_dict('records'),
                                    page_current=0,
                                    page_size=10, #change this for number of rows displayed on one page in table
                                    page_action='native',
                                    
                                    filter_action='native',
                                    filter_query='',
                                    
                                    sort_action='native',
                                    
                                    #This part not in example code. Delete if needed.
                                    #This adds a column with row selection. Need to use this as output in the next graph. 
                                    row_selectable="single",
                                    selected_rows=[], 
                                    
                                    sort_mode='multi',
                                    #Tooltip stuff
                                    tooltip_data = tooltip_data,
                                    
                                    #Hide columns - not used, can add if necessary
#                                     style_cell_conditional=[
#                                         {
#                                             'if': {'column_id': 'index'},
#                                             'display': 'none'
#                                         }
#                                     ],
                                    
                                    sort_by= [],
                                    style_header=table_header_style, #style added
                                            ),#dash_table.DataTable
                                    html.Div(id='datatable-interactivity-container'),
                                
                                ], #children "eight columns pkcalc-data-table"
                        ), #table2 div                 
                    ]#children row2
                ),#div row2
                html.Hr(),
                html.H3('Disease statistics'),
                html.Div(
                    className="row pkcalc-container",
                    style={},
                    children=[
                        html.Div(
                            className="six columns pkcalc-settings",
                            children=[
                                #html.P('Articles mentioning disease per year'),
                                dcc.Graph(id='dis_year')
                            ]#children row2 div1
                        ), #row2 Div1
                        html.Div(
                            className="six columns pkcalc-settings",
                            children=[
                                #html.P('Articles mentioning disease per year'),
                                dcc.Graph(id='ct_year')
                            ]#children row2 div2
                        )#row2 Div2       

                    ], #children row3
                ),#div row3                
            ], #children container
        )#div container
    ]#main children div
)#main div
    
    
#CALLBACKS & FUNCTIONS
# Update table: load new data on search or update on sort & filter

@app.callback(
    [Output('table-paging-with-graph', 'data'),
    Output('output','children')],
    [Input('input1', 'value'),]
    )

def update_table(input1):
    
    info = sql_helper.get_target_id(input1, engine)
    
    if info == 'NaN':
        if not input1:
            return [], ''#u'Target not found'
        else:
            suggestions = sql_helper.find_similar(input1, engine)
            return [], (html.P(['Target not found.', html.Br(), 'Maybe you meant:', html.Br(), html.Br(), ', '.join(suggestions)]))
    
    else:
        try:
            df = sql_helper.get_rankings(info[0], engine)
            df = df.reset_index().drop(columns='index')

            return df.to_dict('records'), (html.P(['Found:', html.Br(), html.Br(), f'Abbr: {info[1]}', html.Br(), f'Full: {info[2]}']))

        except ValueError:
            return [], (html.P(['No articles match the target:', html.Br(), html.Br(), f'Abbr: {info[1]}', html.Br(), f'Full: {info[2]}']))




#Update table 2

@app.callback(
    Output('drug_table', 'data'),
    [Input('input1', 'value')]
)

def update_table2(input1):
    
    info = sql_helper.get_target_id(input1, engine)
    
    if info == 'NaN':
        return []
    
    else:
        try:  
            drug_df = sql_helper.get_drug_info(info[0], engine)
            drug_df = drug_df.reset_index().drop(columns='index')

            return drug_df.to_dict('records')

        except ValueError:
            return []

#Update figure one: Number of articles published on disease per year


@app.callback(
    Output("dis_year","figure"),
    [Input('table-paging-with-graph', 'derived_virtual_selected_rows'),
     Input('table-paging-with-graph', "derived_virtual_data"),
    ])

 
def update_graph(derived_virtual_selected_rows, rows):
    '''
    Takes information from the selected row in the datatable and 
    returns a bar chart with 
        - number of clinical trials for a selected disease per year 
        - disease name in the title
        - line chart for percentage of clinical trials for disease from all trials per years
        IMPORTANT: takes a precomputed list of number of trials per year. See counts.py
    If nothing is given, returns an empty figure. If there is no data found, returns empty figure indicating trials were not
        found.
    Arguments:
        selected rows: row with disease selected from the datatable     
    Returns:
        fig: plotly.go barchart
    '''
    
    if derived_virtual_selected_rows == []:

        fig = go.Figure(
            data = []
        )
        
    else:
        
        dff = pd.DataFrame(rows)
        
        disease_name = dff['disease'].iloc[derived_virtual_selected_rows[0]]
        disease_id = sql_helper.get_dis_id(disease_name, engine)
    
        dis_print = '<br>'.join(textwrap.wrap(disease_name, width=40)) if len(disease_name)>40 else disease_name

        #dis_id = sql_helper.get_dis_id(disease_name, engine)
        dis_years = sql_helper.get_pubmed_year(disease_id, engine)
        
        if dis_years == []:
            fig = go.Figure(
            data = [
                   ],

            layout = go.Layout(title=go.layout.Title(text = f'Publications not found:<br>{dis_print}', 
                                                     font = dict(size=14)))
            )
        
        
        else:
            dis_counts = counts.get_count_abstracts(dis_years)
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(
                go.Bar(x=dis_counts["year"], y=dis_counts["count"], name="No of publications", marker_color = 'rgb(2,21,70)'),
                secondary_y=False
            )

            fig.add_trace(
                go.Scatter(x=dis_counts["year"], y=dis_counts["percentage"], name="% from total", marker_color='red', mode='lines'),
                secondary_y=True
            )

            fig.update_layout(
                title_text=f"Publications per year:<br>{dis_print}",
                titlefont = dict(size=14)
            )

            fig.update_yaxes(
                title_text=f"Annual publications",
                secondary_y=False
            )

            fig.update_yaxes(
                title_text="% of publications that year",
                secondary_y=True
            )

            fig.update_xaxes(
                title_text="Year"
            )
            
            fig.update_layout(legend=dict(
                yanchor="bottom",
                y=-0.5, 
                xanchor="center",
                x=0.5
))
            
    return fig        



#Update graph 2

@app.callback(
    Output("ct_year","figure"),
    [Input('table-paging-with-graph', 'derived_virtual_selected_rows'),
     Input('table-paging-with-graph', "derived_virtual_data"),
    ])


def update_graph2(derived_virtual_selected_rows, rows):
    '''
    Takes information from the selected row in the datatable and 
    returns a bar chart with 
        - number of clinical trials for a selected disease per year 
        - disease name in the title
        - line chart for percentage of clinical trials for disease from all trials per years
        IMPORTANT: takes a precomputed list of number of trials per year. See counts.py
    If nothing is given, returns an empty figure. If there is no data found, returns empty figure indicating trials were not
        found.
    Arguments:
        selected rows: row with disease selected from the datatable     
    Returns:
        fig: plotly.go barchart
    '''
    if derived_virtual_selected_rows == []:

        fig = go.Figure(
            data = []
        )
        
    else:
        
        dff = pd.DataFrame(rows)
        
        disease_name = dff['disease'].iloc[derived_virtual_selected_rows[0]]
        #disease_id = sql_helper.get_dis_id(disease_name, engine)
        dis_print = '<br>'.join(textwrap.wrap(disease_name, width=50)) if len(disease_name)>50 else disease_name
    

        #dis_id = sql_helper.get_dis_id(disease_name, engine)
        ct_years = sql_helper.get_ct_year(disease_name, engine)
        
        if ct_years == []:
            fig = go.Figure(
            data = [
                   ],

            layout = go.Layout(title=go.layout.Title(text = f'Trials not found:<br>{dis_print}', 
                                                     font = dict(size=14)))
            )
        
        
        else:
            dis_counts = counts.get_count_dataframe(ct_years)
            dis_id = sql_helper.get_dis_id(disease_name, engine)
            dis_pred = sql_helper.ct_forecast(dis_id, engine)
            
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(
                go.Bar(x=dis_counts["year"], y=dis_counts["count"], name="No of trials", marker_color = 'rgb(2,21,70)'),
                secondary_y=False
            )
            if dis_pred == [0,0]:
                fig.add_trace(
                    go.Scatter(x = [2020, 2021], y=[i for i in dis_pred], name = "Forecast", marker_color = 'green', mode='lines'),
                    secondary_y=False
                )
            else:
                fig.add_trace(
                    go.Bar(x = [2020, 2021], y=[i for i in dis_pred], name = "Forecast", marker_color = 'green', ),
                    secondary_y=False
                )
            
            fig.add_trace(
                go.Scatter(x=dis_counts["year"], y=dis_counts["percentage"], name="% from total", marker_color='red', mode='lines'),
                secondary_y=True
            )
            

            fig.update_layout(
                title_text=f"Clinical trials per year:<br>{dis_print}",
                titlefont = dict(size=14),
            )

            fig.update_yaxes(
                title_text=f"Annual trials",
                secondary_y=False
            )

            fig.update_yaxes(
                title_text="% of trials that year",
                secondary_y=True
            )

            fig.update_xaxes(
                title_text="Year",
                #range = [1999, 2025]
            )
            
            fig.update_layout(legend=dict(
                yanchor="bottom",
                y=-0.5, 
                xanchor="center",
                x=0.5
))
            
    return fig


#LEGACY CODE

# #Sort table: custom 

# operators = [['ge ', '>='],
#              ['le ', '<='],
#              ['lt ', '<'],
#              ['gt ', '>'],
#              ['ne ', '!='],
#              ['eq ', '='],
#              ['contains '],
#              ['datestartswith ']]


# def split_filter_part(filter_part):
#     for operator_type in operators:
#         for operator in operator_type:
#             if operator in filter_part:
#                 name_part, value_part = filter_part.split(operator, 1)
#                 name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

#                 value_part = value_part.strip()
#                 v0 = value_part[0]
#                 if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
#                     value = value_part[1: -1].replace('\\' + v0, v0)
#                 else:
#                     try:
#                         value = float(value_part)
#                     except ValueError:
#                         value = value_part

#                 # word operators need spaces after them in the filter string,
#                 # but we don't want these later
#                 return name, operator_type[0].strip(), value

#     return [None] * 3



#Update table when sorting and filtering are set to 'custom'

# @app.callback(
#     [Output('table-paging-with-graph', "data"),
#     Output('output','children')],
#     [Input('table-paging-with-graph', "page_current"),
#      Input('table-paging-with-graph', "page_size"),
#      Input('table-paging-with-graph', "sort_by"),
#      Input('table-paging-with-graph', "filter_query"),
#      Input("input1", "value")])

# def update_table(page_current, page_size, sort_by, filter, input1):
#     '''
#     Updates the datatable shown on dashboard. 
#     If input1 is updated (new search target), it pulls information on target from SQLite and displays a new table.
#     For other inputs (sort_by, filter etc.) if updates the view of the table based on selected method.
#     IMPORTANT When this function is run, it overrides the global df variable in order to be able to pass new data to other
#         callbacks.
        
#     Arguments:
#         page_current: current page number
#         page_size: number of rows to return per page
#         sort_by: sorting mechanism
#         filter:
#         input1: search input from the search field
    
#     Returns:
#         df: a new dataframe to display, parced according to set page size
#     '''
#     #TODO with saving things to global df there is no way to return all data after filtering.
#     #this assigns updated dataframes to the global variable. Need to do this to use new data for callbacks.
#     global df
#     global search_term
#     global df_filt
    
#     #see https://dash.plotly.com/advanced-callbacks
#     ctx = dash.callback_context
#     event_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     if event_id == 'input1':
#         info = sql_helper.get_target_id(input1, engine)
    
#         if info == 'NaN':
            
#             suggestions = sql_helper.find_similar(input1, engine)
#             if len(suggestions) ==0:
#                 return [], u'Target not found'
#             else:
#                 return [], (html.P(['Target not found.', html.Br(), 'Maybe you meant:', html.Br(), html.Br(), ', '.join(suggestions)]))

#         else:
#             try:
#                 df = sql_helper.get_rankings(info[0], engine)
#                 df_filt = df.copy()
#                 search_term = info
#                 #return df.to_dict('records')
                
#                 #TODO Because of this part row selection on all pages but first return first page resuls
#                 #Can either somehow rewrite the df or assign a hidden column with index and refer to it, not the automatic index
#                 return df.iloc[page_current*page_size: (page_current + 1)*page_size].to_dict('records'),         (html.P(['Found:', html.Br(), html.Br(), f'Abbr: {search_term[1]}', html.Br(), f'Full: {search_term[2]}']))
            
#             except ValueError:
#                 search_term = info
#                 return [], (html.P(['No articles match the target:', html.Br(), html.Br(), f'Abbr: {search_term[1]}', html.Br(), f'Full: {search_term[2]}']))
            
#     else:
#         #see https://dash.plotly.com/datatable/interactivity
#         filtering_expressions = filter.split(' && ')
#         if filtering_expressions == ['']:
#             return df_filt.iloc[page_current*page_size: (page_current + 1)*page_size].to_dict('records'), (html.P(['Found:', html.Br(), html.Br(), f'Abbr: {search_term[1]}', html.Br(), f'Full: {search_term[2]}']))
        
#         else:
#             dff = df
#             for filter_part in filtering_expressions:
#                 col_name, operator, filter_value = split_filter_part(filter_part)

#                 if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
#                     # these operators match pandas series operator method names
#                     dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
#                 elif operator == 'contains':
#                     dff = dff.loc[dff[col_name].str.contains(filter_value)]
#                 elif operator == 'datestartswith':
#                     # this is a simplification of the front-end filtering logic,
#                     # only works with complete fields in standard format
#                     dff = dff.loc[dff[col_name].str.startswith(filter_value)]

#             if len(sort_by):
#                 dff = dff.sort_values(
#                     [col['column_id'] for col in sort_by],
#                     ascending=[
#                         col['direction'] == 'asc'
#                         for col in sort_by
#                     ],
#                     inplace=False
#                 )

#             #This rewrites the global df. Need to do this to be able to pass the right data to callbacks after table is updated
#             df = dff
#             return df.iloc[page_current*page_size: (page_current + 1)*page_size].to_dict('records'), (html.P(['Found:', html.Br(), html.Br(), f'Abbr: {search_term[1]}', html.Br(), f'Full: {search_term[2]}']))



# @app.callback(
#     Output('drug_table', "data"),
#     [Input('drug_table', "page_current"),
#      Input('drug_table', "page_size"),
#      Input('drug_table', "sort_by"),
#      Input('drug_table', "filter_query"),
#      Input("input1", "value")])

# def update_table2(page_current, page_size, sort_by, filter, input1):
#     #TODO with saving things to global df there is no way to return all data after filtering.
    
#     #this assigns updated dataframes to the global variable. Need to do this to use new data for callbacks.
#     global drug_df
#     global drug_df_filt
    
#     #see https://dash.plotly.com/advanced-callbacks
#     ctx = dash.callback_context
#     event_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     info = sql_helper.get_target_id(input1, engine)
#     if event_id == 'input1':
    
#         if info == 'NaN':
#             return []

#         else:
#             try:
#                 drug_df = sql_helper.get_drug_info(info[0], engine)
#                 drug_df_filt = drug_df.copy()
                
#                 search_term = info
#                 return drug_df.iloc[page_current*page_size: (page_current + 1)*page_size].to_dict('records')
            
#             except ValueError:
#                 search_term = info
#                 return []
            
#     else:
#         #see https://dash.plotly.com/datatable/interactivity
#         filtering_expressions = filter.split(' && ')

#         if filtering_expressions == ['']:
#             return drug_df_filt.iloc[page_current*page_size: (page_current + 1)*page_size].to_dict('records')
#         else:
#             dff = drug_df
#             for filter_part in filtering_expressions:
#                 col_name, operator, filter_value = split_filter_part(filter_part)

#                 if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
#                     # these operators match pandas series operator method names
#                     dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
#                 elif operator == 'contains':
#                     dff = dff.loc[dff[col_name].str.contains(filter_value)]
#                 elif operator == 'datestartswith':
#                     # this is a simplification of the front-end filtering logic,
#                     # only works with complete fields in standard format
#                     dff = dff.loc[dff[col_name].str.startswith(filter_value)]

#             if len(sort_by):
#                 dff = dff.sort_values(
#                     [col['column_id'] for col in sort_by],
#                     ascending=[
#                         col['direction'] == 'asc'
#                         for col in sort_by
#                     ],
#                     inplace=False
#                 )

#             #This rewrites the global df. Need to do this to be able to pass the right data to callbacks after table is updated
#             drug_df = dff
#             #print('dff happening')
#             return drug_df.iloc[page_current*page_size: (page_current + 1)*page_size].to_dict('records')
    
        


#LEGACY CODE
#Simpler graph updates


#Simpler graph 1 with only absolute frequencies

# def update_graph(selected_rows, page_current, page_size):
#     '''
#     Takes information from the selected row in the datatable and 
#     returns a bar chart with number of pubmed articles for a selected disease per year & disease name in the title.
#     If nothing is given, returns an empty figure.
    
#     Arguments:
#         selected rows: row with disease selected from the datatable     
#     Returns:
#         fig: plotly.go barchart
#     '''
#     if not selected_rows:
#         #https://community.plotly.com/t/return-an-empty-graph/13061/2
#         fig = go.Figure(
#             data = []
#         )
#     else:        
#         index = page_current*page_size + selected_rows[0]
#         dff = df.iloc[index]
        
#         disease_name = dff['disease']
    

#         dis_id = sql_helper.get_dis_id(disease_name, engine)
#         dis_years = sql_helper.get_dis_year(dis_id, engine)
#         counts = dis_years.groupby('year').size().tolist()

#         fig = go.Figure(
#         data = [
#               go.Bar(name = 'Articles on disease per year', x=[i for i in range(2009, 2021)], y=[i for i in counts]),
#                ],

#         layout = go.Layout(title=go.layout.Title(text = f'Articles per year:<br>{disease_name}', font = dict(size=14)))
#         )

#     return fig


#Update figure 2: Number of clinical trials for given disease per year


#Same grah without predictions

# def update_graph2(selected_rows, page_current, page_size):
#     '''
#     Takes information from the selected row in the datatable and 
#     returns a bar chart with 
#         - number of clinical trials for a selected disease per year 
#         - disease name in the title
#         - line chart for percentage of clinical trials for disease from all trials per years
#         IMPORTANT: takes a precomputed list of number of trials per year. See counts.py
#     If nothing is given, returns an empty figure. If there is no data found, returns empty figure indicating trials were not
#         found.
#     Arguments:
#         selected rows: row with disease selected from the datatable     
#     Returns:
#         fig: plotly.go barchart
#     '''
#     if not selected_rows:
#         #https://community.plotly.com/t/return-an-empty-graph/13061/2
#         fig = go.Figure(
#             data = []
#         )
        
#     else:
#         index = page_current*page_size + selected_rows[0]
#         dff = df.iloc[index]
        
#         disease_name = dff['disease']
#         dis_print = '<br>'.join(textwrap.wrap(disease_name, width=50)) if len(disease_name)>50 else disease_name
    

#         #dis_id = sql_helper.get_dis_id(disease_name, engine)
#         ct_years = sql_helper.get_ct_year(disease_name, engine)
        
#         if ct_years == []:
#             fig = go.Figure(
#             data = [
#                    ],

#             layout = go.Layout(title=go.layout.Title(text = f'Trials not found:<br>{dis_print}', 
#                                                      font = dict(size=14)))
#             )
        
        
#         else:
#             dis_counts = counts.get_count_dataframe(ct_years)
            
#             fig = make_subplots(specs=[[{"secondary_y": True}]])

#             fig.add_trace(
#                 go.Bar(x=dis_counts["year"], y=dis_counts["count"], name="No of trials", marker_color = 'rgb(2,21,70)'),
#                 secondary_y=False
#             )

#             fig.add_trace(
#                 go.Scatter(x=dis_counts["year"], y=dis_counts["percentage"], name="% from total", marker_color='red', mode='lines'),
#                 secondary_y=True
#             )

#             fig.update_layout(
#                 title_text=f"Clinical trials per year:<br>{dis_print}",
#                 titlefont = dict(size=14)
#             )

#             fig.update_yaxes(
#                 title_text=f"Annual trials",
#                 secondary_y=False
#             )

#             fig.update_yaxes(
#                 title_text="% of trials that year",
#                 secondary_y=True
#             )

#             fig.update_xaxes(
#                 title_text="Year"
#             )
            
#             fig.update_layout(legend=dict(
#                 yanchor="bottom",
#                 y=-0.5, 
#                 xanchor="center",
#                 x=0.5
# ))
            
#     return fig



#Code for simple graph with absolute counts from CT

# def update_graph2(selected_rows, page_current, page_size):
#     '''
#     Takes information from the selected row in the datatable and 
#     returns a bar chart with number of clinical trials for a selected disease per year & disease name in the title.
#     If nothing is given, returns an empty figure. If there is no data found, returns empty figure indicating trials were not
#         found.
#     Arguments:
#         selected rows: row with disease selected from the datatable     
#     Returns:
#         fig: plotly.go barchart
#     '''
#     if not selected_rows:
#         #https://community.plotly.com/t/return-an-empty-graph/13061/2
#         fig = go.Figure(
#             data = []
#         )
        
#     else:
#         index = page_current*page_size + selected_rows[0]
#         dff = df.iloc[index]
        
#         disease_name = dff['disease']
    

#         #dis_id = sql_helper.get_dis_id(disease_name, engine)
#         ct_years = sql_helper.get_ct_year(disease_name, engine)
        
#         if ct_years == []:
#             fig = go.Figure(
#             data = [
#                    ],

#             layout = go.Layout(title=go.layout.Title(text = f'Trials not found:<br>{disease_name}', font = dict(size=14)))
#             )
        
        
#         else:
#             fig = go.Figure(
#             data = [
#                   go.Bar(name = 'Trials on disease per year', x=[i for i in ct_years], y=[ct_years[i] for i in ct_years]),
#                    ],

#             layout = go.Layout(title=go.layout.Title(text = f'Trials per year:<br>{disease_name}', font = dict(size=14)))
#             )

#     return fig
