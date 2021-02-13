# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 21:03:45 2021

@author: kylej
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import networkx as nx
import numpy as np
import pandas as pd

########
# Data and Variables
########

url_github_SR_data = "https://github.com/kylejwaters/SuperRare-Network/blob/main/superrare%20top%20artists%20and%20collectors.xlsx?raw=True"
tabtitle='----'
myheading='SR Ego Graph Artnome'
githublink='https://github.com/kylejwaters/SuperRare-Network'
sourceurl='https://superrare.co/'  

###########
#Load data
###########

df_collector_artist_pairs = pd.read_excel(url_github_SR_data)    
#Create pairings
df_pairs = pd.DataFrame()
df_pairs["From"] = df_collector_artist_pairs.Artist
df_pairs["To"] = df_collector_artist_pairs.Collector
#Remove duplicates
df_pairs.drop_duplicates(inplace=True)

##################    
#Generate a graph from the dataframe
##################
#G=nx.Graph()
#G=nx.from_pandas_edgelist(df_pairs, 'From', 'To')
#hub_ego = nx.ego_graph(G, sr_user, radius=degree)
#pos = nx.spring_layout(hub_ego)

## with help from https://plotly.com/python/network-graphs/ ##

G = nx.random_geometric_graph(200, 0.125)

# Edges 
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

#Nodes
node_x = []
node_y = []
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append('# of connections: '+str(len(adjacencies[1])))

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network graph made with Python',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )


########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1(myheading),
    dcc.Graph(
        id='SR',
        figure=fig
    ),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A('Data Source', href=sourceurl),
    ]
)

if __name__ == '__main__':
    app.run_server()