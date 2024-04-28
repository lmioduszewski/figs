from ._fig import Template

def create_hover(*args, **kwargs):
    """
    Function to return a hover template for a Plotly figure

    :args:
    name_dict [dict]: dict where the keys are the names of each hover data label,
    such as 'Proj #'. The values associated with each dict key are a list of data for that key,
    such as a list of project numbers, one for each data point in the figure trace

    :return: customdata, hovertemplate
    """
    return Template.create_hover(*args, **kwargs)