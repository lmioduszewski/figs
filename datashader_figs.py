import holoviews as hv
from holoviews.operation.datashader import datashade
import pandas as pd
import numpy as np
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler

hv.extension('bokeh')


class DatashaderServer:
    def __init__(self, lines_df, points_df):
        self.lines = [(row.x1, row.y1, row.x2, row.y2) for index, row in lines_df.iterrows()]
        self.points_df = points_df

    def modify_doc(self, doc):
        # Prepare the lines for hv.Path
        paths_data = [np.array([(x1, y1), (x2, y2)]) for x1, y1, x2, y2 in self.lines]

        # Create HoloViews Path element
        paths = hv.Path(paths_data)

        # Convert DataFrame to HoloViews Points for points
        points = hv.Points(self.points_df, kdims=['x', 'y'])

        # Use datashade for lines and points
        shaded_lines = datashade(paths, cmap=['blue'])
        shaded_points = datashade(points, cmap=['red'])

        # Combine plots
        plot = shaded_lines * shaded_points

        # Add the HoloViews plot to the document
        doc.add_root(hv.render(plot))

    def run(self, port=5006):
        apps = {'/': Application(FunctionHandler(self.modify_doc))}
        server = Server(apps, port=port)
        server.start()
        server.io_loop.start()


# Example data for lines and points
lines_data = {'x1': [1, 3, 5], 'y1': [2, 4, 6], 'x2': [2, 4, 6], 'y2': [3, 5, 7]}
lines_df = pd.DataFrame(lines_data)
points_data = {'x': np.random.rand(1000), 'y': np.random.rand(1000)}
points_df = pd.DataFrame(points_data)

# Create and run the server
if __name__ == '__main__':
    plotter = DatashaderServer(lines_df, points_df)
    plotter.run()
