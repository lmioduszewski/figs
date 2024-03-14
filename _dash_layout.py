from dash import Dash, html, dcc
from figs import _ids as ids
import dash_bootstrap_components as dbc
import _dash_wl_viewer as wl
from dash.dependencies import Input, Output, State
#import dash_daq

def create_layout(app: Dash) -> dbc.Container:


#MAIN FIGURE
    water_viewer_fig = dbc.Col([wl.render(app),], 
                               #width=10,
                               class_name='h-100 d-flex flex-column',
                               style={"height":"100vh"})

#TRACE PROPERTIES
    trace_properties = html.Div([
        dbc.Row([
            dbc.Col(
                html.Button('color', id=ids.COLOR_PICKER_BUTTON,
                            style={'color':'red',
                                'background-color':'red',
                                'border-radius':'12px'})),
            dbc.Col([
                dbc.Input(
                    type='color',
                    id=ids.COLOR_PICKER_TRACE,
                    style={'padding':'0px'}
                ),
                dcc.Store(id=ids.STORE_COLOR_PICKER_VALUE)])
            ],
                style={'padding':'5px'}),
        dbc.Row(
            dbc.Col(
                dbc.DropdownMenu(
                    label='dash type',
                    menu_variant='dark',
                    children=[
                         dbc.DropdownMenuItem(
                             "solid", id=ids.DROPDOWN_LINE_SOLID, n_clicks=0),
                         dbc.DropdownMenuItem(
                             "dash", id=ids.DROPDOWN_LINE_DASH, n_clicks=0)                         
                    ]
                )
            )
        )
        ]
                                )
    
#SIDEBAR2
    sidebar2 = (
        dbc.Container(
            [
                dbc.Card(
                    [
                        dbc.CardHeader(
                            dbc.Row(
                                "Data",
                                justify='center'
                                )
                            ),
                        dbc.CardBody(
                            id=ids.DATA_RETURN,
                            children='None'
                        )
                        ]
                    ),
                ],
            )
        )

#WATER LEVEL VIEWER    
    water_level_viewer_tab_content = html.Div(
        [dbc.Row(
            [
                dbc.Col(water_viewer_fig,
                        width=11,
                        style={
                            'width': '97vw'
                        }
                        ),
                dbc.Col(
                    [
                        dcc.Upload(
                            dbc.Button("O",
                                   style={'display':'inline',
                                          'width': '2vw',
                                          'padding': '1px',
                                          'margin': '1px',
                                          },
                                   size='sm',
                                   color='Red'
                            ),
                             id=ids.OPEN_FIG, 
                        ),
                        dcc.Store(ids.STORE_OPENED_FIG),
                        dbc.Button("F", 
                                   id=ids.TOGGLE_FULLSCREEN,
                                   size='sm',
                                   color='Warning',
                                   style={
                                       'display':'inline',
                                       'width': '2vw',
                                       'padding': '1px',
                                       'margin': '1px',
                                       }),
                        dbc.Button(id=ids.BUTTON_OPEN_MAIN_SIDEBAR2,
                                   size='sm',
                                   children='2',
                                   style={
                                       'width': '2vw',
                                       'padding': '1px',
                                       'margin': '1px',
                                       }),
                        dbc.Offcanvas(id=ids.OFFCANVAS_MAIN2,
                                      children=sidebar2,
                                      is_open=False,
                                      placement='end',
                                      backdrop=False,
                                      style={
                                          'width':'30vw'
                                          }
                                      ),
                        ],
                    #width=1
                    style={
                        'width': '1vw',
                        'padding': '1px'
                    }
                    )   
            ], 
            style={"height":"95vh"},
            )
         ], 
        #className="h-100 d-flex flex-column",
        style={"height":"90vh"},
    ) 

#MAIN LAYOUT    
    main_layout = dbc.Container(children=[
        dbc.Row(
            dbc.Col(
                dbc.Tabs(id=ids.TAB_MAIN,  
                         children=[
                            
                            dbc.Tab(children=water_level_viewer_tab_content, 
                                    label=ids.TAB_WATER_LEVEL_VIEWER,
                                    id=ids.TAB_WATER_LEVEL_VIEWER,
                                    ), 
                            ],
                         ),
                #tyle={"height": "100vh"}
                ),
            #style={"height": "100vh"}
            )
        ],
                                fluid=True)
        
    return main_layout