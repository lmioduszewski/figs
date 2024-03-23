from bokeh.plotting import figure, show
import bokeh.plotting as bkp

class BokehFig:
    def __init__(self, *args, **kwargs):

        print('inited')
        self.f = figure(*args, **kwargs)
        #  self.f.sizing_mode = 'stretch_both'


    def show(self):
        return bkp.show(self.f)

    def line(self, *args, **kwargs):
        self.f.line(*args, **args)


if __name__ == "__main__":
    fig = BokehFig(title="My Custom Plot")
    fig.f.line(x=[1, 2, 3], y=[1, 6, 8])
    fig.show()
