import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from sqlalchemy import create_engine

# Conexion a base de datos Postgres
POSTGRES_ADDRESS = 'postgresdb'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'postgres'
POSTGRES_PASSWORD = '12345'
POSTGRES_DBNAME= "postgres"

connection_format = "postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}"

postgres_str = connection_format.format(username=POSTGRES_USERNAME,password=POSTGRES_PASSWORD,ipaddress=POSTGRES_ADDRESS,port=POSTGRES_PORT,dbname=POSTGRES_DBNAME)
cnn = create_engine(postgres_str)
app = dash.Dash(__name__)
df=pd.read_sql_query('select * from bees;', cnn)
df = df.groupby(['state', 'ansi', 'affected_by', 'year', 'state_code'])[['pct_of_colonies_impacted']].mean()
df.reset_index(inplace=True)
chickens_killers = ["Disease", "Other", "Pesticides", "Pests_excl_Varroa", "Unknown", "Varroa_mites"]

# Interfaz de la Aplicacion
app.layout = html.Div(className="container", children=[

    html.Div(id="header", children=[
        html.H2("Dashboard"),
    ]),
    #Mapa
    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018}],
                 multi=False,
                 value=2015
        
                 ),
            
    html.Div(id='output_container', children=[],style={'text-align': 'center'}),
    dcc.Graph(id='my_bee_map', figure={},style={'border-radius':"50px"}),
    #Barras
    
                
    html.Br(),
    html.Div(id='output_container2', children=[],style={'text-align': 'center'}),
    html.Br(),
    dcc.Graph(id='my_bee_map2', figure={}),
    
    html.Br(),
    #Lineas
    dcc.Dropdown(id="slct_impact3",
                 options=[{"label": x, "value":x} for x in chickens_killers],
                 value="Pesticides",
                 multi=False
                 ),
            
    html.Br(),
    html.Div(id='output_container3', children=[],style={'text-align': 'center'}),
    html.Br(),
    dcc.Graph(id='my_bee_map3', figure={})


]
)

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)

def update_graph(option_slctd):
    container = ""

    dff = df.copy()
    dff = dff[dff["year"] == option_slctd]
    dff = dff[dff["affected_by"] == "Disease"]

    # Mapa Plotly
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope="north america",
        color='pct_of_colonies_impacted',
        hover_data=['state', 'pct_of_colonies_impacted'],
        color_continuous_scale=px.colors.sequential.Blues,
        labels={'pct_of_colonies_impacted': 'Percentage of Chickens'},
        template='plotly'
    )

    fig.update_layout(height=700, margin={"r":0,"t":0,"l":0,"b":0})
    fig.layout.plot_bgcolor = '#ffffff'
    fig.layout.paper_bgcolor = '#ffffff'
    return container, fig 

@app.callback(
    [Output(component_id='output_container2', component_property='children'),
     Output(component_id='my_bee_map2', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph2(option_slctd):

    container2 = ""

    dff2 = df.copy()
    dff2 = dff2[dff2["year"] == option_slctd]
    dff2 = dff2[dff2["affected_by"] == "Varroa_mites"]
    
    #Grafico de Barras
    fig2 = px.bar(

        data_frame=dff2,
        x='state',
        y='pct_of_colonies_impacted',
        hover_data=['state', 'pct_of_colonies_impacted'],
        labels={'pct_of_colonies_impacted': 'Percentage of Chickens'},
        template='plotly'
    )

    return container2, fig2

@app.callback(
    [Output(component_id='output_container3', component_property='children'),
     Output(component_id='my_bee_map3', component_property='figure')],
    [Input(component_id='slct_impact3', component_property='value')]
)

def update_graph3(option_slctd):

    container3 = ""

    dff3 = df.copy()
    dff3 = dff3[dff3["affected_by"] == option_slctd]
    dff3 = dff3[((dff3["state"] == "New York") | (dff3["state"] == "New Mexico")
    | (dff3["state"] == "New Jersey") | (dff3["state"] == "Texas") | (dff3["state"] == "California"))]
    #Grafico de Lineas
    fig3 = px.line(
        data_frame=dff3,
        x='year',
        y='pct_of_colonies_impacted',
        color='state',
        template='plotly'
    )

    return container3, fig3


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)
