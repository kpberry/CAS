# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 13:51:47 2015

@author: kberry
"""

from graphics import *
from function_class import *
from raw_function_class import *
from parametric_equation_class import *
from k_decorators import timed
from datetime import datetime
    
def graph(funct, width = 250, height = 250, center = None,\
parameter = 'x', scale = 20, raw = False):
    t = datetime.now()
    if type(funct) == type(''):
        if not raw:
            funct = Function(funct)
        else:
            funct = RawFunction(funct)
    if center == None:
        center = Point(width/2, height/2)
    low = -center.getX()
    up = width - center.getX()
    win = GraphWin('Graph', width, height)
    win.setBackground('white')
    Line(Point(0, center.getY()), Point(width, center.getY())).draw(win)
    Line(Point(center.getX(), 0), Point(center.getX(), height)).draw(win)
    prev = Point(low + center.getX(),\
        -funct.evaluate({parameter:low/scale}) * scale + center.getY())
    while low  < up:
        cur = Point(low + center.getX(),\
        -funct.evaluate({parameter:low/scale}) * scale + center.getY())
        lin = Line(prev, cur)
        prev = cur
        try:
            lin.draw(win)
        except:
            pass
        low += 1
    print('Grapher took', (datetime.now() - t), 'seconds.')
    print('')
    win.getMouse()
    win.close()
    win.destroy()

def graph_par(param_eqn, low = 0, up = 100,\
 parameter = 't', step = 1, scale = 1):
    width = 500
    height = 500
    win = GraphWin('Graph', width, height)
    win.setBackground('white')
    Line(Point(0, height/2), Point(width, height/2)).draw(win)
    Line(Point(width/2, 0), Point(width/2, height)).draw(win)
    temp = param_eqn[low]
    prev = Point(float(temp[0]) * scale + width/2,\
        -float(temp[1]) * scale + height/2)
    while low < up + step:
        temp = param_eqn[low]
        cur = Point(float(temp[0]) * scale + width/2,\
        -float(temp[1]) * scale + height/2)
        lin = Line(prev, cur)
        prev = cur
        try:
            lin.draw(win)
        except:
            pass
        low += step
    win.getMouse()
    win.close()

#graph('(2x+3sin(x))/cosh(x)*e^(x)/5', 500, 500, raw = True, scale = 20)
#graph('x * abs(x)', 500, 500,  scale = 250, raw = True)
#graph('e^(x**0.5)', 400, 400, scale = 10, raw = True, center = Point(20, 380))
#absolutely bizarre behavior here
#graph('(<sin(x), 2x, 10> cross <cos(x), 10, 3> dot <ln(x), e^x>)/e^x',\
# 400, 400, scale = 10, raw = True)
#a = graph_par(ParamEqn('x = sin(t)', 'y = cos(t)'), 0, 2*pi,\
# scale = 100, step = 0.1)
#a = graph('2(3x)^(1/2)-x', 500, 500, center = Point(50, 200))
#graph_par(ParamEqn('x = t^2+t', 'y = t^2-t'), -5, 5, step = 0.3, scale = 20)
#graph_par(ParamEqn('x = cos(t^3)', 'y = 3sin(t^3)'),\
# 0, 9, step = 0.01, scale = 60)
#graph_par(ParamEqn('x = e^tsin(t)', 'y = tcos(t)'),\
# -10, 5, step = 0.1, scale = 5)
#this eventually makes a square, but it takes about 5 minutes to do so.
#graph_par(Function('<cos(x)^500, tan(x)^(1/500)>'), 0, 2*pi,\
#scale = 100, step = 0.01)
#graph('sin(x/2)', 500, 500, scale = 20, raw = True)
#graph('acos((2t^3+t)/(sqrt(t^4+t^2)*sqrt(4t^2+1)))', 400, 400, parameter = 't')
#graph('x^2-x^7+1/8', 500, 500, scale = 100)
print('Graphics currently running.')