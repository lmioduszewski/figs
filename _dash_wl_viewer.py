import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly import graph_objs
import plotly
import plotly.express as px
from figs import _ids as ids
from dash import Dash, dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import io
import pickle
import base64
import random
from dash.exceptions import PreventUpdate
import copy
import os
from figs._fig import Template, Fig
import json
from pathlib import Path
import plotly.io as pio
from bokeh_fig import BokehFig
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource

canvas_height = 750
#canvas_width = 1000
percent_progress = 0
xaxis_startingtype = 'linear'
yaxis_startingtype = 'linear'
xaxis_color = '#888'
yaxis_color = '#888'
clickmode = 'event'
figure_bgcolor = '#222222'
default_dragmode = 'pan'
trace_drawingmode = 'lines'
savefile_name = 'sample.json'
config = dict({'scrollZoom': True,
               'displaylogo': False,
               'autosizable':True,
               'responsive': True,
               })
#  Define the Water Level DataFrame to plot from
wls_df = pd.read_excel(Path.home() / 'Python/data/Tehaleh_wls.xlsx', sheet_name='WellDD')
wls_df = wls_df.set_index('Date Time')

def render(app: Dash) -> dcc.Graph:
    
    fig = Fig()
    
    @app.callback(
        Output(ids.WATER_LEVELS, 'figure'),
        Input(ids.OPEN_FIG, 'contents'),
        Input(ids.WATER_LEVELS, 'clickData'),
        State(ids.WATER_LEVELS, 'figure'),
        prevent_initial_call=True)
    def update_wl_fig(upload_contents, clickData, fig_state):
        if callback_context.triggered_id == ids.OPEN_FIG:
            """file to open must be a json representation of a Plotly fig"""
            # Split the content into metadata and data itself
            content_type, content_string = upload_contents.split(',')
            # Decode the base64 string
            decoded = base64.b64decode(content_string)
            json_fig = json.loads(decoded)
            fig_to_open = go.Figure(json_fig)
            return fig_to_open
        if callback_context.triggered_id == ids.WATER_LEVELS:
            curve_number = clickData['points'][0]['curveNumber']
            return

    @app.callback(
        Output(ids.DATA_RETURN, 'children'),
        Input(ids.WATER_LEVELS, 'clickData'),
        Input(ids.WATER_LEVELS, 'selectedData'),
        prevent_initial_call=True
    )
    def display_data(click_data, selected_data):
        data = json.dumps(
            [
                click_data,
                selected_data
                ],
            indent=1
        )
        return data
    @app.callback(
        Output(ids.PLOT_WLS, 'value'),
        Input(ids.PLOT_WLS, 'n_clicks'),
        State(ids.WATER_LEVELS, 'selectedData'),
        prevent_initial_call=True
    )
    def show_wls(_, selected_data):
        selected_points = []
        for point in selected_data['points']:
            selected_points.append(point['text'])
        columns = wls_df.columns
        wl_fig = Fig()
        wl_fig_bokeh = BokehFig(x_axis_type="datetime")
        wldd_source = wl_fig_bokeh.column_data_source(wls_df)
        for point_name in selected_points:
            if point_name in columns:
                well_data = wls_df.loc[:, point_name].dropna()
                wl_fig.add_scattergl(x=well_data.index, y=well_data, name=point_name, connectgaps=False)
                wl_fig_bokeh.line(x='Date Time', legend_label=point_name, y=point_name, source=wldd_source)
        wl_fig.show()
        # wl_fig_bokeh.show()

    @app.callback(
        Output(ids.OFFCANVAS_MAIN2, 'is_open'),
        Input(ids.BUTTON_OPEN_MAIN_SIDEBAR2, 'n_clicks'),
        State(ids.OFFCANVAS_MAIN2, 'is_open'),
        prevent_initial_call=True
    )
    def offcanvas_main_sidebar_2_open(_, is_open):
        if is_open == False:
            return True
        if is_open == True:
            return False
 
    return dcc.Graph(figure=fig, 
                     config=config, 
                     id=ids.WATER_LEVELS,
                     className="flex-grow-1")
