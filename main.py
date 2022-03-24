import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# External Stylesheet for Fonts and Headers
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'top': 0,
    'padding': '20px 10px'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# read the data from csv
data = pd.read_csv('f1_race_results.csv')
data = data[data['grid'] != 0]

# function that creates a dictionary for key/value pair for dropdown

df = px.data.tips()
fig = px.box(data,x="grid",y="position")

def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})

    return dict_list


controls = dcc.Dropdown(
    id='circuitName',
    options=get_options(data['circuitName'].unique()),
    multi=True,
    value=data['circuitName'].unique()
)

sidebar = html.Div(
    [
        html.H2('Circuits', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)

graph1 = html.Div(
    dbc.Row(
        dbc.Col(
            dcc.Graph(id="boxplot", config={
                'displayModeBar': False}), width=6)))


graph2 = html.Div(
    dbc.Row(
        dbc.Col(
            dcc.Graph(id="barchart", config={
                'displayModeBar': False}, animate=True), width=6)))




content = html.Div(
    [
        html.H2('F1 Grid Position Analysis', style=TEXT_STYLE),
        html.Hr(),
        graph2,
        graph1
    ],
    style=CONTENT_STYLE
)


app.layout = html.Div([sidebar, content])

@app.callback(Output('boxplot', 'figure'), Output('barchart','figure'), [Input('circuitName', 'value')])
def update_charts(selected_values):
    df = data[data['circuitName'].isin(selected_values)]

    df_subset = data[['position', 'grid']]
    df_subset['Finish Type'] = pd.cut(df_subset['position'], [0, 3, 10, 100], labels=['Podium Finish', 'Points Finish', 'No Points Finish'])
    #aggregate grid and position by count
    df_agg = df_subset.groupby(['grid', 'Finish Type']).size().reset_index().rename(columns={0:'count'})
    df_agg['prop'] = round(100*(df_agg['count'] / df_agg.groupby('grid')['count'].transform('sum')),2)

    boxplot_fig = px.box(df, x="grid", y="position", color="grid",labels={"grid":"Starting Grid Position", "position": "Finishing Position"}, title="Distribution of Finishing Position based on Starting Grid Position")
    boxplot_fig.update_xaxes(tick0=0, dtick=1)
    boxplot_fig.update_layout(hovermode="x", showlegend=False,hoverlabel=dict(
        bgcolor="white",
        font_size=16,
        font_family="Balto"
    ))

    bar_fig = px.bar(df_agg, x="grid",y="prop", color="Finish Type", labels={"grid":"Starting Grid Position", "prop": "Proportion (%)"}, title="Proportions of Finishing Positions based on Starting Grid")
    bar_fig.update_xaxes(tick0=0, dtick=1)
    bar_fig.update_layout(hovermode="x", hoverlabel=dict(
        bgcolor="white",
        font_size=16,
        font_family="Balto"
    ))
    return boxplot_fig, bar_fig

if __name__ == '__main__':
    app.run_server(debug=True)