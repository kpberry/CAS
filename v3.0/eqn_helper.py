# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:41:13 2015

@author: kberry
"""

import re
from math import sin, cos, tan, log, asin, acos, atan, sinh, cosh, tanh,\
asinh, acosh, atanh, floor, ceil, factorial
import cmath




#numerators and denominators; they'll help with degree getting




"""This is a group of methods that are potentially useful for different kinds 
of function parsers or manipulators, so I kept them separate from the actual
function class. I did not use all of them in my current version of the equation
parser because some are remnants of its earlier versions."""

#list of default operators
operators = ["+", "-", "/", "*", "%", "^"]
#not a compiled regular expression because this has to be put inside others
#later; it also recognizes infinity as a function, but I'm not sure about 
#how I actually want to implement that
function_pattern =\
r'((?:a*(?:(sin|cos|tan|csc|cot|sec)h*|bs))' + \
r'|(?:l(?:og|n))|inf|sum|fact|cbrt|sqrt|dot|cross|norm|floor|ceil|point)'
number_pattern = r'(\-?[\d]+\.?[\d]*(e[\d\-]+(\.?[\d])?)?)'
symbol_pattern = r'[a-zA-Zα-ωΑ-ΩЀ-ӿ]'

#list of functions with corresponding definitions put in one central location
#to make editing easier
simple_functions = {'sin': lambda x: sin(x), 'cos': lambda x: cos(x),
                    'tan': lambda x: tan(x), 'csc': lambda x: 1/sin(x),
                    'sec': lambda x: 1/cos(x), 'cot': lambda x: 1/tan(x),
                    'ln': lambda x: log(x), 'log': lambda x: log(x)/log(10),
                    'sqrt': lambda x: x**(1/2), 'cbrt': lambda x: x**(1/3),
                    'asin': lambda x: asin(x), 'acos': lambda x: acos(x),
                    'atan': lambda x: atan(x), 'acsc': lambda x: asin(1/x),
                    'asec': lambda x: acos(1/x), 'acot': lambda x: atan(1/x),
                    'abs': lambda x: abs(x), 'fact': lambda x: factorial(int(x)),
                    'sinh': lambda x: sinh(x), 'cosh': lambda x: cosh(x),
                    'tanh': lambda x: tanh(x), 'csch': lambda x: 1/sinh(x),
                    'sech': lambda x: 1/cosh(x), 'coth': lambda x: 1/tanh(x),
                    'asinh': lambda x: asinh(x), 'acosh': lambda x: acosh(x),
                    'atanh': lambda x: atanh(x), 'acsch': lambda x: asinh(1/x),
                    'asech': lambda x: acosh(1/x), '': lambda x: x,
                    'acoth': lambda x: atanh(1/x), 'floor': lambda x: floor(x),
                    'ceil': lambda x: ceil(x), 
                    'point': lambda x: x/(10 ** floor(1+log(x)/log(10)))
                    }
                    
complex_functions = {'sin': lambda x: cmath.sin(x), 
                    'cos': lambda x: cmath.cos(x),
                    'tan': lambda x: cmath.tan(x), 
                    'csc': lambda x: 1/cmath.sin(x),
                    'sec': lambda x: 1/cmath.cos(x), 
                    'cot': lambda x: 1/cmath.tan(x),
                    'ln': lambda x: cmath.log(x), 
                    'log': lambda x: cmath.log(x)/cmath.log(10),
                    'fact': lambda x: factorial(int(x)),
                    'asin': lambda x: cmath.asin(x), 
                    'acos': lambda x: cmath.acos(x),
                    'atan': lambda x: cmath.atan(x), 
                    'acsc': lambda x: cmath.asin(1/x),
                    'asec': lambda x: cmath.acos(1/x), 
                    'acot': lambda x: cmath.atan(1/x),
                    'sinh': lambda x: cmath.sinh(x), 
                    'cosh': lambda x: cmath.cosh(x),
                    'tanh': lambda x: cmath.tanh(x), 
                    'csch': lambda x: 1/cmath.sinh(x),
                    'sech': lambda x: 1/cmath.cosh(x),
                    'coth': lambda x: 1/cmath.tanh(x),
                    'asinh': lambda x: cmath.asinh(x), 
                    'acosh': lambda x: cmath.acosh(x),
                    'atanh': lambda x: cmath.atanh(x), 
                    'acsch': lambda x: cmath.asinh(1/x),
                    'asech': lambda x: cmath.acosh(1/x),
                    'acoth': lambda x: cmath.atanh(1/x)
                    }

def replace_variables(phrase, replacement, var = 'x'):
    """Replaces all instances of a named variable in a phrase with a 
    replacement, 'x' by default."""
    i = 0
    while i < len(phrase):
        match = re.match('((sum.+?,).+,.+?\))', phrase[i:])
        if match:
            i += len(match.groups(0)[1]) - 1    
        match = re.match(function_pattern, phrase[i:])
        if match:
            i += len(match.groups(0)[0]) 
        if re.match(var, phrase[i:]):
            phrase = phrase[:i]+'('+str(replacement)+')'+phrase[i+len(var):]
            i += 2 + len(var)
        else:
            i += 1
    return phrase

def replace_constants(phrase, replacement, var = 'x'):
    """Replaces all instances of a named variable in a phrase with a 
    replacement, 'x' by default."""
    i = 0
    while i < len(phrase):   
        match = re.match(function_pattern, phrase[i:])
        if match:
            i += len(match.groups(0)[0]) 
        if re.match(var + '(?!\d)', phrase[i:]):
            if i > 0 and re.match('\d' + var + '\-', phrase[i-1:]):
                i += 1 + len(var)
            elif var == 'inf':
                phrase = phrase[:i]+str(replacement) + phrase[i+len(var):]
                i += 1+len(var)
            else:
                phrase = phrase[:i]+'('+str(replacement)+')'+phrase[i+len(var):]
                i += 2 + len(var)
        else:
            i += 1
    return phrase
    
def get_variables(eqn, cpx = True):
    """returns an ordered list of distinct variable names within a function.
    Skips j to avoid conflicts with imaginary numbers."""
    variables = []
    #finds all characters surrounded by numbers or other non words
    variables = re.findall(r'(?<=[\W\d\b])([a-df-zA-Zα-ωΑ-Ω])(?=[\W\d\b])', \
    eqn)
    #finds variables at the end of the string specifically; necessary
    #because of the way Python handles String boundaries
    match = re.search(r'[\W\d\b]('+symbol_pattern+')$', eqn)
    if match:
        variables.append(match.groups(0)[0])
    #finds variables at the beginning of the string
    match = re.search(r'^('+symbol_pattern+')[\W\d\b]', eqn)
    if match:
        variables.insert(0, match.groups(0)[0])
    #matches a variable if it's the only thing in the string
    match = re.search(r'^('+symbol_pattern+')$', eqn)
    if match:
        variables.append(match.groups(0)[0])
    #creates a list and appends non-duplicate variables
    result = []
    for i in range(len(variables)):
        if cpx:
             if variables.index(variables[i]) == i and variables[i] != 'j':
                result.append(variables[i])
        else:
            if variables.index(variables[i]) == i:
                result.append(variables[i])
    return result

def make_friendly(phrase, constants = [], cpx = True):
    """handles implicit multiplication, converts double signs into single ones,
    ensures that complex numbers work, deals with exponential terms like 2e8"""
    phrase = trim_spaces(phrase)
    phrase = phrase.replace('--', '+')
    phrase = phrase.replace('+-', '-')
    phrase = phrase.replace('++', '+')
    phrase = phrase.replace('^', '**')
    if len(phrase) > 0 and phrase[0] == '+':
        phrase = phrase[1:]
    #handles exponential terms; replaces them with a dollar sign to be 
    #back-converted later
    phrase = re.sub(\
    r'(\d|'+symbol_pattern+')e(-?)(?:0*)(\d+)', r'\1$\2\3', phrase)
    if cpx:
        phrase = re.sub('([\d\)])(?!j)((?:\(|\<)|'+symbol_pattern+')', r'\1*\2', phrase)
        #converts a single j into 1j to agree with python's complex numbers
        phrase = re.sub('(?<!\d)j', '1j', phrase)
    else:
        phrase = re.sub('([\d\)])(\(|'+symbol_pattern+')', r'\1*\2', phrase)
    #both of these handle implicit multiplication
    phrase = re.sub('((?:\)|\>)|'+symbol_pattern+')(\d)', r'\1*\2', phrase)
    phrase = re.sub(r'(\d)('+function_pattern+')', r'\1*\2', phrase)
    #handles each instance of implicit multiplication of variables and functions
    phrase = implicit_multiply_variables(phrase, constants)
    #makes the dollar sign from earlier proper
    phrase = phrase.replace('$', 'e')
    return phrase

def implicit_multiply_variables(phrase, constants = []):
    """finds instances where variables are implicitly multiplied and
    explicitly multiplies them. Makes sure to ignore strings of characters
    that form one of the pre-defined functions"""
    i = 0
    temp = phrase
    constant_pattern = ''
    #there are still significant issues with constant handling
    #in particular, fsimplify on test()[15] causes problems with exponents
    for j in constants:
        constant_pattern = constant_pattern + j + '|'
    constant_pattern = '(' + constant_pattern[:len(constant_pattern)-1] + ')'
    while i < len(phrase):
        temp = phrase[i:]
        if re.match(function_pattern, temp):
            i += len(re.match(function_pattern, temp).groups(0)[0])
        elif re.match(constant_pattern, temp):
            i += len(re.match(constant_pattern, temp).groups(0)[0])
        elif re.match(symbol_pattern+'{2}', temp):
            phrase = phrase[:i] + temp[0] + '*' + temp[1:]
            i += 1
        elif re.match(symbol_pattern+'\(', temp)\
        and not re.match(r'(\d|'+symbol_pattern+')e(-?)(?:0*)(\d+)', temp):
            phrase = phrase[:i] + temp[0] + '*' + temp[1:]
            i += 1
        elif re.match(symbol_pattern+'\<', temp)\
        and not re.match(r'(\d|'+symbol_pattern+')e(-?)(?:0*)(\d+)', temp):
            phrase = phrase[:i] + temp[0] + '*' + temp[1:]
            i += 1
        """
        elif re.match(constant_pattern, temp):
            i += len(re.match(constant_pattern, temp).groups(0)[0])
        """
        i += 1
    return phrase       

def get_function_name(phrase, cpx = True):
    """returns the part of the function before the first parenthesis"""
    try:
        #prevents confusion between cross and dot, which are operators
        result = 'cross'
        while result == 'cross' or result == 'dot':
            match = re.search(function_pattern, phrase)
            result = match.group()
            phrase = phrase[match.end():]
        return result
    except AttributeError:
        return ""

def get_index(phrase):
    """returns the index of the first letter of the first function of phrase"""
    i = 0
    match = re.search(function_pattern, phrase[i:])
    while i < len(phrase) and \
    (match.group() == 'cross' or match.group() == 'dot'):
        match = re.search(function_pattern, phrase[i:])
        if match.group() == 'cross' or match.group() == 'dot':
            i += match.end()
        else:
            break
    if match:
        return match.start() + i

def get_outdex(phrase):
    """returns the index of the last parenthesis that matches that of the first
    function in a phrase"""
    parens = 0
    paren_string = re.search(symbol_pattern+'\(', phrase)
    if paren_string:
        ti = paren_string.start() + 1
    else:
        return len(phrase)-int(phrase[len(phrase)-1]!=")")
    while ti < len(phrase):
        if phrase[ti] == "(":
            parens += 1
        elif phrase[ti] == ")":
            parens -= 1
        if parens == 0:
            break
        ti += 1
    return ti

def get_function_term(phrase):
    """returns the term between the parentheses of an elementary function"""
    paren_string = re.search(symbol_pattern+'\(', phrase)
    if paren_string:
        ti = paren_string.start() + 2
    else:
        return ""
    return phrase[ti:get_outdex(phrase)]

def get_parenthesis_outdex(phrase):
    """returns the index of the last parenthesis that matches the first one"""
    parens = 0
    paren_string = re.search('\(', phrase)
    if paren_string:
        ti = paren_string.start()
    else:
        return len(phrase)-int(phrase[len(phrase)-1]!=")")
    while ti < len(phrase):
        if phrase[ti] == "(":
            parens += 1
        elif phrase[ti] == ")":
            parens -= 1
        if parens == 0:
            break
        ti += 1
    return ti

def get_parenthesis_group(phrase):
    """returns the term between the first parenthesis and its pair"""
    paren_string = re.search('\(', phrase)
    if paren_string:
        ti = paren_string.start() + 1
    else:
        return ""
    return phrase[ti:get_parenthesis_outdex(phrase)]

def balanced(phrase):
    """returns true if the numbers of left and right parentheses are equal"""
    i, count = 0, 0
    for i in phrase:
        if i == '(':
            count += 1
        if i == ')':
            count -= 1
    if count == 0:
        return True
    return False

def get_terms(phrase):
    """returns a list of the added and subtracted terms within a phrase"""
    terms, parens = [], 0
    i = 0
    while i < len(phrase):
        #passes over terms in parentheses
        if phrase[i] == '(':
            parens = 1
            i += 1
            while parens > 0:
                if phrase[i] == '(':
                    parens += 1
                if phrase[i] == ')':
                    parens -= 1
                i += 1
            i -= 1
        elif phrase[i] == '<':
            parens = 1
            i += 1
            while parens > 0:
                if phrase[i] == '<':
                    parens += 1
                if phrase[i] == '>':
                    parens -= 1
                i += 1
            i -= 1
        elif phrase[i] == '+':
            terms.append(phrase[:i])
            phrase = phrase[i+1:]
            i = -1
        #captures negative signs attached to terms 
        elif phrase[i] == '-':
            #distinguishes a multiplying minus from one used to separate terms
            if i == 0 or i > 0 and (phrase[i-1] == '*' or phrase[i-1] == '/'):
               pass
            else:
                terms.append(phrase[:i])
                phrase = phrase[i:]
                i = 0
        i += 1
    terms.append(phrase)
    return terms

def get_coefficient(term):
    """returns the coefficient of a term whose coefficient is simplified"""
    #gets everything within a parenthesis
    if term[0] == '(':
        parens = 1
        i = 1
        while parens > 0:
            if term[i] == '(':
                parens += 1
            if term[i] == ')':
                parens -= 1
            i += 1
        if re.match('\*\*', term[i:]):
            return '1'
        if re.match('.', term[i:]):
            return term[:i]
        else:
            return '1'
    #e.g. 2*x*( or 2*x*<
    match = re.match('('+number_pattern+'(\*?'+symbol_pattern+'))\*(\(|\<)',\
    term)
    if match:
        return match.groups(0)[0]
    #e.g. *x*<
    match = re.match('((\*?'+symbol_pattern+'))\*(\(|\<)', term)
    if match:
        return match.groups(0)[0]
    #e.g. -x*(
    match = re.match('(\-'+symbol_pattern+')\*(\(|<)', term)
    if match:
        return match.groups(0)[0]
    #e.g. 2e-2
    match = re.match(number_pattern, term)
    if match:
        return match.groups(0)[0]
    match = re.match('\-', term)
    if match:
        return '-1'
    #e.g. sin; returns the whole function, i.e. sin(foo)
    match = re.match(function_pattern, term)
    if match:
        i = match.end()
        if term[i] == '(':
            parens = 1
            i += 1
            while parens > 0:
                if term[i] == '(':
                    parens += 1
                if term[i] == ')':
                    parens -= 1
                i += 1
            return term[:i]
    return '1'

def get_core(term):
    """returns the non-coefficient part of a simplified term
    because this is based on the get_coefficient method, changes only need
    to be made to get_coefficients to change what is returned as a core"""
    coefficient = get_coefficient(term)
    if coefficient == '-1':
        core = term[1:]
    elif coefficient == '1':
        core = term
    else:
        core = term[len(coefficient):]
    if len(core) > 0 and (core[0] == '*' or core[0] == '\\'):
        return core[1:]
    return core
    
def simplify(phrase):
    """simplifies all of the coefficients of a phrase"""
    terms = get_terms(str(phrase))
    result = ''
    for term in terms:
        result = result + str(simplify_coefficients(term)) + '+'
    result = make_friendly(result[:len(result)-1])
    return result
        
def simplify_coefficients(term):
    """reduces all of the coefficients of a term to a single leading one
    and returns the result of that times or divided by the simplified phrase.
    It's very likely that this could be better done recursively, but I 
    haven't had time to write such an agorithm"""
    #carats are easy to identify
    term = re.sub('\*\*', '^', term)
    coefficient, i, parens = 1, 0, 0
    #temporary string to be returned later
    temp = ""
    #tracks whether or not one of the miniature functions within this one has
    #happened to prevent overlapping use of rules
    traced = False
    if term == '':
        return '0'
    match = re.match(number_pattern+'[\*\/]', term)
    if match:
        coefficient *= float(match.groups(0)[0])
        term = term[len(match.groups(0)[0]):]
    while i < len(term):
        traced = False
        #skips items in parentheses and sets them as part of temp
        if term[i] == '(':
            parens = 1
            temp = temp + term[i]
            i += 1          
            while parens > 0:
                if term[i] == '(':
                    parens += 1
                if term[i] == ')':
                    parens -= 1
                i += 1
                temp = temp + term[i-1]
            term = term[i:]
            i = 0
            traced = True
        #skips over vectors
        elif term[i] == '<':
            parens = 1
            temp = temp + term[i]
            i += 1          
            while parens > 0:
                if term[i] == '<':
                    parens += 1
                if term[i] == '>':
                    parens -= 1
                i += 1
                temp = temp + term[i-1]
            term = term[i:]
            i = 0
            traced = True
        #matches a number times something arbitrary to its right
        match = re.match('\*'+number_pattern+'([^\d\^]|$)', term)
        if match and not traced:
            coefficient *= float(match.groups(0)[0])
            term = term[len(match.groups(0)[0])+1:]
            traced = True
        #matches divisors where a negative sign cannot be distributed
        match = re.match('\/'+number_pattern+'[^\^]?', term)
        if match and not traced:
            coefficient /= float(match.groups(0)[0])
            term = term[len(match.groups(0)[0])+1:]
            traced = True
        #adds unsimplified numbers and functions to temp
        elif not traced:
            temp = temp + term[0]
            term = term[1:]
    temp = re.sub(r'\*+', r'*', temp)
    if len(temp) > 0 and temp[0] == '*':
        temp = temp[1:]
    #reverts carats to the double asterisk
    temp = re.sub('\^', r'**', temp)
    if coefficient == 0:
        return '0'
    if temp == '' or temp == '1':
        return coefficient
    if temp[0] == '-' and str(coefficient)[0] == '-':
        return simplify_coefficients(str(coefficient)[1:] + '*' + temp[1:])
    elif temp[0] == '/':
        return(str(coefficient) + temp)
    elif coefficient == 1:
        return temp
    else:
        return(str(coefficient) + '*' + temp)
        
def simplify_degrees(term):
    #to be implemented
    pass

def get_degree(term):
    """Returns the degree of a term, whether or not the degree has been
    simplified already."""
    degrees = []
    temp = 0
    variables = get_variables(term)
    for i in variables:
        degrees.append(0)
        temp = 0
        #e.g. x**2
        match = re.findall('(?<!\/)'+i+'\*\*([^(].*?)(?:[*/+\-]|$)', term)
        for j in match:
            try:
                temp += float(j)
            except ValueError:
                return 'exponential'
        degrees[len(degrees)-1] = temp
        temp = 0
        #e.g. /x**2
        match = re.findall('\/'+i+'\*\*([^(].*?)(?:[*/+\-]|$)', term)
        for j in match:
            try:
                temp -= float(j)
            except ValueError:
                return 'exponential'
        degrees[len(degrees)-1] += temp
        temp = 0
        #e.g. x
        match = re.match('^'+i+'$', term)
        if match:
            degrees[len(degrees)-1] += 1
        #e.g. *x
        match = re.findall('\*'+i+'(?!\*\*)', term)
        for j in match:
            temp += 1
        degrees[len(degrees)-1] += temp
        temp = 0
        #e.g. x at the beginning of a phrase
        match = re.match('^'+i+'[*/](?!\*)', term)
        if match:
            degrees[len(degrees)-1] += 1
        temp = 0
        #e.g. a/x
        match = re.findall('.\/'+i, term)
        for j in match:
            temp -= 1
        degrees[len(degrees)-1] += temp
        j = 0
        #adds all of the evaluated exponents within parentheses
        temp = ''
        while j < len(term):
            if re.match(i+'\*\*\(', term[j:]):
                parens = 1
                j += 4
                temp = temp + term[j-1]
                while parens > 0:
                    if term[j] == '(':
                        parens += 1
                    if term[j] == ')':
                        parens -= 1
                    j += 1
                    temp = temp + term[j-1]
            else:
                j += 1
        try:
            if temp != '':
                degrees[len(degrees)-1] += float(eval(temp))
        except (ValueError, SyntaxError, NameError):
            return 'exponential'
        """
        #this should happen for things like sin(x)
        if degrees[len(degrees)-1] == 0:
            return 'unknown'
        """
    if degrees == []:
        return [0]
    return degrees

def factor(phrase):
    #to be implemented
    pass

def trim_spaces(phrase):
    """trims the spaces from a String phrase"""
    phrase = re.sub('\s', '', phrase)
    return phrase

def fact(x):
    """returns the factorial of a number"""
    n = 1
    for i in range(1, x + 1):
        n = n * i
    return n

def is_num(n):
    """determines whether or not a given string is a number or a component
    of a number; excludes things beginning or ending with spaces"""
    if re.match('\A[0-9|.]+\Z', n) != None:
        return True
    return False

def is_operator(n, ops = operators):
    """compares a character to a list of operators for equivalence;
    operator list is by default that at the top of this program"""
    for i in ops:
        if n == i:
            return True
    return False

def is_letter(n):
    """determines if an input character is a letter, given a list of operators
    to be compared to."""
    if re.match(symbol_pattern, n) != None:
        return True
    return False

def is_word(n):
    """returns true if a phrase is a single word or function as specified by the
    items in the symbol pattern specified above."""
    if re.match('\A'+symbol_pattern+'+', n) != None:
        return True
    return False

def unshell(phrase):
    """if a phrase ends with a parenthesis, return the portion of the phrase
    between the first open parenthesis and the ending parenthesis"""
    if phrase[len(phrase) - 1] == ")":
        return phrase[phrase.index("(")+1:len(phrase)-1]
    return phrase

def get_real(phrase):
    """gets the real part of a complex number"""
    try:
        match = re.search(number_pattern + '[+\-]', phrase)
        return phrase[1:match.end()-1]
    except ValueError:
        return phrase

def get_imaginary(phrase):
    """gets the imaginary part of a complex number"""
    try:
        match1 = re.search(number_pattern + '.', phrase)
        if match1:
            term = phrase[match1.end():len(phrase)-1]
            match2 = re.search('j.', term)
            if match2:
                return phrase[match1.end()-1] + term[match2.end():] + 'j'
            else:
                return term
    except AttributeError:
        return "0"

def make_complex(phrase):
    """turns real numbers into complex numbers"""
    try:
        return complex('('+ get_real(phrase) + get_imaginary(phrase) + ')')
    except ValueError:
        return phrase

def test(funct):
    print(funct('-1*2*3*4'))
    print(funct('1/2*-2/4'))
    print(funct('2*3*3/4'))
    print(funct('2**3/20*4/4'))
    print(funct('2*x*3/5**4'))
    print(funct('2*s**(8*2-5)'))
    print(funct('4*3/-sin(2*x+3/3)/4'))
    print(funct('2/s^(sin(3))/3'))