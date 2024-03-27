import os
from figs._fig import Fig
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
import plotly.io as pio
import xml.etree.ElementTree as ETree
import svgpathtools as svgtools
from bokeh.plotting import figure, show
from bokeh.models import Range1d
from bokeh.io.export import get_svg, export_svg


class ScalableFigure(Fig):
    """Subclass of 'Fig' from 'figs' custom go.Figure class. Main purpose is to allow the setting
    of a scale for a go.Scatter plot using plotly. Can then print to pdf a plot that has precise
    horizontal and vertical scales.

    Simple Example:

        fig = ScalableFigure()
        fig.add_scatter(x=..., y=...)
        fig.x_scale = 200
        fig.write_scaled_pdf()

        By default, the x-axis is the anchor axis, while the scale of the y-axis is determined by the exaggeration,
        which defaults to 10 times. So in the example, the y-scale would be 1 inch = 20 feet, and the x-scale would
        be 1 inch = 200 feet. Also, by default the page size (plot_height and plot_width properties) is 11 x 17 inches,
        and the scaling changes the range of the axes so that the axes' scales match the defined properties for
        x_scale and y_scale. Can also scale the page, instead of changing axes' ranges by setting adjust_by = "page" in
        the write_scaled_pdf method.

        """

    def __init__(
            self,
            svg_path='temp_plot.svg',
            pdf_path='temp_plot.pdf'
    ):
        super().__init__()
        self._x_range = None
        self._y_range = None
        self._svg_path = svg_path
        self._pdf_path = pdf_path
        # default plot size is 11 x 17 inches
        self._plot_width = 72 * 17  # 72 points per inch
        self._plot_height = 72 * 11
        self._x_scale = None
        self._y_scale = None
        self._y_scale_exaggeration = 10
        self._xaxis_anchor = True
        self._tree = None
        self._grid_dimensions = None

    @property
    def x_range(self):
        """convenience property to set the x-axis range. Value is passed to the 'range' argument of the
        update_xaxes method of the figure (self)."""
        return self._x_range

    @x_range.setter
    def x_range(self, val):
        self.update_xaxes(range=val)
        self._x_range = val

    @property
    def y_range(self):
        """convenience property to set the y-axis range. Value is passed to the 'range' argument of the
        update_yaxes method of the figure (self). """
        return self._y_range

    @y_range.setter
    def y_range(self, val):
        self.update_yaxes(range=val)
        self._y_range = val

    @property
    def x_scale(self):
        """defines the number of plot units in the x-direction per inch on the paper"""
        return self._x_scale

    @x_scale.setter
    def x_scale(self, val):
        if type(val) is int:
            self._x_scale = val
        else:
            print('cannot set the x scale. Must be an integer')

    @property
    def y_scale(self):
        """defines the number of plot units in the y-direction per inch on the paper"""
        return self._y_scale

    @y_scale.setter
    def y_scale(self, val):
        if type(val) is int:
            self._y_scale = val
        else:
            print('cannot set the y scale. Must be an integer')

    @property
    def element_tree(self):
        """the entire XML representation of the SVG as an element tree"""
        try:
            self.write_svg()
            self._tree = ETree.parse(self._svg_path)
        except IOError:
            print('no readable svg file found!')
            self._tree = None
        return self._tree

    @property
    def grid_dimensions(self):
        """get the dimensions of the grid/canvas area of a scatter plot by parsing a plotly generated SVG"""
        grid_dimensions = {}
        try:
            tree = self.element_tree
            root = tree.getroot()
        except AttributeError:
            print('cannot calculate grid dimensions because cannot generate the XML element tree')
            return
        #  find the plot grid dimensions in the SVG file
        for element in root.iter():
            if 'class' in element.attrib.keys():
                #  we are looking for elements classified as a 'gridlayer'
                if element.attrib['class'] == 'gridlayer':
                    for subelement in element.iter():
                        #  the 'd' attribute defines an SVG 'path'
                        if 'd' in subelement.attrib:
                            #  get the path length of this 'gridlayer' element
                            grid_length = svgtools.parse_path(subelement.attrib['d']).length()
                            #  it's confusing but use xgrid to get the height, ygrid for width
                            if 'xgrid' in subelement.attrib['class']:
                                grid_dimensions['height'] = grid_length
                            if 'ygrid' in subelement.attrib['class']:
                                grid_dimensions['width'] = grid_length
        self._grid_dimensions = grid_dimensions
        return self._grid_dimensions

    @property
    def plot_width(self):
        """sets the page width of the plot in inches"""
        return self._plot_width

    @plot_width.setter
    def plot_width(self, val):
        if type(val) is int:
            #  assumes the conversion 72 dots per inch in the output SVG/PDF
            self._plot_width = val * 72
        else:
            print(f'provided value: {val} is not an integer. Property cannot be set')

    @property
    def plot_height(self):
        """sets the page height of the plot in inches"""
        return self._plot_height

    @plot_height.setter
    def plot_height(self, val):
        if type(val) is int:
            #  assumes the conversion 72 dots per inch in the output SVG/PDF
            self._plot_height = val * 72
        else:
            print(f'provided value: {val} is not an integer. Property cannot be set')

    def _get_plot_to_grid_scale_ratios(self):
        """get the ratios of the plot width and height to the grid width and height"""
        grid_dimensions = self.grid_dimensions
        x_scale_ratio = self.plot_width / grid_dimensions['width']
        y_scale_ratio = self.plot_height / grid_dimensions['height']
        return x_scale_ratio, y_scale_ratio

    def write_svg(self, filename: str = None):
        """writes an SVG representation of the figure to a *.svg file"""
        if filename is None:
            filename = self._svg_path
        pio.write_image(
            self,
            format='svg',
            file=filename,
            width=self.plot_width,
            height=self.plot_height)

    def write_scaled_pdf(
            self,
            delete_svg=True,
            adjust_by='range',
    ):
        if adjust_by == 'page':
            drawing = self._scale_page()
            self._write_pdf(drawing)
        elif adjust_by == 'range':
            drawing = self._scale_range()
            self._write_pdf(drawing)
        else:
            print("adjust_by must equal 'page' or 'range'")
        if delete_svg and os.path.exists(self._svg_path):
            os.remove(self._svg_path)

    def _scale_page(self):
        """scale the figure so that the plot grid/canvas is the size defined by plot_height and plot_width."""
        scale_x, scale_y = self._get_plot_to_grid_scale_ratios()
        drawing = svg2rlg(self._svg_path)
        # Scale the drawing
        drawing.width, drawing.height = drawing.width * scale_x, drawing.height * scale_y
        drawing.scale(scale_x, scale_y)
        return drawing

    def _scale_range(self):
        """Scale the range of the figure, keeping the page size the same, so that
        the x and y ranges are at the provided scale"""
        x_feet_per_dot = [self._x_scale / 72 if self._x_scale is not None else 0]
        y_feet_per_dot = [self._y_scale / 72 if self._y_scale is not None else 0]
        grid_dimensions = self.grid_dimensions
        #  get default minimum x-axis value based on data
        x_min = self.full_figure_for_development(warn=False).layout.xaxis.range[0]
        x_dots, y_dots = grid_dimensions['width'], grid_dimensions['height']
        x_span, y_span = x_dots * x_feet_per_dot[0], y_dots * y_feet_per_dot[0]
        if self._xaxis_anchor is True:
            self.update_yaxes(scaleanchor='x', scaleratio=self._y_scale_exaggeration)
        self.update_xaxes(range=[x_min, (x_min + x_span)])
        #   write a new svg file with the updated, scaled axes ranges
        self.write_svg()
        drawing = svg2rlg(self._svg_path)
        return drawing

    def _write_pdf(self, drawing: svg2rlg, pdf_path=None):
        """write a pdf from a svg2rlg drawing"""
        if pdf_path is None:
            pdf_path = self._pdf_path
        rendered_drawing = Drawing(drawing.width, drawing.height)
        rendered_drawing.add(drawing)
        # Render the drawing to PDF
        renderPDF.drawToFile(rendered_drawing, pdf_path)
        print(f'wrote drawing {pdf_path}')

class BokehScalableFigure:
    def __init__(
            self,
            bokeh_figure: figure = None,
            plot_width=17,
            plot_height=11,
            x_scale=1,
            y_scale=1,
            x_start=0,
            y_start=0
    ):
        # Basic plot setup
        self.dot_per_inch = 72  # used to convert plot dimensions to inches, 72 is the standard default
        self.plot_width = plot_width * self.dot_per_inch
        self.plot_height = plot_height * self.dot_per_inch
        self.x_scale = x_scale  # real-world units per inch
        self.y_scale = y_scale  # real-world units per inch
        self.x_start = x_start  # minimum x value in real-world units
        self.y_start = y_start  # minimum y value in real-world units
        if bokeh_figure is None:
            self.figure = figure(
                width=self.plot_width, height=self.plot_height,
                output_backend="svg")
        else:
            self.figure = bokeh_figure
            self.figure.width = self.plot_width
            self.figure.height = self.plot_height
            self.figure.output_backend = 'svg'

        # Default file paths
        self.svg_path = 'temp_plot.svg'
        self.pdf_path = 'temp_plot.pdf'

    def add_line(self, x, y, **kwargs):
        self.figure.line(x, y, **kwargs)

    def write_svg(self):
        # Save the current figure as svg
        export_svg(self.figure, filename=self.svg_path)

    @property
    def x_scale(self):
        return self._x_scale

    @x_scale.setter
    def x_scale(self, val):
        self._x_scale = val

    @property
    def x_start(self):
        return self._x_start

    @x_start.setter
    def x_start(self, val):
        self._x_start = val

    @property
    def y_scale(self):
        return self._y_scale

    @y_scale.setter
    def y_scale(self, val):
        self._y_scale = val

    @property
    def y_start(self):
        return self._y_start

    @y_start.setter
    def y_start(self, val):
        self._y_start = val

    @property
    def root(self):
        root = ETree.parse(self.svg_path).getroot()
        self._root = root
        return self._root

    def get_scaled_grid_dimensions(self):
        """Parses the figure SVG to get the scaled x and y ranges based on the starting.
        Determines the actual axes spans in inches and scales the ranges so that the
        specified x_scale and y_scale are true."""
        root = self.root
        elements = [element for element in root.iter()]
        #  get the bounding box of the grid of the svg plot exported from Bokeh. the element with the
        #  index of 5 encompases the grid area of the plot, so we get the bbox from this element
        bbox = svgtools.parse_path(elements[5].attrib['d']).bbox()
        x_dot_min, y_dot_min = bbox[0], bbox[2]
        x_dot_span, y_dot_span = bbox[1] - bbox[0], bbox[3] - bbox[2]
        x_length_grid_in_inches = x_dot_span / self.dot_per_inch
        y_height_grid_in_inches = y_dot_span / self.dot_per_inch

        x_unit_span = x_length_grid_in_inches * self.x_scale
        y_unit_span = y_height_grid_in_inches * self.y_scale
        x_unit_min, y_unit_min = self.x_start, self.y_start

        x_unit_max = x_unit_min + x_unit_span
        y_unit_max = y_unit_min + y_unit_span
        x_range, y_range = (x_unit_min, x_unit_max), (y_unit_min, y_unit_max)

        return x_range, y_range

    def write_scaled_pdf(self):
        svg_path = self.svg_path
        pdf_path = self.pdf_path

        #  write and parse inital svg, adust the figure ranges, and then write the scaled svg
        self.write_svg()
        print('wrote 1st svg')
        x_range, y_range = self.get_scaled_grid_dimensions()
        self.figure.x_range = Range1d(*x_range)
        self.figure.y_range = Range1d(*y_range)
        self.write_svg()
        print('wrote scaled svg')

        # Convert SVG to PDF while maintaining scale
        drawing = svg2rlg(svg_path)

        # Create a ReportLab drawing and render the SVG drawing into it
        rendered_drawing = Drawing(drawing.width, drawing.height)
        rendered_drawing.add(drawing)

        # Write to a PDF
        renderPDF.drawToFile(rendered_drawing, pdf_path)
        print(f'PDF exported to {pdf_path}')


if __name__ == "__main__":
    bokeh_fig = BokehScalableFigure()
    bokeh_fig.add_line(x=[1, 2, 3, 4], y=[4, 3, 5, 2], line_width=2, color="blue", legend_label='ground line')
    bokeh_fig.write_scaled_pdf()  # Convert and scale to PDF

"""if __name__ == "__main__":

    fig = ScalableFigure()
    fig.add_scatter(x=[-110, 20, 44], y=[3, 2, 1])
    fig.add_scatter(x=[-20, 30, 49], y=[6, 8, 10])
    fig.x_scale = 50
    fig.write_scaled_pdf()"""
