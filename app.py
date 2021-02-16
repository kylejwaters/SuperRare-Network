# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 21:03:45 2021

@author: kylej
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import networkx as nx
import numpy as np
import pandas as pd

########
# Data and Variables
########

url_github_SR_data = "https://github.com/kylejwaters/SuperRare-Network/blob/main/superrare%20top%20artists%20and%20collectors.csv?raw=True"
tabtitle='----'
myheading='Who is in your SuperRare Crypto-Art Sphere?'
githublink='https://github.com/kylejwaters/SuperRare-Network'
sourceurl='https://superrare.co/'  

###########
#Load data
###########

df_collector_artist_pairs = pd.read_csv(url_github_SR_data)    
#Create pairings
df_pairs = pd.DataFrame()
df_pairs["From"] = df_collector_artist_pairs.Artist
df_pairs["To"] = df_collector_artist_pairs.Collector
#Remove duplicates
df_pairs.drop_duplicates(inplace=True)
#Remove cases where the artist is connected to him/herself 
df_pairs = df_pairs[df_pairs.From != df_pairs.To].copy()

G=nx.Graph()
G=nx.from_pandas_edgelist(df_pairs, 'From', 'To')

##################    
#Generate a graph from the dataframe
##################
def get_network(sr_user,degree):
    
    hub_ego = nx.ego_graph(G, sr_user, radius=int(degree))
    pos = nx.spring_layout(hub_ego)
    
    ## with help from https://plotly.com/python/network-graphs/ ##
    
    Xv=[pos[k][0] for k in hub_ego.nodes if k != sr_user]
    Yv=[pos[k][1] for k in hub_ego.nodes if k != sr_user]
    Xed=[]
    Yed=[]
    for edge in hub_ego.edges:
        Xed+=[pos[edge[0]][0],pos[edge[1]][0], None]
        Yed+=[pos[edge[0]][1],pos[edge[1]][1], None]
    
    trace3=go.Scatter(x=Xed,
                   y=Yed,
                   mode='lines',
                   line=dict(color='rgb(210,210,210)', width=1),
                   hoverinfo='none'
                   )
    
    node_text = ["{}\nDegree:{}".format(x[0],x[1]) for x in nx.degree(hub_ego) if x[0] != sr_user] 
    
    trace4=go.Scatter(x=Xv,
                   y=Yv,
                   mode='markers',
                   name='net',
                   marker=dict(symbol='circle-dot',
                                 size=10,
                                 color='#6959CD',
                                 line=dict(color='rgb(50,50,50)', width=0.5)
                                 ),
                   text=node_text,
                   hoverinfo='text'
                   )
    
    trace5=go.Scatter(x=[pos[sr_user][0]],
                      y=[pos[sr_user][1]],
                   mode='markers',
                   name='net',
                   marker=dict(symbol='circle-dot',
                                 size=20,
                                 color='red',
                                 line=dict(color='rgb(50,50,50)', width=0.5)
                                 ),
                   text=["{}\nDegree:{}".format(x[0],x[1]) for x in nx.degree(hub_ego) if x[0] == sr_user],
                   hoverinfo='text'
                   )
    
    annot="This networkx.Graph has the ----- layout<br>Code:"+\
    "<a href='http://nbviewer.ipython.org/gist/empet/07ea33b2e4e0b84193bd'> [2]</a>"
    
    if degree == 1:
    
        title_graph = "SuperRare users who currently own an artwork created by {} OR have sold an artwork to {}".format(sr_user,sr_user)
    
    else:
    
        title_graph = "SuperRare users within {} degrees of {}".format(degree,sr_user)
    
    
    data1=[trace3, trace4, trace5]
    fig1=go.Figure(data=data1,layout=go.Layout(
                    title='<br>{}'.format(title_graph),
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        #text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig1['layout']['annotations'][0]['text']=annot
    fig1.update_layout(transition_duration=500)
    
    return fig1

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1(myheading),
    html.H6("Enter your SuperRare username!"),
    html.Div([
        html.Div(["SR User: ",
                  dcc.Input(id='sr-user', value='artnome', type='text')]),
        html.Div(["Degree of Separation: ",
                  dcc.Input(id='degree', value=1, type='text')]),
    ]),
        
    html.Br(),
    
    dcc.Graph(
        id='SuperRare User Network'
    ),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A('Data Source', href=sourceurl),
    ]
)

@app.callback(
    [Output('SuperRare User Network', 'figure')],
    [Input(component_id='sr-user', component_property='value'),
    Input(component_id='degree', component_property='value')]
)
def update_network(sr_user,degree):
    return get_network(sr_user,degree)

if __name__ == '__main__':
    app.run_server()