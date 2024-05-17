from dash import Dash
from threading import Timer
import dash_bootstrap_components.themes as theme
from _dash_layout import create_layout
import _ids as ids
from dash.dependencies import Input, Output, State
import webview

app = Dash(external_stylesheets=[theme.DARKLY])
app.title = "Hydro Tools"
app.layout = create_layout(app)
main_window = webview.create_window('Water Level Viewer v0.1a', 'http://127.0.0.1:8050//', 
                            min_size=(1500,1500),
                            fullscreen=True)

@app.callback(
    Output(ids.TOGGLE_FULLSCREEN, 'value'),
    Input(ids.TOGGLE_FULLSCREEN, 'n_clicks'),
    prevent_initial_call=True)
def toggle_fullscreen(_):
    """callback for toggle fullscreen button"""
    main_window.toggle_fullscreen()
    
if __name__ == "__main__":
    
    def run_app():
        Timer(
            interval=1, 
            function=(app.run(debug=True, port=8050, use_reloader=False))
            ).start()
            
    webview.start(func=(run_app))

    Dash.run
