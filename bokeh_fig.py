from bokeh.plotting import figure, show
import bokeh.plotting as bkp
from bokeh.models.tools import (
    PanTool, WheelZoomTool, BoxZoomTool, ResetTool,
    HoverTool, SaveTool, BoxSelectTool, LassoSelectTool,
    PointDrawTool, PolyDrawTool, PolyEditTool, TapTool
)
from bokeh.models import ColumnDataSource, Legend, ColorPicker, Select, CustomJS
import bokeh.models as bkmodels
from pathlib import Path
import pandas as pd
import bokeh.layouts as bklayout
from plotly.colors import DEFAULT_PLOTLY_COLORS
import itertools


class BokehFig:
    """Custom Bokeh plot with custom defaults properties and methods"""

    def __init__(self, webgl=True, *args, **kwargs):
        #  Setup figure and data sources for drawn points and polys
        self.f = figure(*args, **kwargs)
        self.drawn_points_data = ColumnDataSource(data=dict(x=[], y=[]))
        self.drawn_points = self.f.scatter(x='x', y='y', source=self.drawn_points_data, size=10, color='blue')
        self.drawn_polys_data = ColumnDataSource(data=dict(xs=[], ys=[]))
        self.drawn_polys_vertex_data = ColumnDataSource(data=dict(x=[], y=[]))
        self.drawn_polys_vertex = self.f.scatter(x='x', y='y', source=self.drawn_polys_vertex_data, size=20,
                                                 color='red', marker='x')
        self.drawn_polys = self.f.patches(xs='xs', ys='ys', source=self.drawn_polys_data, color='blue')
        self.glyph_list = []

        # Define tools
        self.pan_tool = PanTool()
        self.wheel_zoom_tool = WheelZoomTool()
        self.box_zoom_tool = BoxZoomTool()
        self.reset_tool = ResetTool()
        self.hover_tool = HoverTool()
        self.save_tool = SaveTool()
        self.box_select_tool = BoxSelectTool()
        self.lasso_select_tool = LassoSelectTool()
        self.point_draw_tool = PointDrawTool(renderers=[self.drawn_points])
        self.poly_draw_tool = PolyDrawTool(renderers=[self.drawn_polys])
        self.poly_edit_tool = PolyEditTool(renderers=[self.drawn_polys], vertex_renderer=self.drawn_polys_vertex)
        self.tap_tool = TapTool()

        # List of tools to pass to figure object
        tool_list = [
            self.pan_tool,
            self.wheel_zoom_tool,
            self.box_zoom_tool,
            self.reset_tool,
            self.hover_tool,
            self.save_tool,
            self.box_select_tool,
            self.lasso_select_tool,
            self.point_draw_tool,
            self.poly_draw_tool,
            self.poly_edit_tool,
            self.tap_tool
        ]
        self.taptext = bkmodels.Div()
        self.f.sizing_mode = 'stretch_both'
        self.f.output_backend = 'webgl' if webgl is True else 'canvas'
        self.f.tools = tool_list
        self.f.toolbar.active_scroll = self.wheel_zoom_tool
        self.f.toolbar.logo = None  # Remove Bokeh logo from toolbar

        self.color_cycle = itertools.cycle(DEFAULT_PLOTLY_COLORS)

        #  Setup default axes properties
        axis_props = {
            'axis_line_width': 2,
            'major_label_text_font_size': '16px'
        }
        self.f.xaxis.update(**axis_props)
        self.f.yaxis.update(**axis_props)

        #  Container to hold all datasources for plot
        self._column_data_sources = []
        self._source_id = 0

        #  Color Picker behavoir
        self.color_picker = ColorPicker()
        self.color_picker_callback = CustomJS(
            args={
                'sources': self.column_data_sources,
                'div': self.taptext,
                'glyph_list': self.glyph_list,
                'color_picker': self.color_picker
            }, code="""
                    let selected_glyphs = [];
                    sources.forEach((source, index) => {
                        let selected_indices = source.selected.line_indices;
                        if (selected_indices.length > 0) {
                            selected_glyphs = source.selected.selected_glyphs;
                            selected_glyphs.forEach((glyph, index) => {
                                glyph.line_color = color_picker.color;
                            });
                            source.change.emit();
                            source.selected.line_indices = [];
                            source.selected.selected_glyphs = [];
                        }
                    });
                    selected_glyphs = [];
                """)
        self.color_picker.js_on_change('color', self.color_picker_callback)

        # TapTool behavior
        #  callback to make only the last tapped glyph part of the selected_glyphs attribute
        tap_callback = CustomJS(args={'div': self.taptext}, code="""
            let last_selected = cb_data.source.selected.selected_glyphs[0];
            cb_data.source.selected.selected_glyphs = [last_selected];
            """)
        tap_tool = self.f.select(type=TapTool)
        tap_tool.callback = tap_callback

    @property
    def column_data_sources(self):
        return self._column_data_sources

    @property
    def source_id(self):
        return self._source_id

    def show(self):
        self.f.legend.click_policy = "hide"
        #  set legend location to left outside the plot
        legend = self.f.legend[0]
        self.f.add_layout(legend, place='left')
        return bkp.show(
            bklayout.column(
                self.f,
                bklayout.row(
                    self.color_picker,
                    self.taptext
                ),
                sizing_mode='stretch_both'
            )
        )

    def line(self, legend_label='None', *args, **kwargs):
        this_line = self.f.line(
            legend_label=legend_label,
            name=legend_label,
            selection_color="firebrick",
            color=next(self.color_cycle),
            *args, **kwargs
        )
        self.glyph_list.append(this_line)
        return this_line

    def column_data_source(self, *args, **kwargs):
        source = ColumnDataSource(*args, **kwargs)
        self.column_data_sources.append(source)
        self.color_picker_callback.args['sources'] = self.column_data_sources  # Update the list in JS
        return source


if __name__ == "__main__":
    from bokeh_fig import BokehFig
    from bokeh.plotting import figure, show
    from bokeh.models import ColumnDataSource
    import random
    import plotly.graph_objs as go
    from figs._fig import Fig



    path = Path().home() / 'Python/data/tehaleh_wls.xlsx'
    df_dd = pd.read_excel(path, sheet_name='WellDD').set_index('Date Time').apply(
        lambda column: pd.to_numeric(column, errors='coerce'))
    df_dd = df_dd.drop(['Month', 'Year', 'Water Year'], axis='columns').dropna(how='all')
    fig = BokehFig(x_axis_type="datetime")
    pfig = Fig()
    source = fig.column_data_source(df_dd)

    for col in df_dd.columns:
        fig.line(x='Date Time', legend_label=col, y=col, source=source)
        pfig.add_scattergl(x=df_dd.index, y=df_dd[col])
    fig.show()
    # pfig.show()

