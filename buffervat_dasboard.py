import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import mysql.connector
import pandas as pd
import plotly.express as px
from pygments.lexers import go
import datetime

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host='192.168.178.20',
    port=3307,
    user='Arduino',
    password='#@Xymox123',
    database='Energielogger',
)

if conn:
    print("Connectie geslaagd...")
    db_cursor = conn.cursor()
    db_cursor.execute("SHOW DATABASES")
    for rows in db_cursor:
        print(rows)
else:
    print("Connectie mislukt..")


# Fetch data from MySQL database
def fetch_data(start_date, end_date):
    #query = f"SELECT datum, elecACTverbruik, elecACTgeleverd FROM buffervat WHERE datum BETWEEN '{start_date}' AND '{end_date}'"
    query = f"SELECT datum, elecACTverbruik, elecACTgeleverd FROM buffervat WHERE datum BETWEEN '{start_date}' AND '{end_date}'"
    df = pd.read_sql(query, conn)
    return df

# Initial data
vandaag = datetime.datetime.now()
gisteren = vandaag - datetime.timedelta(days=1)
morgen = vandaag + datetime.timedelta(days=1)
print('Gisteren: ', gisteren)
print('Vandaag: ', vandaag)
print('Morgen: ', morgen)

df = fetch_data(gisteren, vandaag)
if df.empty:
    print("No Data Available")
print(df)

# Create a simple bar chart using Plotly Express
# fig1 = px.bar(df, x='datum', y='elecACTverbruik', title='Electriciteit Verbruik', color_discrete_sequence=['red'])
# fig2 = px.bar(df, x='datum', y='elecACTgeleverd', title='Electriciteit Geleverd', color_discrete_sequence=['green'])
fig3 = px.bar(df, x='datum', y='elecACTverbruik', title='Electriciteit: Verbruik/Geleverd', color_discrete_sequence=['red'])

# Define the layout of the app
app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col([
            html.H1("Energie overzicht, It Heech 18 HARICH"),
                    #style={'textAlign': 'center'}),
            dcc.DatePickerRange(
                 id='date-picker-range',
                 # start_date='2024-11-29',
                 # end_date='2024-12-01',
                 start_date=gisteren,
                 end_date=vandaag,
                 display_format='YYYY-MM-DD'
            ),
            html.Button('Submit', id='submit-button', n_clicks=0),
            #dcc.Graph(id='example-graph', figure=fig)
        ], width=12)
    ]),
    dbc.Row([
        # dbc.Col([dcc.Graph(id='graph-1', figure=fig1)], width=6),
        # dbc.Col([dcc.Graph(id='graph-2', figure=fig2)], width=6),
        dbc.Col([dcc.Graph(id='graph-3', figure=fig3)], width=6),
    ])
])

# Define the callback to update the graph based on the selected date range
@app.callback(
    #Output('example-graph', 'figure'),
    #[Output('graph-1', 'figure'), Output('graph-2', 'figure'), Output('graph-3', 'figure')],
    #[Output('graph-2', 'figure'), Output('graph-3', 'figure')],
    Output('graph-3', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(n_clicks, start_date, end_date):
    df = fetch_data(start_date, end_date)
    # fig1 = px.scatter(df, x='datum', y='elecACTverbruik', title='Electriciteit Verbruik', color_discrete_sequence=['red'])
    # fig2 = px.line(df, x='datum', y='elecACTgeleverd', title='Electriciteit Geleverd', color_discrete_sequence=['green'])
    # #fig2 = px.scatter
    #fig2 = px.bar

    # Prepare data for two lines
    df_long = pd.melt(df, id_vars=['datum'], value_vars=['elecACTverbruik', 'elecACTgeleverd'], var_name='Type', value_name='Value')
    fig3 = px.line(df_long, x='datum', y='Value', color='Type', title='Electriciteit: Verbruik/Geleverd',
                      labels={'Value': 'Electriciteit', 'datum': 'Date'},
                      color_discrete_map={ 'elecACTverbruik': 'red', 'elecACTgeleverd': 'green'})

    #fig4 = px.scatter(df, x='datum', y='elecTOTgeleverd', title='Elec. Ver/Gel', color_discrete_sequence=['green']),
    #return fig1, fig2, fig3
    return fig3

if __name__ == '__main__':
    app.run_server(debug=True)
