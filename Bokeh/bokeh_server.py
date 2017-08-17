from bokeh.plotting import curdoc
from bokeh.models.widgets import Button

def button_clicked():
    print('Button Clicked')

my_button = Button(label="Click Here!")
my_button.on_click(button_clicked)
curdoc().add_root(my_button)