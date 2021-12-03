import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pyvis.network import Network


def draw_diagram():
    # Set header title
    st.title('Supply Network Diagram Athena')

    # set the physics layout of the network
    df_data = pd.read_excel('Diagram.xlsx', sheet_name='Sheet1', engine='openpyxl')

    # Implement multiselect dropdown menu for option selection (returns a list)
    multiselect_cluster_list = df_data[['CLUSTER']].drop_duplicates().iloc[:, 0].tolist()
    selected_cluster = st.multiselect('Select cluster(s) to visualize', multiselect_cluster_list)
    df_filtered_cluster = df_data.loc[df_data['CLUSTER'].isin(selected_cluster)].reset_index(drop=True)

    if len(selected_cluster) == 0:
        multiselect_source_list = df_data[['SOURCE']].drop_duplicates().iloc[:, 0].tolist()
        selected_source = st.multiselect('Select source(s) to visualize', multiselect_source_list)
        df_filtered = df_data.loc[df_data['SOURCE'].isin(selected_source)].reset_index(drop=True)

    else:
        multiselect_source_list = df_filtered_cluster[['SOURCE']].drop_duplicates().iloc[:, 0].tolist()
        selected_source = st.multiselect('Select source(s) to visualize', multiselect_source_list)
        df_filtered = df_filtered_cluster.loc[df_filtered_cluster['SOURCE'].isin(selected_source)].reset_index(
            drop=True)

    if len(df_filtered_cluster) == 0:
        if len(df_filtered) == 0:
            df_selected = df_data
        else:
            df_selected = df_filtered
    else:
        if len(df_filtered) == 0:
            df_selected = df_filtered_cluster
        else:
            df_selected = df_filtered

    # Initiate PyVis network object
    net = Network(height='1250px', width='1250px', bgcolor='#F1F1F1', font_color='#7E909A', directed=True)
    # set the physics layout of the network
    net.repulsion(node_distance=420, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)

    sources = df_selected['SOURCE']
    targets = df_selected['TARGET']
    source_value = df_selected['SOURCE_VALUE']
    target_value = df_selected['TARGET_VALUE']
    edge_value = df_selected['EDGE_VALUE']
    source_color = df_selected['SOURCE_COLOR']
    target_color = df_selected['TARGET_COLOR']

    edge_data = zip(sources, targets, source_value, target_value, edge_value, source_color, target_color)

    # load the nodes and edges
    for e in edge_data:
        src = e[0]
        tgt = e[1]
        src_v = e[2]
        tgt_v = e[3]
        edge_v = e[4]
        src_color = e[5]
        tgt_color = e[6]

        net.add_node(src, color=src_color, value=src_v)
        net.add_node(tgt, color=tgt_color, value=tgt_v)
        net.add_edge(src, tgt, value=edge_v)

    net.set_options(""" 
        var options = {
        "nodes": {
            "font": {
                "size": 40
            }
        },
        "edges": {
            "color": {
                "inherit": true
            },
            "smooth": false
        },
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -80000,
                "springLength": 250,
                "springConstant": 0.001
            },
            "minVelocity": 0.75
        }
    } 
    """)

    # label to list the demand sources
    for node in net.nodes:
        df_filtered_countries = df_data[['SOURCE', 'TARGET', 'COUNTRY']].drop_duplicates().reset_index(drop=True)
        target_list = df_filtered_countries[['TARGET']].drop_duplicates().iloc[:, 0].tolist()
        if node['id'] in target_list:
            df_filtered_countries = df_filtered_countries.loc[df_filtered_countries['TARGET'] == node['id']]
            node['title'] = 'Demand source:<br>'
            previous_country = ''
            for index, row in df_filtered_countries.iterrows():
                if row[2] != previous_country:
                    node['title'] += (row[2]) + '<br>'
                    previous_country = row[2]

    # Save and read graph as HTML file (on Streamlit Sharing)
    net.save_graph('supply_network.html')
    html_file = open('supply_network.html', 'r', encoding='utf-8')
    components.html(html_file.read(), height=800)
