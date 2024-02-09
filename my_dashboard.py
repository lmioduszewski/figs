# Get libraries for data import and visualization
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime
import os
import glob

# ****************
# * Get the data *
# ****************

# Get current script directory.
script_directory = os.path.dirname(os.path.realpath(__file__))

# Define relative paths for input and output subdirectories.
input_path = "../my_data_intermediate"
output_path = "../my_data_outputs"

# Join script directory and relative paths for absolute paths.
abs_input_path = os.path.join(script_directory, input_path)
abs_output_path = os.path.join(script_directory, output_path)

# Get the pickle files and sort alphabetically.
files = glob.glob(os.path.join(abs_input_path, "*.pkl"))
files.sort()

# Read each .pkl into a dataframe.
dfs = [pd.read_pickle(f) for f in files]

# Unpack the list of dfs.
df_hand, df_lake, df_loc, df_rain, df_streams, df_streams_hand, df_AESI = dfs

# ********************
# * Create Dashboard *
# ********************

# Initialize a faceted dashboard
fig = make_subplots(
    rows=3, cols=2,
    specs=[[{},{'rowspan': 3, 'type': 'scattermapbox'}],
           [{}, None],
           [{}, None]],
    subplot_titles=('Daily Water Level Logger Data',
                    'Monitoring Locations',
                    'Daily Rainfall',
                    'Stream Flow Data'
                    ),
    column_widths=[0.67, 0.33],
    row_heights=[0.7, 0.1, 0.2],
    horizontal_spacing=0.03,
    vertical_spacing=0.07,
    shared_xaxes=True
)

# UPPER LEFT: Add a trace for each well in the AESI set.
for col in df_AESI.columns[1:]:
    fig.add_trace(
       go.Scattergl(
        x=df_AESI.Date,
        y=df_AESI[col],
        mode='lines',
        name=col),
    row=1,
    col=1)

# UPPER LEFT: Label the y-axis of elevations plot.
fig.update_yaxes(
   title_text="Water Levels Elevation (ft)",
   showticklabels=True,
   automargin=True,
   row=1,
   col=1)

# UPPER LEFT: Add a trace for monitored lake.
for col in df_lake.columns[1:]:
   fig.add_trace(
      go.Scattergl(
         x=df_lake.Date,
         y=df_lake[col],
         mode='lines',
         line=dict(
            dash='dot'),
        name=col),
    row=1,
    col=1)


# UPPER LEFT: Add a trace for well in the hand data set.
for col in df_hand.columns[1:]:
   fig.add_trace(
      go.Scattergl(
         x=df_hand.Date,
         y=df_hand[col],
         mode='markers',
        name=col),
    row=1,
    col=1)

# MIDDLE LEFT: Add rainfall data as a barplot.
for gauge in df_rain['Rain Gauge'].unique():
   subset = df_rain[df_rain['Rain Gauge'] == gauge]
   fig.add_trace(
      go.Bar(
         x=subset.Date,
         y=subset['Rain (in)'],
         name='Rain Gauge ' + gauge,
      ),
      row=2,
      col=1
      )

# MIDDLE LEFT: Label the y-axis of rainfall plot.
fig.update_yaxes(
   title_text="Rainfall (in)",
   showticklabels=True,
   automargin=True,
   row=2,
   col=1
   )

# MIDDLE LEFT: configure the rainfall bars to display side-by-side.
fig.update_layout(barmode='group')

# LOWER LEFT: Add streamflow data.
for col in df_streams.columns[1:]:
   fig.add_trace(
      go.Scattergl(
         x=df_streams.Date,
         y=df_streams[col],
         mode='lines',
        name=col),
    row=3,
    col=1)

# LOWER LEFT: Add streamflow hand data. This data is long form.
for stream in df_streams_hand['Stream'].unique():
   subset = df_streams_hand[df_streams_hand['Stream'] == stream]
   fig.add_trace(
      go.Scattergl(
        x=subset.Date,
        y=subset['Stream Flow (cfs)'],
        mode='markers',
        name=stream
        ),
      row=3,
      col=1
      ) 

# LOWER LEFT: label y-axis of streamflow plot.
fig.update_yaxes(
   title_text="Stream Flow (cfs)",
   showticklabels=True,
   automargin=True,
   row=3,
   col=1)

# RIGHT SIDE: Add a map with the monitoring locations.
fig.add_trace(
   go.Scattermapbox(
      lat=df_loc.lat,
      lon=df_loc.lon,
      mode='markers+text',
      marker=dict(size=15),
      text=df_loc.Name,
      textposition='middle left',
      hovertemplate=df_loc.Name+
       '<br>Lat: %{lat:.4f}<br>'+
       'Lon: %{lon:.4f}<extra></extra>',
      showlegend=False,
   ),
   row=1,
   col=2
)

# **********************************
# * Configure the dashboard layout *
# **********************************

# Move legend to left side of dashboard.
fig.update_layout(
   legend=dict(
      x=-0.26,
      y=0.5
   )
)

# Change the default colors to improve readability.
fig.update_layout(plot_bgcolor='whitesmoke')

# Make the legend background have no color to stop obscuring tick labels.
fig.update_layout(legend_bgcolor='rgba(0,0,0,0)')

# Configure mapbox.
fig.update_layout(
   mapbox=dict(
      style='open-street-map',
      zoom=13,
      center=dict(
         # Center of Ten Trails site
         lat=47.30888,
         lon=-122.033152),
   ),
)

# Set the title and add subtitle with today's date.
current_date = datetime.datetime.today().strftime('%Y-%m-%d')
title = "<b>Ten Trails Hydrogeologic Monitoring Data<b>"
subtitle = "<br><sub>Dashboard Prepare On: " + current_date
fig.update_layout(title_text=title+subtitle)

# Change size of dashboard.
fig.update_layout(
   height=850,
   width=1900
)

# Show the axes labels.
fig.update_layout(
   xaxis=dict(showticklabels=True),
   xaxis2=dict(showticklabels=True)
   )

# Set pan mode as default plot interaction.
fig.update_layout(dragmode='pan')

# Set scroll-to-zoom for zooming on html.
config = {'scrollZoom': True}

# Show the figure upon run.
fig.show(config=config)

# Download the dashboard to a shareable .html file.
fig.write_html(os.path.join(
   abs_output_path,
   "TenTrailsDashboard.html"
   ),  
   config=config)