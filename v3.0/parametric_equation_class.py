# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:51:49 2015

@author: kberry
"""

from function_class import *
from equation_class import *
from vector_class import Vector

class ParamEqn(Equation):
    """Creates a system of parametric equations of the form x = foo, 
    y = bar, z = foo * bar, etc., which can be evaluated at a point."""
    def __init__(self, *eqns):
        self.variables = []
        self.equations = []
        for i in eqns:
            if type(i) == type(['']):
                for j in i:
                    self.equations.append(Equation(j))
                    self.variables.extend(\
                    self.equations[len(self.equations)-1][1].get_variables())
            elif type(i) == type(''):
                self.equations.append(Equation(i))
                self.variables.extend(\
                self.equations[len(self.equations)-1][1].get_variables())
            else:
                self.equations.append(i)
                self.variables.extend(\
                self.equations[len(self.equations)-1][1].get_variables())
        self.variables = list(set(self.variables))
    
    def evaluate(self, var_values = [0], printing = False):
        try:
            values = []
            if type(var_values) == type([0]) or type(var_values) == type((0, 0)):
                variables = dict(zip(self.variables, var_values))
            elif type(var_values) == type({'0':0}):
                variables = var_values
            else:
                variables = {self.variables[0]: var_values}
            if printing:
                for i in self.equations:
                    values.append(str(i[0])+': '+str(i[1].evaluate(variables)))
            else:
                for i in self.equations:
                    values.append(i[1].evaluate(variables))
            return values
        except IndexError:
            return 'Not an evaluable system of parametric equations.'
    
    def __getitem__(self, var_values):
        if type(var_values) == type((0, 0)):
            var_values = list(var_values)
        elif type(var_values) == type(0):
            var_values = [var_values]
        return self.evaluate(var_values, printing = False)
    
    def get_equations(self):
        return self.equations
    
    def get_variables(self):
        return self.variables
        
    def __str__(self):
        return str(self.equations)
    
    def __repr__(self):
        return str(self.equations)

#copy of proper ParamEqn class that's easier to type and use
class pe(ParamEqn):
    pass
    