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
import pandas as pd

########
# Data and Variables
########

url_github_SR_data = "https://github.com/kylejwaters/SuperRare-Network/blob/main/superrare%20top%20artists%20and%20collectors_2021-02-27.csv?raw=True"
tabtitle='SuperRare Network Viewer'
myheading='Who is in your SuperRare CryptoArt Sphere?'
githublink='https://github.com/kylejwaters/SuperRare-Network'
sourceurl='https://superrare.co/'  
kyletwitter = "https://twitter.com/waters_ky"

###########
#Load data
###########

df_collector_artist_pairs = pd.read_csv(url_github_SR_data)    
#Create pairings
df_pairs = pd.DataFrame()
#From is artist, to is collector
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
def get_network(sr_user):
    
    hub_ego = nx.ego_graph(G, sr_user, radius=1)
    pos = nx.spring_layout(hub_ego)
    
    ## with help from https://plotly.com/python/network-graphs/ ##
    
    ###
    #Edges 
    ###
    
    Xv=[pos[k][0] for k in hub_ego.nodes if k != sr_user]
    Yv=[pos[k][1] for k in hub_ego.nodes if k != sr_user]
    Xed=[]
    Yed=[]
    for edge in hub_ego.edges:
        Xed+=[pos[edge[0]][0],pos[edge[1]][0], None]
        Yed+=[pos[edge[0]][1],pos[edge[1]][1], None]
    
    #Edges 
    trace3=go.Scatter(x=Xed,
                   y=Yed,
                   mode='lines',
                   line=dict(color='rgb(200,200,200)', width=1),
                   hoverinfo='none'
                   )
    
    node_text = ["{}\nDegree:{}".format(x[0],x[1]) for x in nx.degree(hub_ego) if x[0] != sr_user] 
    
    profile = "https://superrare.co/{}".format(sr_user)
    title_graph = "SR users connected to {} ({})".format(sr_user, profile)
    mode_ = "markers+text"
    
    #Nodes
    trace4=go.Scatter(x=Xv,
                   y=Yv,
                   mode=mode_,
                   name='net',
                   marker=dict(symbol='circle-dot',
                                 size=10,
                                 color='#6959CD',
                                 line=dict(color='rgb(50,50,50)', width=0.5)
                                 ),
                   text=["{}".format(x[0]) for x in nx.degree(hub_ego) if x[0] != sr_user],
                   hovertext=node_text,
                   hoverinfo='text',
                   textposition="bottom center",
                   )
    
    #SR user node
    trace5=go.Scatter(x=[pos[sr_user][0]],
                      y=[pos[sr_user][1]],
                   mode=mode_,
                   name='net',
                   marker=dict(symbol='circle-dot',
                                 size=20,
                                 color='red',
                                 line=dict(color='rgb(50,50,50)', width=0.5)
                                 ),
                   text=["{}".format(x[0]) for x in nx.degree(hub_ego) if x[0] == sr_user],
                   hovertext=["{}\nDegree:{}".format(x[0],x[1]) for x in nx.degree(hub_ego) if x[0] == sr_user],
                   hoverinfo='text'
                   )
    
    #annot="This networkx.Graph has the ----- layout<br>Code:"+\
    #"<a href='http://nbviewer.ipython.org/gist/empet/07ea33b2e4e0b84193bd'> [2]</a>"
    
    data1=[trace3, trace4, trace5]
    fig1=go.Figure(data=data1,layout=go.Layout(
                    title='<br>{}'.format(title_graph),
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    #annotations=[ dict(
                    #    #text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                    #    showarrow=False,
                    #    xref="paper", yref="paper",
                    #    x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    #fig1['layout']['annotations'][0]['text']=annot
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
        
    html.Br(),
    
    dcc.Graph(
        id='User SuperRare Network')
    ]),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A('Created by Kyle Waters', href=kyletwitter),
    html.Br(),
    html.A('Source (Data as of February 27, 2021)', href=sourceurl)
    ]
)

@app.callback(
    Output('User SuperRare Network', 'figure'),
    [Input(component_id='sr-user', component_property='value')]
)
def update_network(sr_user):
    return get_network(sr_user)

if __name__ == '__main__':
    app.run_server()