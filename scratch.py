from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler


class BokehFigureServer:
    def __init__(self, figure, port=5006):
        self.figure = figure
        self.port = port

    def modify_doc(self, doc):
        doc.add_root(self.figure)

    def run(self):
        # Create a Bokeh application that modifies the document via a function
        bokeh_app = Application(FunctionHandler(self.modify_doc))

        # Start a Bokeh server with the application
        server = Server({'/': bokeh_app}, port=self.port)
        server.start()

        print(f'Serving Bokeh app on http://localhost:{self.port}/')

        # Open the application in a browser window
        server.io_loop.add_callback(server.show, "/")
        server.io_loop.start()


# Example usage
if __name__ == '__main__':
    # Assuming `my_figure` is a Bokeh figure you have previously created
    my_figure = figure(title="Simple Bokeh Figure Example")
    my_figure.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)

    server = BokehFigureServer(my_figure)
    server.run()
