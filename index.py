import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import targets, database, team

server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])

def display_page(pathname):
    if pathname == '/' or pathname == '/targets':
        return targets.layout
    elif pathname == '/database':
        return database.layout
    elif pathname == '/team':
        return team.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=False)
