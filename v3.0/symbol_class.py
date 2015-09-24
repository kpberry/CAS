# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 14:10:55 2015

@author: kberry
"""

from function_class import *

#needs to automatically add itself to variable lists
#fairly rudimentary at this point; needs refinement
class Symbol:
    def __init__(self, name, value = 1, constant = False):
        self.name = str(name)
        self.value = value
        self.constant = constant
    
    def __add__(self, other):
        try:
            return Function(self.name, [self.value])\
            + Function(str(other), other.get_var_values())
        except AttributeError:
            return Function(self.name, [self.value]) + Function(str(other))
    
    def __sub__(self, other):
        try:
            return Function(self.name, [self.value])\
            - Function(str(other), other.get_var_values())
        except AttributeError:
            return Function(self.name, [self.value]) - Function(str(other))
    
    def __mul__(self, other):
        try:
            return Function(self.name, [self.value])\
            * Function(str(other), other.get_var_values())
        except AttributeError:
            return Function(self.name, [self.value]) * Function(str(other))
    
    def __truediv__(self, other):
        try:
            return Function(self.name, [self.value])\
            / Function(str(other), other.get_var_values())
        except AttributeError:
            return Function(self.name, [self.value]) / Function(str(other))
    
    def __pow__(self, other):
        try:
            return Function(self.name, [self.value])\
            ** Function(str(other), other.get_var_values())
        except AttributeError:
            return Function(self.name, [self.value]) ** Function(str(other))
    
    def __iadd__(self, other):
        return self + other
    
    def __isub__(self, other):
        return self - other
    
    def __imul__(self, other):
        return self * other
    
    def __itruediv__(self, other):
        return self / other
    
    def get_name(self):
        return self.name
    
    def get_value(self):
        return self.value
    
    def get_var_values(self):
        return [self.value]
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    