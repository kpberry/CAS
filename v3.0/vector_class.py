# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:43:08 2015

@author: kberry
"""

from function_class import *

class Vector:
    def __init__(self, *components):
        self.components = []
        
        for i in components:
            #appends each of the items within lists of submitted components
            if type(i) == type((0,0)) or type(i) == type([0,0]):
                for j in i:
                    self.components.append(j)
            else:
                self.components.append(i)
        self.mag = abs(self)
    
    def __add__(self, other):
        """Adds two vectors or adds a float to the first value in a vector"""
        c1 = self.components
        try:
            c2 = other.components
        #makes sure both items are vectors
        except AttributeError:
            c2 = Vector(other).get_components()
        #makes sure that the component lists are the same length
        while len(c1) > len(c2):
            c2.append(0)
        while len(c1) < len(c2):
            c1.append(0)
        result = [c1[i] + c2[i] for i in range(len(c1))]
        return Vector(*result)
    
    def __iadd__(self, other):
        return self + other
    
    def __sub__(self, other):
        """Subtracts a vector or float from this one"""
        c1 = self.components
        try:
            c2 = other.components
        except AttributeError:
            c2 = Vector(other).get_components()
        while len(c1) > len(c2):
            c2.append(0)
        while len(c1) < len(c2):
            c1.append(0)
        result = [c1[i] - c2[i] for i in range(len(c1))]
        return Vector(*result)
        
    def __isub__(self, other):
        return self - other
    
    def __mul__(self, other):
        """Multiplies a vector by floats or functions"""
        #multiplies a one dimensional vector by another vector
        if len(self.components) == 1 and type(other) == type(self):
            result = []
            for i in range(len(other.get_components())):
                result.append(other.get_components()[i] * self.components[0])
            return Vector(*result)
        try:
            #multiplies a vector by a floating point number
            result = []
            for i in range(len(self.components)):
                result.append(self.components[i] * float(other))
            return Vector(*result)
        except TypeError:
            #multiplies a vector by a function
            result = []
            for i in range(len(self.components)):
                result.append(Function(str(self.components[i])) * other)
            return Vector(*result)
    
    def __imul__(self, other):
        return self * other
    
    def __truediv__(self, other):
        """Divides a vector by a float or a function"""
        try:
            result = []
            for i in range(len(self.components)):
                result.append(self.components[i] / other)
            return Vector(*result)
        except TypeError:
            result = []
            for i in range(len(self.components)):
                result.append(Function(str(self.components[i])) / other)
            return Vector(*result)
    
    def __itruediv__(self, other):
        return self / other
    
    def cross(self, other):
        """performs a three dimensional vector cross product; automatically
        adjusts vectors of fewer dimensions, bringing them up to three"""
        c1, c2 = self.components, other.get_components()
        while len(c1) < 3:
            c1.append(0)
        while len(c2) < 3:
            c2.append(0)
        return Vector(c1[1]*c2[2]-c1[2]*c2[1],\
        c1[2]*c2[0]-c1[0]*c2[2], c1[0]*c2[1]-c1[1]*c2[0])
    
    def dot(self, other):
        """Performs an n dimensional cross product on two vectors"""
        try:
            #makes sure components are the same length
            c1, c2 = self.components, other.get_components()
            while len(c1) > len(c2):
                c2.append(0)
            while len(c1) < len(c2):
                c1.append(0)
            result = 0
            for i in range(len(c1)):
                result += c1[i] * c2[i]
            return result
        except TypeError:
            #makes a Function result in case float numbers didn't work
            c1, c2 = self.components, other.get_components()
            while len(c1) > len(c2):
                c2.append(0)
            while len(c1) < len(c2):
                c1.append(0)
            result = Function('')
            for i in range(len(c1)):
                result += c1[i] * c2[i]
            return result
    
    def __abs__(self):
        """returns the magnitude of a vector"""
        try:
            result = 0
            for i in self.components:
                result += i ** 2
            return result ** 0.5
        except TypeError:
            result = Function('0')
            for i in self.components:
                result += i ** 2
            return result ** 0.5
    
    def normalize(self):
        """returns a unit vector in the direction of this one"""
        mag = self.mag
        result = []
        for i in self.components:
            result.append(i/mag)
        return Vector(result)
        
    def __getitem__(self, index):
        return self.components[index]
        
    def evaluate(self, values):
        try:
            values = list(values)
            return Function(str(self)).evaluate(values)
        except TypeError:
            return Function(str(self)).evaluate([values])
            
    def add_component(self, other):
        self.components.append(other)
        
    def get_components(self):
        return self.components
    
    def __float__(self):
        if len(self.components) == 1:
            return float(self.components[0])
        
    def __str__(self):
        return '<' + str(self.components)[1:len(str(self.components))-1] + '>'
    
    def __repr__(self):
        return '<' + str(self.components)[1:len(str(self.components))-1] + '>'