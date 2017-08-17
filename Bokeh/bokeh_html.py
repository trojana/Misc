from bokeh.plotting import figure
from bokeh.io import output_file, show
x = [1, 2, 3, 4, 5]
y = [3, 7, 8, 12, 1]
p = figure(title="Hello Bokeh!")
p.line(x,y)
output_file("hello_bokeh.html")
show(p)
