# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 08:08:10 2015

@author: kberry
"""

from eqn_helper import make_friendly, replace_constants, replace_variables,\
get_variables, fact, get_function_name, get_function_term, get_index,\
get_outdex, unshell, simple_functions, complex_functions
from math import sin, cos, tan, log, asin, acos, atan, sinh, cosh, tanh,\
asinh, acosh, atanh, e, pi
from evaluator import evaluate_numbers
from raw_evaluator import RawEvaluator
from vector_class import Vector
from function_class import Function
import cmath
from k_decorators import timed

class RawFunction:
    def __init__(self, phrase, cpx = False, constants = {'e':e, 'pi':pi,\
    'I':1j, 'π':pi, 'inf':'inf', 'oo':'inf'}):
        """makes a Function given a string phrase and isolates its variables"""
        self.complex = cpx
        self.phrase = phrase
        self.phrase = make_friendly(\
        self.phrase, constants.keys(), self.complex)
        if constants != None:
            for name in constants:
                self.phrase = replace_constants(\
                self.phrase, constants[name], name)
            self.phrase = make_friendly(\
            self.phrase, constants.keys(), self.complex)
        else:
            self.constants = dict('')
        self.constants = constants
        self.var_names = get_variables(self.phrase, self.complex)
        self.imd = RawEvaluator(self.phrase)
    
    def evaluate(self, variables = None, phrase = None):
        """takes a Function defined by the items in a phrase 
        and evaluates it given the values in the values array"""
        phrase = self.phrase
        #sets variables to their previously assigned values
        if type(variables) == type([0]):
            for i in range(len(variables)):
                if i < len(self.var_names):
                    phrase = replace_variables(\
                    phrase, variables[i], self.var_names[i])
                else:
                    break
        elif variables != None:
            for name in variables:
                phrase = replace_variables(\
                phrase, variables[name], name)
        phrase = self.eval_functions(phrase)
        #this try-catch setup is obviously naïve, but it's a useful way to keep
        #the program running while trying to evaluate many Functions for making
        #a graph or something of the like
        try:
            try:
                return_term = evaluate_numbers(phrase)
            except ValueError:    
                print('Kevin\'s term evaluator failed on:', phrase)
                return_term = eval(phrase)
            return return_term
        except ZeroDivisionError:
            print('Zero Division Error.')
            return 0
        except SyntaxError:
            print('Syntax Error.')
            return_term = eval(make_friendly(phrase))
            return return_term
        except OverflowError:
            print('Overflow Error. Value too large or too small.')
            return 0
        
    def eval_functions(self, phrase):
        """parses the equation and attempts to evaluate each function therein.
        Works recursively, calling itself again for each nested item."""
        inside = 0
        function = ""
        index = 0
        outdex = 0
        for i in range(len(phrase)):
            if get_function_name(phrase) != "":
                function = get_function_name(phrase, self.complex)
                inside = get_function_term(phrase)
                index = get_index(phrase)
                outdex = get_outdex(phrase)
                #the funky bit in that string just converts the float input
                #to a string with 9 decimal places
                try:
                    middle = "{:.9f}".format(float(\
                    self.eval_function(str(function)+"("+str(inside)+")")))
                except (TypeError, ValueError):
                    middle = str(\
                    self.eval_function(str(function)+"("+str(inside)+")"))
                if len(phrase) > 0 and phrase[index] == 'j':
                    phrase = phrase[:index+2] + str(middle) + phrase[outdex+1:]
                else:
                    phrase = phrase[:index] + str(middle) + phrase[outdex+1:]
        return phrase
        
    def eval_function(self, phrase):
        """evaluates a given function by splitting it into its term and its
        function component, then using the appropriate pre-defined math
        operation"""
        #manages the sign of the output
        sign = 1.0
        if phrase[0] == "-":
            funct = phrase[1:phrase.index("(")]
            sign = -1.0
        #gets everything before the first parenthesis in the phrase
        else:
            funct = phrase[:phrase.index("(")]
        #gets / evaluates the term as the item inside the parentheses;
        #if the term is a summation, handles that separately so as not
        #to evaluate the terms inside beforehand          
        term = rfn(unshell(phrase), cpx = self.complex,\
        constants = self.constants).evaluate()
        try:
            return sign * simple_functions[funct](term)
        except TypeError:
            return sign * complex_functions[funct](term)
        except KeyError:
            if funct == "norm":
                if type(term) != type(Vector(0)):
                    term = Vector(term[0:len(term)])
                result = str(term.normalize() * sign)
                if result[0] == '<':
                    result = result[1:len(result)-1]
                return result
        except ValueError:
            print('Value Error.')
            return 0
        except ZeroDivisionError:
            print('Zero Division Error.')
            return 0
        return term
            
    """Calls the Function class's version of these methods to ensure that the
    result is simplified before being returned as a RawFunction."""
        
        
    def __add__(self, other):
        return RawFunction(str(Function(self.phrase) + other),\
        cpx = self.complex, constants = self.constants)
    
    def __iadd__(self, other):
        return self + other
    
    def __sub__(self, other):
        return RawFunction(str(Function(self.phrase) - other),\
        cpx = self.complex, constants = self.constants)
    
    def __isub__(self, other):
        return self - other
    
    def __mul__(self, other):
        return RawFunction(str(Function(self.phrase) * other),\
        cpx = self.complex, constants = self.constants)
    
    def __imul__(self, other):
        return self * other
    
    def __truediv__(self, other):
        return RawFunction(str(Function(self.phrase) / other),\
        cpx = self.complex, constants = self.constants)
    
    def __itruediv__(self, other):
        return self / other
    
    def __pow__(self, other):
        return RawFunction(str(Function(self.phrase) ** other),\
        cpx = self.complex, constants = self.constants)
    
    def __ipow__(self, other):
        return self + other
            
class rfn(RawFunction):
    pass

@timed
#range eval
def reval(funct, low, up, step = 1, printing = False):
    if type(funct) == type(''):
        funct = RawFunction(funct)
    result = []
    while low < up:
        result.append(funct.evaluate([low]))
        low += step
    return result
    