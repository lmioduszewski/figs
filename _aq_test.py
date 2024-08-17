import figs as f
from pathlib import Path
import pandas as pd
from figs.figure_transforms import ScalableFigure
import numpy as np

def exp(e):
    return float(f'1e{e}')

def generate_log_like_sequence(start_e, stop_e):
    values = [exp(start_e)]
    current_e = start_e
    while current_e < stop_e:
        current_list = np.linspace(exp(current_e), exp(current_e+1), 10).tolist()
        values += current_list[1:]
        current_e += 1
    return values

class AquiferTestFigure(ScalableFigure):

    def __init__(self,
                 plot_type: str = 'loglog',
                 scale_ratio: float | int = 0,
                 scale_anchor: str = 'x',
                 x_log_range = (-1, 4),
                 y_log_range = (-1, 2),
                 *args,
                 **kwargs
                 ):
        super().__init__(*args, **kwargs)

        self._plot_type = None
        self.plot_type = plot_type
        self._scale_ratio = None
        self.scale_ratio = scale_ratio
        self._scale_anchor = None
        self.scale_anchor = scale_anchor

        # sets the scale for both the x and y axes to 1 log per 1 inch
        # so you can save to a scaled pdf, print, and use aquifer test overlays
        self._xaxis_anchor = False
        self.x_scale = 1
        self.y_scale = 1

        self.layout.xaxis.tickvals = generate_log_like_sequence(x_log_range[0], x_log_range[1])
        self.layout.yaxis.tickvals = generate_log_like_sequence(y_log_range[0], y_log_range[1])
        self.layout.xaxis.range = (x_log_range[0], x_log_range[1])
        self.layout.yaxis.range = (y_log_range[0], y_log_range[1])
        self.layout.xaxis.tickfont = {'size': 9}
        self.layout.yaxis.tickfont = {'size': 9}
        self.layout.xaxis.zeroline = True
        self.layout.yaxis.zeroline = True


    @property
    def plot_type(self):
        return self._plot_type

    @plot_type.setter
    def plot_type(self, plot_type):

        if plot_type == 'loglog':
            xaxis_type = 'log'
            yaxis_type = 'log'
        elif plot_type == 'semilog':
            xaxis_type = 'log'
            yaxis_type = 'linear'
        else:
            raise ValueError('plot_type must be either loglog or semilog')
        self.update_layout(
            xaxis = {'type': xaxis_type},
            yaxis = {'type': yaxis_type},
        )
        self._plot_type = plot_type

    @property
    def scale_ratio(self):
        """scale ratio is the amount one axis scaled compared to the scale anchor axis. For example, if the scale anchor axis is 'x', then the scale ratio would define how much the y-axis scaled relative to the x-axis"""
        return self._scale_ratio

    @scale_ratio.setter
    def scale_ratio(self, scale_ratio):
        assert isinstance(scale_ratio, float | int), 'scale_ratio must be a float or int'
        self.update_layout(
            xaxis={'scaleratio': scale_ratio},
            yaxis={'scaleratio': scale_ratio},
        )
        self._scale_ratio = scale_ratio

    @property
    def scale_anchor(self):
        """sets which axis is the anchor axis for scaling. If the x-axis is the anchor, then the y-axis will be scaled (by the scale ratio) relative to the x-axis"""
        return self._scale_anchor

    @scale_anchor.setter
    def scale_anchor(self, scale_anchor):
        allowed_anchors = ['x', 'y', None]
        assert scale_anchor in allowed_anchors, f'scale_anchor must be one of {allowed_anchors}, not {scale_anchor}'
        if scale_anchor == 'x':
            self.update_layout(
                yaxis={'scaleanchor': scale_anchor})
        elif scale_anchor == 'y':
            self.update_layout(
                xaxis={'scaleanchor': scale_anchor}
            )
        self._scale_anchor = scale_anchor

if __name__ == '__main__':

    fig = AquiferTestFigure()
    fig.write_scaled_pdf()
