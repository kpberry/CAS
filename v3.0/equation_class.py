# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:42:52 2015

@author: kberry
"""

from function_class import *
import eqn_helper

class Equation():
    def __init__(self, phrase, cpx = True, constants = {'e':e, 'p':pi}):
        self.complex = cpx
        self.phrase = eqn_helper.make_friendly(phrase)
        self.functions = self.init_functions()
        self.variables = self.init_variables()
        self.terms = self.init_terms()
        self.degree = self.init_degree()
        
    def init_functions(self):
        """returns a list of the functions within an equation's phrase"""
        functions = []
        phrase = self.phrase
        while True:
            try:
                functions.append(Function(phrase[:phrase.index('=')],\
                                          cpx = self.complex))
                phrase = phrase[phrase.index('=')+1:]
            except ValueError:
                functions.append(Function(phrase, cpx = self.complex))
                return functions

    def init_variables(self):
        """returns a list of all of the variables in an equation's phrase"""
        return eqn_helper.get_variables(self.phrase)

    def init_terms(self):
        """returns all of the additive terms of an equation."""
        terms = []
        for i in self.functions:
            terms.append(i.get_terms())
        return terms

    def init_degree(self):
        """returns the greatest exponent of a variable within the equation"""
        degrees = []
        for i in self.functions:
            degrees.append(i.get_degree())
        return max(degrees)
        
    def lin_solve(self, var = 'x', left = None, right = None):
        """moves all terms contianing var to the left and all other terms to
        the right."""
        if left == None:
            left = self.functions[0]
        if right == None:
            right = self.functions[1]
        a = self.isolate_variable(var, left, right)
        left = a.functions[0]
        right = a.functions[1]
        while Function(left.get_phrase()) != Function(var):
            a /= eqn_helper.get_coefficient(left.get_phrase())
            left = a.get_functions()[0]
        if len(left.get_terms()) > 1:
            print('Equation cannot be solved as linear function of '+ var)
            return None
        return a
        
    def quad_solve(self, var = 'x', left = None, right = None):
        if left == None:
            left = self.functions[0]
        if right == None:
            right = self.functions[1]
        left = left.expand()
        right = right.expand()
        a, b, c = 0, 0, 0
        for i in left.get_terms():
            i = Function(i)
            if i.get_degree() == 2:
                a = eqn_helper.get_coefficient(i.get_phrase())
            if i.get_degree() == 1:
                b = eqn_helper.get_coefficient(i.get_phrase())
            if i.get_degree() == 0:
                c = eqn_helper.get_coefficient(i.get_phrase())
        if right != Function('0'):
            print('Equation cannot be solved as quadratic function of ' + var)
            return None
        funct = Function('(-b+sqrt(b**2-4*a*c))/(2*a)', \
        variables = {'a':a, 'b':b, 'c':c})
        first = funct.evaluate()
        funct = Function('(-b-sqrt(b**2-4*a*c))/(2*a)', \
        variables = {'a':a, 'b':b, 'c':c})
        second = funct.evaluate()
        return [first, second]
    
    def cube_solve(self, var = 'x', left = None, right = None):
        if left == None:
            left = self.functions[0]
        if right == None:
            right = self.functions[1]
        left = left.expand()
        right = right.expand()
        a, b, c = 0, 0, 0
        for i in left.get_terms():
            i = Function(i)
            if i.get_degree() == 3:
                a = eqn_helper.get_coefficient(i.get_phrase())
            if i.get_degree() == 2:
                b = eqn_helper.get_coefficient(i.get_phrase())
            if i.get_degree() == 1:
                c = eqn_helper.get_coefficient(i.get_phrase())
            if i.get_degree() == 0:
                d = eqn_helper.get_coefficient(i.get_phrase())
        if right != Function('0'):
            print('Equation cannot be solved as cubic function of ' + var)
            return None
        #to be finished later
        """
        funct = Function('-1/(3a)(b+(1)+(b^2-3ac)/1', \
        variables = {'a':a, 'b':b, 'c':c})
        first = funct.evaluate()
        funct = Function('(-b-sqrt(b**2-4*a*c))/(2*a)', \
        variables = {'a':a, 'b':b, 'c':c})
        second = funct.evaluate()
        return [first, second]
        """

    def isolate_variable(self, var = 'x', left = None, right = None):
        """moves all terms contianing var to the left and all other terms to
        the right."""
        if left == None:
            left = self.functions[0]
        if right == None:
            right = self.functions[1]
        #subtracts terms from the left that lack the requested variable
        left_result = Function('')
        right_result = Function('')
        for i in left.get_terms():
            i = Function(i)
            try:
                i.get_var_names().index(var)
                left_result.set_phrase(left_result.get_phrase()\
                + '+' + i.get_phrase())
            except ValueError:
                right -= i
        left = left_result
        #subtracts terms from the right that have the requested variable
        for i in right.get_terms():
            i = Function(i)
            try:
                i.get_var_names().index(var)
                left -= i            
            except ValueError:
                right_result.set_phrase(right_result.get_phrase()\
                + '+' + i.get_phrase())
        right = right_result
        return Equation(left.get_phrase() + '=' + right.get_phrase()).simplify()
    
    def simplify(self):
        """simplifies all of the coefficients in an equation and returns the
        resulting string"""
        result = ''
        for i in self.functions:
            result = result + i.simplify().get_phrase() + '='
        result = result[:len(result)-1]
        result = eqn_helper.make_friendly(result)
        return Equation(result)

    def is_identity(self):
        """returns True if the equation given is an incontrovertible algebraic
        identity. Works for multivariable equations."""
        for i in range(len(self.functions)-1):
            if self.functions[i] != self.functions[i+1]:
                return False
        return True

    def __add__(self, other):
        """adds a number or function to every function in an equation"""
        phrase = ''
        for i in range(len(self.functions)):
            if i == len(self.functions)-1:
                phrase = phrase + (self.functions[i]+other).phrase
            else:
                phrase = phrase + (self.functions[i]+other).phrase + '='
        return Equation(phrase, cpx = self.complex)

    def __iadd__(self, other):
        return self + other

    def __sub__(self, other):
        """subtracts a number or function from every function in an equation"""
        phrase = ''
        for i in range(len(self.functions)):
            if i == len(self.functions)-1:
                phrase = phrase + (self.functions[i]-other).phrase
            else:
                phrase = phrase + (self.functions[i]-other).phrase + '='
        return Equation(phrase, cpx = self.complex)

    def __isub__(self, other):
        return self - other

    def __mul__(self, other):
        """multiplies every function in an equation by a number or function"""
        phrase = ''
        for i in range(len(self.functions)):
            if i == len(self.functions)-1:
                phrase = phrase + (self.functions[i]*other).phrase
            else:
                phrase = phrase + (self.functions[i]*other).phrase + '='
        return Equation(phrase, cpx = self.complex)

    def __imul__(self, other):
        return self * other

    def __truediv__(self, other):
        """divides every function in an equation by a number or function"""
        phrase = ''
        for i in range(len(self.functions)):
            if i == len(self.functions)-1:
                phrase = phrase + (self.functions[i]/other).phrase
            else:
                phrase = phrase + (self.functions[i]/other).phrase + '='
        return Equation(phrase, cpx = self.complex)

    def __itruediv__(self, other):
        return self / other

    def __pow__(self, other):
        """raises every function in an equation to the power of a function or
        number"""
        phrase = ''
        for i in range(len(self.functions)):
            if i == len(self.functions)-1:
                phrase = phrase + (self.functions[i]**other).phrase
            else:
                phrase = phrase + (self.functions[i]**other).phrase + '='
        return Equation(phrase, cpx = self.cpx)

    def set_phrase(self, phrase):
        """sets an equation's phrase to an input and adjusts its variables
        and functions accordingly"""
        self.phrase = eqn_helper.make_friendly(phrase, self.complex)
        self.variables = eqn_helper.get_variables(self.phrase, self.complex)
        self.functions = self.init_functions()
        self.terms = self.init_terms()
    
    def __getitem__(self, index):
        return self.functions[index]
    
    def set_var_values(self, values):
        #barely meaningful in the context of an equation
        self.values = values

    def get_variables(self):
        return self.variables

    def get_functions(self):
        return self.functions

    def get_phrase(self):
        return self.phrase

    def get_complex(self):
        return self.complex

    def get_terms(self):
        return self.terms
    
    def get_degree(self):
        return self.degree
    
    #@timed
    def full_print(self):
        print("Phrase: " + str(self.phrase))
        print("Variables: " + str(self.variables))
        print("Functions: " + str(self.functions))
        print("Terms: " + str(self.terms))
        print("Degree: " + str(self.degree))
        print("Complex: " + str(self.complex))

    def __repr__(self):
        return self.phrase
    
    def __str__(self):
        return self.phrase

eqn = Equation

#several test equations    
a = Equation('2x+3yzfh=sin(cosh(14ht-l)+t)sin(theta)=9')
b = Equation('k = 1/(4πε)')
c = Equation('4 = 4πε + 3')
d = Equation('a = 2x+3yz-8sin(cos(50-8)+tan(80))-(23)')
f = Equation('2s^(8-5)+sin(x)+3n = 23+yz+2sx+z')
g = Equation('2y^9 = 2*s**(8-5)+sin(x)+3*n+2*x**4/2-2')
h = Equation('(x+1)^2=x^2+2x+1')
i = Equation('1/r + 1/q - q/r + q/r = 1/r + 1/q')
j = Equation('(x+3)(x+4)=0')

