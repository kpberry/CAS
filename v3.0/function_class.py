# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:43:00 2015

@author: kberry
"""

import re
import eqn_helper
import evaluator
import cmath
from datetime import *
from math import *
from k_decorators import *
from vector_class import *
from functools import lru_cache

#interesting construct: 1 + x/(10 ** floor(1 + log(x)/log(10)))
#yields 1.1, 1.2, 1.3 ... 1.9, 1.10, 1.11, 1.12 ... 1.99, 1.100, etc.


#!! simple_functions and complex_functions should be moved to eqn_helper so
#any additions or edits can just be made there
#possibly connect them both to the function string regex?

"""This program creates a Function class given a string input. The function
can then be evaluated or modified with another Function or number."""
                    
#clearly can't work like this
function_derivatives = {'sin': 'cos', 'cos': '-sin', 'tan': 'sec**2'}
                    
class Function:
    def __init__(self, phrase, var_values = None, variables = None,\
    cpx = True, constants = {'e':e, 'pi':pi, 'I':1j, \
    'π':pi, 'inf':'inf', 'oo':'inf'}, asimp = True):
        """makes a Function given a string phrase and isolates its variables"""
        self.complex = cpx
        self.phrase = phrase
        self.phrase = eqn_helper.make_friendly(\
        self.phrase, constants.keys(), self.complex)
        if constants != None:
            for name in constants:
                self.phrase = eqn_helper.replace_constants(\
                self.phrase, constants[name], name)
            self.phrase = eqn_helper.make_friendly(\
            self.phrase, constants.keys(), self.complex)
        else:
            self.constants = dict('')
        self.constants = constants
        #autosimplify
        self.asimp = asimp
        self.var_names = eqn_helper.get_variables(self.phrase, self.complex)
        if variables == None:
            #default list of variables for testing purposes
            if var_values == None:
                self.var_values = [i+1 for i in range(len(self.var_names))]
            else:
                self.var_values = var_values
            #the order of variable assignment and dictionary creation allows
            #the variables in a Function to simply be assigned left to right
            self.variables = dict(zip(self.var_names, self.var_values))
        else:
            self.set_variables(variables)
        self.terms = self.init_terms()
        self.degrees = self.init_degrees()
    
    def evaluate(self, variables = None):
        """takes a Function defined by the items in a phrase 
        and evaluates it given the values in the values array"""
        phrase = self.phrase
        #sets variables to their previously assigned values
        if type(variables) == type([0]):
            for i in range(len(variables)):
                if i < len(self.var_values):
                    phrase = eqn_helper.replace_variables(\
                        phrase, variables[i], self.var_names[i])
        elif variables != None:
            for name in variables:
                phrase = eqn_helper.replace_variables(\
                phrase, variables[name], name)
        elif variables == None:
            for name in self.variables:
                phrase = eqn_helper.replace_variables(\
                phrase, self.variables[name], name)
        phrase = self.eval_functions(phrase)
        #this try-catch setup is obviously naïve, but it's a useful way to keep
        #the program running while trying to evaluate many Functions for making
        #a graph or something of the like
        try:
            try:
                return_term = evaluator.evaluate_numbers(phrase)
            except ValueError:    
                print('Kevin\'s term evaluator failed on:', phrase)
                return_term = eval(phrase)
            return return_term
        except ZeroDivisionError:
            print('Zero Division Error.')
            return 0
        except SyntaxError:
            print('Syntax Error.')
            return_term = eval(eqn_helper.make_friendly(phrase))
            return return_term
            
    def eval_functions(self, phrase):
        """parses the equation and attempts to evaluate each function therein.
        Works recursively, calling itself again for each nested item."""
        inside = 0
        function = ""
        index = 0
        outdex = 0
        for i in range(len(phrase)):
            if eqn_helper.get_function_name(phrase) != "":
                function = eqn_helper.get_function_name(phrase, self.complex)
                inside = eqn_helper.get_function_term(phrase)
                index = eqn_helper.get_index(phrase)
                outdex = eqn_helper.get_outdex(phrase)
                #the funky bit in that string just converts the float input
                #to a string with 12 decimal places
                try:
                    middle = "{:.17f}".format(float(\
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
        if funct != "sum":           
            term = Function(eqn_helper.unshell(phrase),\
                        cpx = self.complex, asimp = self.asimp,\
                        constants = self.constants).evaluate()
        else:
            return sign * self.eval_sum(phrase)
        try:
            return sign * eqn_helper.simple_functions[funct](term)
        except TypeError:
            return sign * eqn_helper.complex_functions[funct](term)
        except KeyError:
            if funct == "norm":
                if type(term) != type(Vector(0)):
                    term = Vector(term[0:len(term)])
                result = str(term.normalize() * sign)
                if result[0] == '<':
                    result = result[1:len(result)-1]
                return result
            else:
                if funct == 'sum':
                    print(term)
                    return self.eval_sum(str(term))
        except ValueError:
            print('Value Error.')
            return 0
        except ZeroDivisionError:
            print('Zero Division Error.')
            return 0
        return term
    
    def init_degrees(self):
        """gets the degrees of all of the terms within a function"""
        degrees = []
        for i in self.terms:
            temp = max(eqn_helper.get_degree(i))
            if type(temp) != type(''):
                degrees.append(float(temp))
            else:
                degrees.append(1)
        if degrees == []:
            return [0]
        return degrees
    
    def init_terms(self):
        """Sets up the list of terms within the function"""
        terms = eqn_helper.get_terms(self.phrase)
        return terms
    
    def fsimplify(self, previous_entry = None):
        """Fully simplifies an expression; repeatedly combines like terms and
        trims excess parentheses"""
        current_entry = self.simplify()
        current_entry = current_entry.simplify_parentheses()
        if previous_entry == None\
        or current_entry.phrase != previous_entry.phrase:
            return current_entry.fsimplify(current_entry)
        return current_entry
        
    def simplify(self, previous_entry = None):
        """simplifies the coefficients of a function. Due to the way that the
        individual simplification step is set up, it makes the most sense to
        simply rerun this method recursively until the coefficients have been
        fully simplified."""
        temp = eqn_helper.simplify(self.phrase)
        current_entry = Function(temp, variables = self.variables, \
        asimp = self.asimp, constants = self.constants)
        current_entry = current_entry.combine_like_terms()
        if previous_entry == None\
        or current_entry.phrase != previous_entry.phrase:
            return current_entry.simplify(current_entry)
        return current_entry      
    
    def simplify_parentheses(self):
        """Removes unnecessary parentheses from a function"""
        result = ''
        i = 0
        terms = self.terms.copy()
        while i < len(terms):
            try:
                while re.match('^\(.*\)$', terms[i])\
                and eqn_helper.balanced(terms[i][1:len(terms[i])-1]) and\
                Function(terms[i]) == Function(terms[i][1:len(terms[i])-1]):
                    terms[i] = terms[i][1:len(terms[i])-1]
            except (SyntaxError, IndexError, ValueError):
                pass
            i += 1
        for i in terms:
            result = result + i + '+'
        return Function(result[:len(result)-1], variables = self.variables,\
        asimp = self.asimp, constants = self.constants)
        
    def combine_like_terms(self):
        """Takes terms with the same cores and combines their coefficients."""
        result = []
        terms = self.terms.copy()
        #False if no substitution has been made in the current loop
        subbed = False
        #makes everything a function so that it's easier to work with
        for i in range(len(terms)):
            terms[i] = Function(terms[i], variables = self.variables,\
            constants = self.constants, asimp = self.asimp)
        #trims away the first term each time it checks for like terms
        while len(terms) > 0:
            subbed = False
            for j in range(len(result)):
                #checks that the cores of the terms are the same
                if len(terms) > 0 and eqn_helper.get_core(result[j].phrase)\
                == eqn_helper.get_core(terms[0].phrase):
                    try:
                        if eqn_helper.get_core(result[j].phrase) != '':
                            result[j] = Function(\
                            str(float(eqn_helper.get_coefficient(terms[0].phrase))\
                            + float(eqn_helper.get_coefficient(result[j].phrase)))\
                            + '*' + eqn_helper.get_core(result[j].phrase),\
                            asimp = self.asimp, constants = self.constants)
                        else:
                            result[j] = Function(\
                            str(float(eqn_helper.get_coefficient(terms[0].phrase))\
                            + float(eqn_helper.get_coefficient(result[j].phrase))), \
                            asimp = self.asimp, constants = self.constants)
                        del terms[0]
                        subbed = True
                    except ValueError:
                        if eqn_helper.get_core(result[j].phrase) != '':
                            result[j] = Function(\
                            '('+str(Function(eqn_helper.get_coefficient(terms[0].phrase))\
                            + Function(eqn_helper.get_coefficient(result[j].phrase)))\
                            + ')*' + eqn_helper.get_core(result[j].phrase), \
                            asimp = self.asimp, constants = self.constants)
                            del terms[0]
                            subbed = True
                    except TypeError:
                        result [j] = Function(\
                        str(complex(terms[0].evaluate())\
                        + complex(result[j].evaluate())), asimp = False,\
                        constants = self.constants)
                        del terms[0]
                        subbed = True
            if not subbed:
                result.append(terms[0])
                del terms[0]
                subbed = False
        phrase = ''
        for i in result:
            try:
                if float(i.phrase) != 0:
                    phrase = phrase + i.get_phrase() + '+'
            except ValueError:
                phrase = phrase + i.get_phrase() + '+'
        i = 0
        while i < len(result)-1:
            if Function(result[i].get_phrase()).get_variables() \
            != Function(result[i+1].get_phrase()).get_variables():
                return Function('(' + phrase[:len(phrase)-1] + ')',\
                variables = self.variables, asimp = self.asimp,
                constants = self.constants)
            i += 1
        return Function(phrase[:len(phrase)-1], variables = self.variables,
                               asimp = self.asimp, constants = self.constants)
        
    def expand(self):
        """Distributes all of the coefficients of terms in a function."""
        result = ''
        for i in self.terms:
            result = result + str(self.expand_term(i)) + '+'
        if result == '0+':
            return Function('0', variables = self.variables, \
            constants = self.constants, asimp = self.asimp)
        result = result[:len(result)-1]
        if self.asimp:
            return Function(result, variables = self.variables,\
            constants = self.constants).fsimplify()
        else:
            return Function(result, variables = self.variables,\
            constants = self.constants, asimp = False)
            
    def expand_term(self, term):
        """distributes a coefficient to all of the terms within a group within
        parentheses."""
        if self.phrase == '0':
            return Function('0', variables = self.variables, constants\
            = self.constants, asimp = self.asimp)
        if True:
            coefficient = Function(\
            eqn_helper.get_coefficient(term), variables = self.variables,\
            constants = self.constants, asimp = self.asimp)\
            .simplify_parentheses()
            core = Function(eqn_helper.get_core(term),\
            variables = self.variables, asimp = self.asimp,\
            constants = self.constants).simplify_parentheses()
            #most of the expansion really happens within the Function's
            #multiplication method
            core *= coefficient
            return core
        else:
            return term
        
    def __add__(self, other):
        """adds a function to another numerical or functional object"""
        self = self.simplify_parentheses()
        if type(other) == type(self):
            other = other.simplify_parentheses()
            #makes sure that the variables and constants of both items persist
            var_list = self.variables.copy()
            var_list.update(other.get_variables())
            constant_list = self.constants.copy()
            constant_list.update(other.get_constants())
            if self.asimp:
                return Function(self.phrase+'+'+other.phrase,\
                variables = var_list, constants = constant_list).fsimplify()
            else:
                return Function(self.phrase+'+'+other.phrase,\
                variables = var_list, asimp = False,\
                constants = constant_list) 
        else:
            other = str(other)
            if self.asimp:
                return Function(self.phrase+'+'+other,\
                variables = self.variables,\
                constants = self.constants).fsimplify()
            else:
                return Function(self.phrase+'+'+other,\
                variables = self.variables, asimp = False,\
                constants = self.constants)

    def __iadd__(self, other):
        return self + other

    def __sub__(self, other):
        """subtracts another numerical or Functional object from a Function"""
        self = self.simplify_parentheses()
        if type(other) == type(self):
            other = other.simplify_parentheses()
            var_list = self.variables.copy()
            var_list.update(other.get_variables())
            constant_list = self.constants.copy()
            constant_list.update(other.get_constants())
            if self.asimp:
                return Function(self.phrase+'-'+other.phrase,\
                variables = var_list, constants = constant_list).fsimplify()
            else:
                return Function(self.phrase+'-'+other.phrase,\
                variables = var_list, asimp = False,\
                constants = constant_list)
        else:
            other = str(other)
            if self.asimp:
                return Function(self.phrase+'-'+other,\
                variables = self.variables,\
                constants = self.constants).fsimplify()
            else:
                return Function(self.phrase+'-'+other,\
                variables = self.variables, asimp = False,\
                constants = self.constants)

    def __isub__(self, other):
        return self - other

    def __mul__(self, other):
        """multiplies a function by another numerical or functional object;
        foils any foilable terms, like (a+b+c)*(d+e) -> ad+ae+bd...+ce, etc.
        I still have the other (simpler) algorithm in a copy of this file,
        just in case I choose to use it later."""
        result = ''
        self = self.simplify_parentheses()
        if type(other) == type(self):
            other = other.simplify_parentheses()
            var_list = self.variables.copy()
            var_list.update(other.get_variables())
            constant_list = self.constants.copy()
            constant_list.update(other.get_constants())
            #distributes terms of both Functions
            for i in self.get_terms():
                for j in other.get_terms():
                    result = result + i + '*'+ j + '+'
            result = result[:len(result)-1]
            if self.asimp:
                return Function(result, variables = var_list,\
                constants = constant_list).fsimplify()
            else:
                return Function(result, variables = var_list,\
                asimp = False, constants = constant_list)
        else:
            other = str(other)
            for i in self.get_terms():
                result = result + i + '*' + other + '+'
            result = result[:len(result)-1]
            if self.asimp:
                return Function(result, variables = self.variables,\
                constants = self.constants).fsimplify()
            else:
                return Function(result, variables = self.variables,\
                asimp = False, constants = self.constants)

    def __imul__(self, other):
        return self * other

    def __truediv__(self, other):
        """divides a function by another numerical or functional object"""
        self = self.simplify_parentheses()
        try:
            result = ''
            if type(other) == type(self):
                other = other.simplify_parentheses()
                var_list = self.variables.copy()
                var_list.update(other.get_variables())
                constant_list = self.constants.copy()
                constant_list.update(other.get_constants())
                for i in self.get_terms():
                    result = result + i + '/('+ other.phrase + ')+'
                result = result[:len(result)-1]
                if self.asimp:
                    return Function(result, variables = var_list,\
                    constants = self.constants).fsimplify()
                else:
                    return Function(result, variables = var_list,\
                    asimp = False, constants = self.constants)
            else:
                other = str(other)
                for i in self.get_terms():
                    result = result + i + '/' + other + '+'
                result = result[:len(result)-1]
                if self.asimp:
                    return Function(result, variables = self.variables, \
                    constants = self.constants).fsimplify()
                else:
                    return Function(result, variables = self.variables,\
                    asimp = False, constants = self.constants)
        except ZeroDivisionError:
            return 0

    def __itruediv__(self, other):
        return self / other

    def __oldpow__(self, other):
        """raises a function to the power of another numerical or functional
        object."""
        if type(other) == type(self):
            var_list = self.variables.copy()
            var_list.update(other.get_variables())
            constant_list = self.constants.copy()
            constant_list.update(other.get_constants())
            if self.asimp:
                return Function('('+self.phrase+')**('+other.phrase+')',\
                variables = var_list, constants = constant_list).simplify()
            else:
                return Function('('+self.phrase+')**('+other.phrase+')',\
                variables = var_list, asimp = False, constants = constant_list)
        else:
            other = str(other)
            if self.asimp:
                return Function('('+self.phrase+')**'+other,\
                variables = self.variables,\
                constants = self.constants).simplify()
            else:
                return Function('('+self.phrase+')**'+other,\
                variables = self.variables, asimp = False,\
                constants = self.constants)
                
    def __pow__(self, other):
        """raises a function to the power of another numerical or functional
        object. For integer powers, multiplies the function by the original
        term n times."""
        if type(other) == type(self):
            var_list = self.variables.copy()
            var_list.update(other.get_variables())
            constant_list = self.constants.copy()
            constant_list.update(other.get_constants())
            if self.asimp:
                return Function('('+self.phrase+')**('+other.phrase+')',\
                variables = var_list, constants = constant_list).simplify()
            else:
                return Function('('+self.phrase+')**('+other.phrase+')',\
                variables = var_list, asimp = False, constants = constant_list)
        else:
            other = str(other)
            if self.asimp:
                result = Function('1', variables = self.variables,\
                constants = self.constants, asimp = self.asimp)
                try:
                    #expands everything, treating exponentiation as repeated
                    #multiplication by a base if the power is an integer
                    for i in range(int(other)):
                        result *= self
                    return result.simplify()
                except ValueError:
                    other = str(other)
                    if self.asimp:
                        return Function('('+self.phrase+')**'+other,\
                        variables = self.variables,\
                        constants = self.constants).simplify()
                    else:
                        return Function('('+self.phrase+')**'+other,\
                        variables = self.variables, asimp = False,\
                        constants = self.constants)
            else:
                return Function('('+self.phrase+')**'+other,\
                variables = self.variables, asimp = False,\
                constants = self.constants)
                
    def __ipow__(self, other):
        return self ** other

    def __eq__(self, other_function, degree = 3, tolerance = 1e-10):
        """determines whether or not two functions are equal by comparing a set
        number of terms, specified by degree, at a certain tolerance. Cannot
        determine if equations are precisely equal due to floating point error
        that would be very difficult to otherwise circumvent."""
        try:
            if type(other_function) != type(self):
                return False
            for i in range(1, degree):
                #adds incremental values to the variable array of this function
                temp = dict(zip(self.var_names,\
                [j+i for j in self.variables.values()]))
                if abs(self.evaluate(temp)-other_function.evaluate(temp))\
                > tolerance:
                    return False
            return True
        #index error indicates that one function has more variables than the
        #other, meaning that the test is invalid
        except IndexError:
            return False
    
    def set_phrase(self, phrase):
        """sets the function's phrase to the given String phrase and sets
        its variables to those therein"""
        self.phrase = phrase
        self.var_names = eqn_helper.get_variables(self.phrase, self.complex)
        if len(self.var_values) != len(self.var_names):
            self.var_values = [i+1 for i in range(len(self.var_names))]
        self.variables = dict(zip(self.var_names, self.var_values))

    def set_complex(self, cpx):
        """sets True or False that the function uses complex variables"""
        self.complex = cpx
        self.phrase = eqn_helper.make_friendly(self.phrase, cpx)
        self.var_names = eqn_helper.get_variables(self.phrase, self.complex)
        if len(self.var_values) != len(self.var_names):
            self.var_values = [i+1 for i in range(len(self.var_names))]
        self.variables = dict(zip(self.var_names, self.var_values))

    def set_variables(self, variables):
        """sets the function's variables to those in an input array"""
        self.variables = variables
        self.var_names = [name for name in variables]
        self.var_values = [variables[name] for name in variables]
    
    def set_variable(self, var, value):
        """sets a variable in the variables array to a given value; adds the 
        variable if it is not alread nominally present"""
        try:
            self.variables[var] = value
            self.var_names = [name for name in self.variables]
            self.var_values = [self.variables[name] for name in self.variables]
        except IndexError:
            self.variables.append((name, value))
    
    def set_var_names(self, var_names):
        """sets the function's variable names to those in an input array"""
        self.var_names = var_names
        self.variables = dict(zip(self.var_names, self.var_values))

    def set_var_values(self, values):
        """sets the function's variable values to those in an input array"""
        self.var_values = values
        self.variables = dict(zip(self.var_names, self.var_values))
    
    def set_asimp(self, tf):
        """sets autosimplification to the boolean value of tf"""
        self.asimp = tf
    
    def __getitem__(self, values):
        try:
            values = list(values)
            return self.evaluate(values)
        except TypeError:
            return self.evaluate([values])

    def get_phrase(self):
        return self.phrase

    def get_complex(self):
        return self.cpx

    def get_variables(self):
        return self.variables
    
    def get_var_names(self):
        return self.var_names

    def get_var_values(self):
        return self.var_values

    def get_terms(self):
        return eqn_helper.get_terms(self.phrase)
    
    def get_constants(self):
        return self.constants

    def get_degree(self):
        try:
            return max(self.degrees)
        except TypeError:
            return 'exponential'

    def full_print(self):
        """prints all of the attributes of a function."""
        #print("Original phrase: " + str(self.original_phrase))
        print("Phrase: " + str(self.phrase))
        print("Variables: " + str(self.variables))
        print("Constants: " + str(self.constants))
        print("Complex: " + str(self.complex))
        print("Terms: " + str(self.get_terms()))
        print("Degree: " + str(self.get_degree()))
    
    def __repr__(self):
        return self.phrase

    def __str__(self):
        return self.phrase
        
    def num_derive(self, variables = None, tolerance = 1e-7):
        """Evaluates a derivative at a point. Works better the slower a 
        Function grows. Relatively low tolerance due to problems with floating
        point precision."""
        if variables == None:
            left = self.evaluate(self.variables)
            right = self.evaluate(dict(zip(self.var_names,\
            [i + tolerance for i in self.variables.values()])))
        else:
            left = self.evaluate(variables)
            right = self.evaluate(variables = dict(zip(variables.keys(),\
            [i + tolerance for i in variables.values()])))
        return round((right-left)/(tolerance), 6)
    
    def eval_sum(self, phrase):
        """Returns the sum of a phrase of the form sum(funct, low, up, step)
        infinite sums are those with an upper boind of oo or inf"""
        total = 0
        match = re.match('(sum\((.+),(.+),(.+),(.+?).$)', phrase)
        if match:
            funct = Function(match.groups()[1],\
            constants = self.constants)
            start = Function(match.groups(0)[2], constants = \
            self.constants, variables = self.variables).evaluate()
            if re.search('inf', match.groups(0)[3]):
                end = 'inf'
            else:
                end = Function(match.groups(0)[3], constants = \
                self.constants, variables = self.variables).evaluate()
            dx = Function(match.groups(0)[4], constants = \
            self.constants, variables = self.variables).evaluate()
        else:
            match = re.match('(sum\((.+),(.+),(.+?).$)', phrase)
            funct = Function(match.groups()[1],\
            constants = self.constants)
            start = Function(match.groups(0)[2], constants = \
            self.constants, variables = self.variables).evaluate()
            if re.search('inf', match.groups(0)[3]):
                end = 'inf'
            else:
                end = Function(match.groups(0)[3], constants = \
                self.constants, variables = self.variables).evaluate()
            dx = 1
        if dx == 0:
            return 0
        if end == 'inf':
            prev, count, div_chance = -1, 0, 0
            while round(total, 10) - round(prev, 10) != 0:
                prev = total
                total += funct[start]
                start += dx
                if count % 1000 == 1:
                    if funct[start * 10 + 1] / funct[start * 10] > 1:
                        div_chance += 1
                    if funct[start * 10] >= 1/count:
                        div_chance += 1
                if div_chance > 5:
                    #return 'oo'
                    return '0'
                count += 1
                if count > 10000:
                    return total
            return round(total, 9)
        while start < end:
            total += funct[start]
            start += dx
        return total
    
    def derive(self):
        result = ''
        for i in self.terms:
            result = result + self.power_rule(i)+'+'
        result = result[:len(result)-1]
        return Function(result)
        
    def power_rule(self, term):
        """returns the derivative of x^n, where n is constant"""
        if get_degree(term) == '0':
            return '0'
        try:
            core = term[len(get_coefficient(term)):term.index('**')]
        except ValueError:
            core = term[len(get_coefficient(term)):]
        degree = str(get_degree(term)[0])
        if degree[0] == '0':
            return '0'
        coefficient = simplify(get_coefficient(term) + '*' + degree)
        #coefficient = derivative(core) + '*' + coefficient
        power = '('+simplify(degree + '-1')+')'
        return coefficient + core + '**' + power
    
    def product_rule(self, left, right):
        pass
        #return left +'*' + derive(right) + '+' + right + '*' + derive(left)
    
    def quotient_rule(self, left, right):
        pass
        #return + '+' + derive(left) + '*' + \
        #right + '-' + derive(right) + '*' + left + ')/(' + right + ')**2'
    
    def function_derive(self, fn):
        pass
    
    
"""adds a series of functions to a testing array. The best way to use this
is to type something along the lines of:
for funct in test:
    print(funct.method())

where 'method' is some method of the Function class."""

@timed
def test(array = 0):
    """adds a series of functions to a testing array."""
    functs = []
    #expected values
    ev = []
    functs.append(Function('sin(1)*cos(tan(2))'))
    ev.append(-0.4849738063847227)
    functs.append(Function("sin(cos(sin(x)))+2"))
    ev.append(2.618134070952928)
    functs.append(Function("2*5^-2"))
    ev.append(0.08)
    functs.append(Function("-11 + 2*-3 -4 -((4/5 + 5)/6 + 1/9*6)"))
    ev.append(-22.6333333333333333)
    functs.append(Function("log(10000)log(10000)3"))
    ev.append(48)
    functs.append(Function("csc(ln(cos(sin(fact(y)*3))))+2", [2]))
    ev.append(-23.287660798962673)
    functs.append(Function("asin(cos(xsin(x)))", [201]))
    ev.append(1.4443661068985891)
    functs.append(Function("acsc(cos(xsin(x))+1)", [201]))
    ev.append(0.5259136634428558)
    functs.append(Function("sin(x) + ln(cos(x - sin(x)))"))
    ev.append(0.8288522725617978)
    functs.append(Function("sin(asin(cos(x-(cos(x+1)))))"))
    ev.append(0.15403378213802238)
    functs.append(Function("x^1.5-5", [11]))
    ev.append(31.4828726939094)
    functs.append(Function("2x^3+1/(x^2)", [2+1j]))
    ev.append(4.12+21.84j)
    functs.append(Function("x/2", [2+15j]))
    ev.append((1+7.5j))
    functs.append(Function("2*3*x^(3-1)+1", [3]))
    ev.append(55)
    functs.append(Function('e**(Ipi)'))
    ev.append(-1)
    #return 1/e**2
    s = Function('0', asimp = False)
    for i in range(10):
        s += Function(str((-1)**i/eqn_helper.fact(i))+'*x**'+str(i))
    ev.append(0.1350970017636685)
    #returns 4/(5-x)
    s.set_variable('x', 2)
    functs.append(s)
    t = Function('', asimp = False)
    for i in range(10):
        t += Function('(x+2)**'+str(i)+'/(7**'+str(i+1)+')')
    t *= 4
    t.set_variable('x', 2)
    functs.append(t)
    ev.append(1.3283838684216895)
    #need to fix the degree getting on this one
    functs.append(Function('2x+3y**2z/5(x)e-8'))
    ev.append(13.571629164905126)
    functs.append(Function('m(c^2-mc^-2+mc^sin(x)+mc^(x-3))'))
    ev.append(5.852760890486783)
    functs.append(Function('x-x^2/2+x^3/3-x^4/4+x^5/5'))
    ev.append(0.783333333333333)
    #intended for testing distribution and simplification methods
    functs.append(Function('(x+3)(2x+3)+4(2x+3)'))
    ev.append(40)
    functs.append(Function('2x(x+2)-3x(x+2)+3(x+2)-x(x+1)'))
    ev.append(4)
    functs.append(Function('2x(3x+2)+2(3x+2)'))
    ev.append(20)
    #returns e^(-pi/1)
    functs.append(Function('I^I'))
    ev.append(0.20787957635076193)
    functs.append(Function('<2xsin(y), 2, 3> cross <1, 2, 3>'))
    ev.append(Vector(0, -2.45578456095409, 1.6371897073027268))
    functs.append(Function('<2x,3y>dot<3x,4y>'))
    ev.append(54)
    functs.append(\
    Function('<2xsin(y), 2, 3> cross <1, 2, 3> * (<2x, 3y> dot <3x, 4y>)'))
    ev.append(Vector(0.0, -132.61236629152086, 88.40824419434725))
    #returns 1/x
    functs.append(Function('2*3/(2x)/3', [3j]))
    ev.append(-0.3333333333333333j)
    functs.append(Function('(cos(a)+jsin(b))*(cos(a)+jsin(b))'))
    ev.append(-0.5348952287061071+0.9825909928678536j)
    #this is actually just a transcription of a physics problem I had to do
    functs.append(Function('V/(mP/(A**2*r)*(1+a(T-t)))', variables = {'V':53.8, \
    'm':0.2,'P':1.2e-7, 'r':7.8e3, 'T':393, 't':293,\
    'A':pi*((1.2e-3)/2)**2, 'a':6e-3}))
    ev.append(13.978172669196836)
    functs.append(Function('<2, 3>*(<2, csch(x)>'+\
    'dot <2, sin(x)>)cross<sin(<2, 2>dot<2, cos(x)>)>'))
    ev.append(Vector(-8.799826327227331, -13.199739490840994))
    funct = Function('2x+3')
    functs.append(funct ** 4)
    ev.append(625)
    functs.append(Function('(2x+3)+(x+3)+(x+3)+(x+3)**2'))
    ev.append(29)
    functs.append(Function('<2x+3, 2> dot <2x+3x, 1, 2> *sum(0.3^x, 0, oo)'))
    ev.append(38.571428583)
    functs.append(Function('<norm(<2, 3, 4>)>cross<norm(3, 4, 5)>'))
    ev.append(Vector(-0.026261286571944542,\
    0.05252257314388903, -0.026261286571944514))
    if array == 0:
        return functs
    if array == 1:
        return ev
    return [functs, ev]

#dummy copy of function class that's easier to type and use
class fn(Function):
    pass

@timed
def etest(printing = False):
    a = test(2)
    if not printing:
        try:
            for i in range(len(a[0])):
                val = a[0][i].evaluate()-a[1][i]
                if abs(val) > 1e-10:
                    print()
                    print('ERROR:')
                    a[0][i].full_print()
                    print()
                    print('IMPROPER VALUE:', a[0][i].evaluate())
                    print('PROPER VALUE:', a[1][i])
                    print()
        except:
                print('Messed up on ' + str(a[0][i]))
    else:
        for i in range(len(a[0])):
            try:
                val = a[0][i].evaluate()-a[1][i]
                if abs(val) > 1e-10:
                    print()
                    print('ERROR:')
                    a[0][i].full_print()
                    print()
                    print('IMPROPER VALUE:', a[0][i].evaluate())
                    print('PROPER VALUE:', a[1][i])
                    print()
                else:
                    print('Function: ', a[0][i])
                    print(val)
            except:
                print('Messed up on ' + str(a[1][i]))

@timed
def ftest(printing = False):
    a = test(2)
    if not printing:
        for i in range(len(a[0])):
            print(a[0][i].fsimplify().evaluate()-a[1][i])
    else:
        for i in range(len(a[0])):
            print('Function: ', a[0][i])
            print(a[0][i].fsimplify())
            print(a[0][i].fsimplify().evaluate()-a[1][i])

@timed
#range eval
def reval(funct, low, up, step = 1, printing = True):
    if type(funct) == type(''):
        funct = Function(funct)
    if printing:
        while low < up:
            print(funct[low])
            low += step
    else:
        result = []
        while low < up:
            result.append(funct.evaluate(low))
            result += step
        return result
        
