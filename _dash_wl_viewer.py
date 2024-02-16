import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly import graph_objs
import plotly
import plotly.express as px
from . import _ids as ids
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
from ._fig import get_fig
import json
from pathlib import Path
from ._fig import Template

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

def render(app: Dash) -> dcc.Graph:
    
    fig = go.Figure()
    
    @app.callback(
        Output(ids.WATER_LEVELS, 'figure'),
        Input(ids.OPEN_FIG, 'contents'),
        Input(ids.WATER_LEVELS, 'clickData'),
        State(ids.WATER_LEVELS, 'figure'),
        prevent_initial_call=True)
    def update_wl_fig(upload_contents, clickData, fig_state):
        if callback_context.triggered_id == ids.OPEN_FIG:
            # Split the content into metadata and data itself
            content_type, content_string = upload_contents.split(',')
            # Decode the base64 string
            decoded = base64.b64decode(content_string)
            try:
                fig_to_open = pickle.loads(decoded)
            except Exception as e:
                return f'An error occurred: {e}'
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
