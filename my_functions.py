import pandas as pd
import plotly.graph_objects as go

# Get some qualitative and quantitative data about a dataframe.
def inspect(df):
    print(f"there are {df.shape[0]} rows and {df.shape[1]} columns")
    num_records_if_all_filled = df.size - len(df.Date)
    print(f"for up to {num_records_if_all_filled} measurements")
    print(f"the date column is currently {df.Date.dtype}")
    print("the column names are")
    for i, col in enumerate(df.columns):
        print(i, col)

# Prepare a quick visualization
def my_viz(fig, df, mode):
    '''
    A function for a quick plot.
    Input:
        fig: an initialized figure, e.g. fig1 = go.Figure()
        df: a dataframe with column 0 called 'Date' and other columns the series of interest.
        mode: 'lines', 'markers', or 'lines+markers'. Include ''.
    Output: 
        A scatter plot that will render in the notebook.

    '''

    for col in df.columns[1:]:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df[col],
            mode=mode,
            name=col
        ))

    fig.show()