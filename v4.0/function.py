# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 18:56:05 2015

@author: Kevin
"""

from function_helper import get_terms, has_sub_function, get_sub_function, \
replace_variables, make_friendly, get_variables, is_number
from fraction import Fraction
from math import *
import re
from k_decorators import timed
from vector import Vector

class Function:
    #needs a more sophisticated replace_values
    #needs its own evaluator
    #needs support for complex numbers; issues with has_sub_function
    #needs better fractional support
    #calculus?
    def __init__(self, phrase = ''):
        self.phrase = make_friendly(phrase)
        self.phrase_length = len(phrase)
        self.signed_terms = get_terms(self.phrase)
        self.terms = [i[1:] for i in self.signed_terms]
        self.variables = {}
        self.ordered_variables = []
        for i in get_variables(self.phrase):
            phrase = 'self.'+i+'=0'
            exec(phrase)
            self.variables.update({i:'self.'+i})
            if not ('self.'+i) in self.ordered_variables:
                self.ordered_variables.append('self.'+i)
        self.self_phrase = replace_variables(self.phrase, self.variables)
        #self.variables = [Symbol(i, 0) for i in get_variables(self.phrase)]
        
    def make_fractional(self):
        self.f_terms = []
        for i in self.terms:
            start = 0
            cur = 1
            while cur < len(i):
                if is_number(i[start:cur]):
                    cur += 1
                else:
                    self.f_terms.append(i[start:cur])
                    start = cur
                    cur += 1
                    
                    

    def evaluate_old(self, values):
        result = self.phrase
        while has_sub_function(result):
            temp = get_sub_function(result, 'all')
            result = result[:temp[1]]\
            + '`' + str(Function(temp[0]).evaluate(values))\
            + '~' + result[temp[2]+1:]
        result = replace_variables(result, {'`':'(', '~':')'})
        result = eval(replace_variables(result, values))
        return result

    def evaluate(self, values):
        for i in values:
            phrase = 'self.'+i+'='+str(values[i])
            exec(phrase)
        return eval(self.self_phrase)

    def f_evaluate(self, *values):
        if type(values) != type(()): values = [values]
        for i in range(len(values)):
            temp = self.ordered_variables[i]+'=Fraction('+str(values[i])+')'
            exec(temp)
        return eval(self.self_phrase)

    def __getitem__(self, values):
        if type(values) != type(()): values = [values]
        for i in range(len(values)):
            temp = self.ordered_variables[i]+'='+str(values[i])
            exec(temp)
        return eval(self.self_phrase)

    def __str__(self):
        return self.phrase

    def __repr__(self):
        return str(self)

class fn (Function):

    pass

@timed
def test_1():
    a = 0
    for i in range(10000000):
        a = i
    return a

@timed
def test_2():
    a = 0
    i = 0
    while i < 10000000:
        a = i
        i += 1
    return a
